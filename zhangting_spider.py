# encoding: utf-8
import akshare as ak
import json
import logging
import re
import requests
import time
from datetime import datetime
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm
from docx.shared import Pt, RGBColor
from pyquery import PyQuery as pq

code_map = {}
zhang_ting_di_wei_tag = {}


def get_proxies():
    proxy_ip = get_proxy_ip()
    if proxy_ip == "":
        proxy_ip = get_proxy_ip()

    # 官网：https://www.qg.net/doc/1697.html
    authKey = "03WMRTUF"
    password = "9D76ED4CAB2E"
    proxyUrl = "http://{}:{}@{}".format(authKey, password, proxy_ip)
    return {
        "http": proxyUrl,
        "https": proxyUrl
    }


def get_article_info(name):
    print("------------------------------")
    name = name.replace("Ａ", "A")
    proxies = get_proxies()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    print("proxies:", proxies)
    text = ""
    for _ in range(10):
        try:
            jiucai_url = 'https://www.jiuyangongshe.com/search/new?k={}&type=5'.format(name)
            print("jiucai_url:", jiucai_url)
            response = requests.get(jiucai_url, headers=headers, proxies=proxies, timeout=3)
            if response.status_code == 200 and response.text.count("股票异动解析") > 0:
                text = response.text
            time.sleep(0.5)
            # print("text:", text)
        except Exception as e:
            proxies = get_proxies()
            logging.error(e)
        if text:
            break

    href_pattern = re.compile(r'href="(/a/.*?)"')
    href_matches = href_pattern.findall(text)

    if len(href_matches) <= 0:
        return None

    # 输出匹配到的href
    for href in href_matches:
        for _ in range(10):
            try:
                href_full_url = "https://www.jiuyangongshe.com{}".format(href)
                print("href_full_url:", href_full_url)
                response = requests.get(href_full_url, headers=headers, proxies=proxies, timeout=3)
                text = ""
                if response.status_code == 200:
                    text = response.text

                doc = pq(text)
                title = doc(".fs28-bold")
                title = title.text()
                print("title:", title)
                print("name:", name)
                print("find:", title.find(name))
                if title.find(name) <= 0:
                    break

                ti_cai_text = doc(".mt40  > div.text-justify")
                ti_cai_text = ti_cai_text.text()
                print("ti_cai_text:", ti_cai_text)

                info = doc(".pre-line")
                date = get_today()
                try:
                    date = doc(".date").text().split(" ")[0]
                except Exception as e:
                    logging.exception(e)

                info = str(info).replace("<div class=\"pre-line\" data-v-1fbcd229=\"\">", "")
                info = info.replace("<div class=\"pre-line\" data-v-2d5a9c93c=\"\">", "")
                info = info.replace("<div class=\"pre-line\" data-v-2d5a9c93=\"\">", "")
                info = info.replace("<div class=\"pre-line\" data-v-e8c25eb2=\"\">", "")
                info = info.replace("</div>", "")
                code_info = code_map.get(name, None)
                tag = zhang_ting_di_wei_tag.get(name, "")
                if code_info:
                    change = code_info.get("涨跌幅", None)
                    code = code_info.get("代码", None)
                    print("change:", change)
                    print("code:", code)
                    if code and change and info:
                        info_arr = info.split("\n", 1)
                        info_0 = info_arr[0] + "  " + str(change) + "%" + "  " + tag + "  " + str(code)
                        info = info_0 + "\n" + info_arr[1]
                print("info:", info)
                return {"info": info, "date": date, "title": title, "ti_cai_text": ti_cai_text}
            except Exception as e:
                proxies = get_proxies()
                logging.exception(e)


def get_today():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


