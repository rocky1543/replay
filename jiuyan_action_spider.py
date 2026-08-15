"""
韭研公社「异动解析」爬虫（已验证可用）
=====================================
原理：
  1. 数据接口为 POST https://web-api.jiuyangongshe.com/jystock-app/api/v1/action/field
     payload: {"date": "YYYY-MM-DD", "pc": 1}
     一次请求即返回全部板块（name=板块名称, reason=题材炒作原因）及板块内
     股票列表（list[].name / code / article.action_info.expound=涨停解析）。
  2. 该接口有登录校验 + 动态 token 反爬（token 由页面 JS 按时间戳签名生成），
     直接用 requests 调不通，因此用 Playwright 打开页面让页面自己发请求，
     从网络层捕获响应。

登录方式（三选一，推荐方式 A）：
  A. 一次性登录 + 本地保存登录态（最省事，无需手动复制 Cookie）：
     1) python jiuyan_action_spider.py --login
        会弹出浏览器窗口，手动登录一次（扫码/账号密码均可），
        登录成功后脚本自动把 Cookie 保存到 jiuyan_state.json 并抓取数据。
     2) 之后每次运行无需任何参数：
        python jiuyan_action_spider.py
        自动读取 jiuyan_state.json 里的登录态，全程无头、全自动。
     3) Cookie 过期（一般 1~2 天）后再运行一次 --login 重新登录即可。

  B. 手动传 Cookie：python jiuyan_action_spider.py --session "..." --sl-session "..."

  C. 已有 state 文件时指定路径：python jiuyan_action_spider.py --state path/to/jiuyan_state.json

输出：
  result/jiuyan_action_<日期>.csv（Excel 友好）+ 同名 _raw.json（原始数据）

注意：
  - --date 参数仅用于命名输出文件，页面实际返回的是最新交易日数据
    （如需抓历史日期，需在页面上手动切换日期，本脚本暂未实现）。

依赖：pip install playwright && playwright install chromium
（本机虚拟环境：/Users/xiaoguaiguai/.workbuddy/binaries/python/envs/jiuyan/）
"""
import argparse, csv, json, os, socket, subprocess, sys, time, urllib.request
from playwright.sync_api import sync_playwright

URL = 'https://www.jiuyangongshe.com/action'
STATE_FILE = '/Users/xiaoguaiguai/Downloads/tmp/jiuyan_state.json'

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


def _make_context(browser, storage_state=None):
    return browser.new_context(
        user_agent=UA,
        viewport={'width': 1280, 'height': 1200},
        storage_state=storage_state,
    )


def _cookie_dicts(session_cookie, sl_session_cookie):
    return [
        {'name': 'SESSION', 'value': session_cookie,
         'domain': 'web-api.jiuyangongshe.com', 'path': '/jystock-app'},
        {'name': 'SESSION', 'value': session_cookie,
         'domain': 'www.jiuyangongshe.com', 'path': '/'},
        {'name': 'sl-session', 'value': sl_session_cookie,
         'domain': 'www.jiuyangongshe.com', 'path': '/'},
    ]


def _capture_field(context, wait_login=False):
    """打开 /action 页面并捕获 action/field 响应，返回 errCode==0 的响应文本

    wait_login=False: 无头模式，最多等 30 秒（登录态失效时返回 ''）
    wait_login=True:  等待用户在浏览器里手动登录，最长 5 分钟。
                      注意：页面未登录时也会发一次 field 请求（返回"登录失效"），
                      不能见到响应就停，必须等到登录成功后的 errCode==0 响应。
    """
    page = context.new_page()
    captured = []

    def handle_response(response):
        if '/api/v1/action/field' in response.url:
            captured.append(response)

    page.on('response', handle_response)
    page.goto(URL, wait_until='networkidle', timeout=60000)

    def click_tab():
        try:
            if not wait_login:
                # 登录模式下不能删弹窗，否则登录框会被误删
                page.evaluate('''() => {
                    document.querySelectorAll('.el-dialog__wrapper, .v-modal, .jc-login')
                        .forEach(d => d.remove());
                }''')
            page.evaluate('''() => {
                const tabs = document.querySelectorAll('.yd-tabs_item');
                for (let t of tabs) {
                    if (t.innerText.includes('全部异动解析')) { t.click(); return; }
                }
            }''')
        except Exception:
            pass

    def extract_ok():
        """从已捕获的响应里找 errCode==0 且有数据的那条（最新优先）"""
        for resp in reversed(captured):
            try:
                text = resp.text()
                d = json.loads(text)
                if str(d.get('errCode')) == '0' and d.get('data'):
                    return text
            except Exception:
                continue
        return ''

    deadline = time.time() + (300 if wait_login else 30)
    last_notice = 0.0
    while time.time() < deadline:
        click_tab()          # 反复点标签，登录后触发新的 field 请求
        page.wait_for_timeout(2000)
        raw = extract_ok()
        if raw:
            return raw
        if wait_login and time.time() - last_notice > 30:
            print('>> 尚未检测到登录成功，继续等待...（请在浏览器窗口完成登录）')
            last_notice = time.time()

    return ''