def save_word_text(he_xin, name_list, info_map, print_type="A5"):
    # 创建文档
    doc = Document()
    doc.styles['Normal'].font.name = 'Times New Roman'
    doc.styles['Normal'].element.rPr.rFonts.set(qn('w:eastAsia'), u'宋体')
    doc.styles['Normal'].font.size = Pt(10)
    doc.styles['Normal'].font.color.rgb = RGBColor(0, 0, 0)

    # 设置页面大小为A5
    section = doc.sections[0]
    if print_type == "A5":
        section.page_width = Cm(14.8)
        section.page_height = Cm(21)
    else:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)

    section.left_margin = Cm(1.27)
    section.right_margin = Cm(1.27)
    section.top_margin = Cm(1.27)
    section.bottom_margin = Cm(1.27)

    h1 = doc.add_heading("时间节点", level=2)
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    time_point = "1、涨潮：买盘一鼓作气， 再而衰， 三而竭， 阶段性顶\n" \
                 "2、退潮：卖盘一鼓作气， 再而衰， 三而竭， 阶段性底"

    doc.add_paragraph(time_point)
    doc.add_paragraph("- " * 90)

    # 题材

    add_page_break = False
    add_he_xin_split = True
    first_page = True
    for key in name_list:
        val = info_map.get(key, None)
        if not val or val is None:
            continue

        if print_type == "A5":
            # 分页符
            if not add_page_break:
                add_page_break = True
            else:
                doc.add_page_break()

        print("key:", key)
        print("val:", val)
        info = val.get("info")
        title = val.get("title")
        ti_cai_text = val.get("ti_cai_text")

        if key not in he_xin and add_he_xin_split:
            add_he_xin_split = False
            doc.add_paragraph("- " * 90)

        # 添加标题，0表示样式为title
        h1 = doc.add_heading(key, level=2)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER

        yu_lu_list = [
            "向内求者，人性为善，向外求者，人性为恶，人性之上，规律之下",
            "看盘：先大后小，自上而下，在哪里打仗，能不能赢，明天有没有更多的人来接盘",
            "亏钱永远比赚钱容易，躲过下雨天已经成功了一半，市场整体比昨天弱时，欣赏别人的股票涨停就好了",
            "当局势有优势，辅助都很强，大哥就可以在团战中三杀，四杀，暴走，反之酱油秒躺，大哥也站不住",
            "化繁为简：找出主要矛盾，忽略所有次要矛盾，小行情，行情差，错过买点时的大胆，是你亏钱的根源",
            "全是重点就是没有重点，其实不需要智慧，只需要做好选择，时间节点，题材方向，龙头个股都是如此，不会就用排除法",
            "行情不好的时候，不要出手，行情好的时候，猛干核心，不是越努力越幸运，要懂得适当的休息，不要逆势",

            "二波本质是让你看清楚个股的地位，辨识度，人气，群众基础，看清楚后不等于要买，决定你要不要买，"
            "个股，图形是次要矛盾，时间节点，大盘环境，题材人气，小弟强度才是主要矛盾，你真牛逼，"
            "到高位之后还有人气，我再看你",

            "慢下来，坚持无减肥，不要犯错，要冷静，看不见猛就往上冲，本质就是贪，大部分的预判都是错的，都是胡思乱想",

            "牛市和熊市的区别：牛市的机会多一些，仅此而已，跟每一个小周期一样，牛市大周期结束都是那90%的人买单",
            "打仗没有什么神秘，打得赢就打，打不赢就走，抓住你的弱点，跟着你打，你打你的，我打我的",

            "战略上藐视敌人：以一当十，要取得胜利，要从全局考虑，找出关键点在哪里，明确该做什么，不该做什么，永远都会有机会，不以人的意志为转移",
            "战术上重视敌人：以十当一，在运动中创造压倒性优势机会，过程是艰难曲折的，当战略战术确定之后，剩下比的就是谁更了解局势了",

            "市场不认可的东西都是垃圾，如果从个股看不出确定性，多看看板块，确定性就有了",
            "市场没有量，其实就是玩的人少了，为什么你不挣钱：因为好的机会很少，你却出手很多",

            "任何一场博弈，都是以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，要有绝对的，压倒性的优势，"
            "如果没有这个条件只能等，在绝对实力面前，一切技术都是花里胡哨",

            "成交量放大，要么是主动买盘变多了，要么是主动卖盘变多了，放量理论上就是强，放量攻不上去就是弱",
            "把很复杂的东西，简化成你能操作的东西，考虑的东西越少越好，现在最强的东西是什么，用眼睛看就可以了，不用去想",
            "是不是高潮，就需要想一下有没有下一波更高亢的情绪出来，如果没有，当前就是高潮，反之低潮也一样",

            "开始分歧了，后排都要卖，因为龙头分歧给机会，去弱留强，虹吸效应会把后排跟风吸死，当龙头也断板了，不涨了，"
            "最漂亮的那个也没人追了，说明买盘力量已经枯竭了，就像楼市，北京房价都跳水了，其他城市肯定好不到哪去",

            "一波高潮后，个股中会有很多获利、埋伏、套牢盘，筹码很复杂，筹码已经坏掉了，"
            "小弟没力气了，板块没力气了，大哥也走得不流畅了，这个时候的筹码结构已经变复杂了",

            "龙头就是人气，人人可参与，是群众基础，是能团结一切能团结的力量",
            "华映科技牛逼吗？在我眼里就是个垃圾，他涨一万个板也是垃圾，常山，海能达，四川这些才是大道，龙头说白了就是学会比较",
            "夫战，勇气也。一鼓作气，再而衰，三而竭，彼竭我盈，故克之，夫大国，难测也，惧有伏焉，吾视其辙乱，望其旗靡，故逐之",
            "这几年一路走来的艰难困苦，有什么值得歌颂的呢，本质上不是一个有天赋的人，打游戏如此，打球如此，智商也如此"
        ]
        zhu = ""
        if first_page:
            for i, yu_lu in enumerate(yu_lu_list):
                zhu = zhu + "{}、{}\n".format(i + 10, yu_lu)
        # 添加段落
        doc.add_paragraph(title + "\n" + info + "\n\n" + ti_cai_text + "\n\n" + zhu)
        first_page = False

    # 保存文档
    doc.add_paragraph("Q: 我如果是神，明天我拉哪个板块，哪个个股，能得到市场认同，形成合力，能盘活整个市场")
    bj = """ 
    主要矛盾：三大范围：时间节点、题材方向、核心个股
    一、时间节点：
        1、涨潮：一鼓作气，再而衰，三而竭
        2、退潮：一鼓作气，再而衰，三而竭
        3、规律：随着时间的变化，买卖强弱关系是会相互转化的，即阴阳循环，祸兮福所倚，福兮祸所伏
        
    二、题材板块：
        1、题材大小
        2、所处阶段
        3、资金进攻力度
        
    三、龙头：
        1、股性：量价关系
        2、人气：群众基础
        3、资金：进攻力度
        
    四、代码简写：
        if "时间节点" == "卖盘强势":
            "全部放弃"
        else:
            if "方向" == "主线题材" and "个股" == "核心龙头":
                "可以考虑"
            else:
                "全部放弃"
    
    五、要有目的性的去比较，刻意地练习
    """
    doc.add_paragraph(bj)
    doc.save('result/复盘.docx')


def get_timestamp(date):
    from dateutil import parser
    return int(parser.parse(date).timestamp())


def get_zhang_ting_list(file):
    name_list = []
    for line in open(file):
        if line.strip():
            data = line.strip().split(",")
            name_list.append(data[0])
            if len(data) == 2 and data[1]:
                zhang_ting_di_wei_tag[data[0]] = data[1]
    return name_list


def get_zhang_ting_map(ti_cai_list):
    zhang_ting_map = {}
    for val in ti_cai_list:
        zhang_ting_map[val] = get_zhang_ting_list("./input/{}.txt".format(val))

    return zhang_ting_map


def get_code_map():
    # 获取东方财富网-沪深京 A 股-实时行情
    df = ak.stock_zh_a_spot_em()
    for index, row in df.iterrows():
        code_map[row["名称"].strip()] = {"代码": row["代码"].strip(), "涨跌幅": row["涨跌幅"]}


def get_proxy_ip():
    try:
        # 青果网络的API地址和参数：https://www.qg.net/tools/IPdebug.html
        api_url = "https://share.proxy.qg.net/get?key=03WMRTUF&num=1&distinct=true"

        response = requests.get(api_url)
        data = json.loads(response.text)
        data = data.get("data", [])

        server_list = [val.get("server") for val in data]
        if server_list and len(server_list) > 0:
            return server_list[0]
    except Exception as e:
        logging.exception(e)
    return ""


def get_name_list(file, filter_list):
    name_list = []
    for line in open(file):
        line = line.strip()
        data = line.strip().split(",")
        name = data[0].strip()

        if len(data) == 2 and name:
            tag = data[1].strip()
            zhang_ting_di_wei_tag[name] = tag

        if name and name not in filter_list:
            name_list.append(name)

    return name_list


def get_replay_name_list():
    he_xin = get_name_list("input/复盘核心.txt", [])
    zhang_ting = get_name_list("./input/涨停.txt", he_xin)
    print("he_xin:", he_xin)
    print("zhang_ting:", zhang_ting)

    return he_xin, he_xin + zhang_ting


if __name__ == '__main__':

    # 获取个股代码
    get_code_map()

    # 获取题材涨停的个股
    he_xin, name_list = get_replay_name_list()
    print("name_list:", name_list)

    # 爬取涨停数据
    info_map = {}
    for name in name_list:
        article_info = get_article_info(name)
        if article_info:
            info_map[name] = article_info

    print("info_map:", info_map)
    if len(info_map) > 0:
        # 保存到word
        save_word_text(he_xin, name_list, info_map, "A4")