def _launch_detached_browser(p):
    """独立启动一个 Chromium 进程（不归 Playwright 托管），脚本退出后窗口保留。
    返回通过 CDP 连接的 browser 对象。"""
    exe = p.chromium.executable_path
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()

    user_data = os.path.abspath('.jiuyan_browser_profile')
    proc = subprocess.Popen(
        [exe, f'--remote-debugging-port={port}',
         f'--user-data-dir={user_data}',
         '--no-first-run', '--no-default-browser-check', URL],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(60):  # 等待 CDP 端口就绪，最长 30 秒
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/json/version', timeout=1)
            browser = p.chromium.connect_over_cdp(f'http://127.0.0.1:{port}')
            return browser, proc
        except Exception:
            time.sleep(0.5)
    proc.terminate()
    raise RuntimeError('独立浏览器启动超时')


def login_and_save(state_path=STATE_FILE, output=''):
    """弹出浏览器让用户手动登录一次，成功后保存登录态到 state 文件，并返回抓到的数据。
    数据保存完成后脚本即退出；浏览器以 detached 模式启动，窗口保留给用户继续浏览，
    不随脚本结束而关闭。"""
    print('>> 即将打开浏览器窗口，请在页面中登录韭研公社（扫码或账号密码）。')
    print('>> 登录成功后脚本会自动检测并保存登录态，最长等待 5 分钟...')
    with sync_playwright() as p:
        browser, proc = _launch_detached_browser(p)  # 独立进程，脚本退出后窗口不关闭
        context = browser.contexts[0]
        raw = _capture_field(context, wait_login=True)

        if not raw:
            browser.close()
            proc.terminate()
            raise RuntimeError('等待超时：5 分钟内未检测到登录成功，请重试 --login')

        data = json.loads(raw)

        # 先把数据落盘，浏览器后面还要留给用户浏览
        if output:
            print('>> 检测到登录成功，先保存数据...')
            save_outputs(data, output)

        context.storage_state(path=state_path)
        print(f'>> 登录态已保存到 {state_path}，之后直接运行无需 --login')
        print('>> 数据已保存完毕，脚本即将退出。浏览器窗口保留，可继续浏览，看完手动关闭即可。')
        # 注意：不调用 browser.close()（CDP 连接断开即可），独立浏览器窗口留给用户
        return data


def fetch_field_data(state_path=None, session_cookie=None, sl_session_cookie=''):
    """无头模式抓取：优先用 state 文件登录态，其次用手动传入的 Cookie"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        if state_path:
            if not os.path.exists(state_path):
                raise SystemExit(f'登录态文件不存在: {state_path}，请先运行 --login 登录一次')
            context = _make_context(browser, storage_state=state_path)
        else:
            context = _make_context(browser)
            context.add_cookies(_cookie_dicts(session_cookie, sl_session_cookie))

        raw = _capture_field(context, wait_login=False)
        browser.close()

    if not raw:
        raise RuntimeError(
            '未捕获到有效数据。可能原因：\n'
            '  1) 登录态/Cookie 已过期（一般 1~2 天失效），请重新运行 --login；\n'
            '  2) 页面加载过慢，可重试一次。'
        )
    return json.loads(raw)


def to_rows(data):
    rows = []
    for field in data.get('data') or []:
        if field.get('name') == '简图':
            continue
        for s in field.get('list') or []:
            info = ((s.get('article') or {}).get('action_info') or {})
            rows.append({
                '日期': field.get('date', ''),
                '板块名称': field.get('name', ''),
                '题材炒作原因': field.get('reason') or '',
                '股票名称': s.get('name', ''),
                '股票代码': s.get('code', ''),
                '涨停时间': info.get('time', ''),
                '连板数': info.get('num', ''),
                '涨停解析': info.get('expound') or '',
            })
    return rows


def save_outputs(data, output):
    raw_path = output.rsplit('.', 1)[0] + '_raw.json'
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f'原始数据已保存到 {raw_path}')

    rows = to_rows(data)
    print(f'共获取 {len(rows)} 条股票记录')

    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                                ['日期', '板块名称', '题材炒作原因', '股票名称', '股票代码', '涨停时间', '连板数', '涨停解析'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'已保存到 {output}')


def main():
    parser = argparse.ArgumentParser(
        description='韭研公社异动解析爬虫。推荐：先 --login 登录一次，之后直接运行。')
    parser.add_argument('--login', action='store_true',
                        help='弹出浏览器手动登录一次，保存登录态到 jiuyan_state.json')
    parser.add_argument('--state', default='', help=f'登录态文件路径（默认 {STATE_FILE}）')
    parser.add_argument('--session', default='', help='手动传入 SESSION cookie 值（不用 state 文件时）')
    parser.add_argument('--sl-session', default='', help='手动传入 sl-session cookie 值')
    parser.add_argument('--date', default='', help='日期 YYYY-MM-DD，留空=今天（仅用于命名输出文件）')
    parser.add_argument('--output', default='', help='输出 CSV 路径，留空=result/jiuyan_action_<日期>.csv')
    args = parser.parse_args()

    date = args.date or time.strftime('%Y-%m-%d')
    output = args.output or f'result/jiuyan_action_{date}.csv'

    if args.login:
        login_and_save(args.state or STATE_FILE, output)
        return  # 数据已在 login_and_save 内提前保存（浏览器关闭前）
    elif args.session:
        data = fetch_field_data(session_cookie=args.session,
                                sl_session_cookie=args.sl_session)
    else:
        data = fetch_field_data(state_path=args.state or STATE_FILE)

    if str(data.get('errCode')) != '0':
        raise SystemExit(
            f"接口返回错误: {data.get('msg')} (errCode={data.get('errCode')})。\n"
            f"登录态可能已过期，请重新运行: python {sys.argv[0]} --login")

    save_outputs(data, output)


if __name__ == '__main__':
    main()
