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
    password = "8911F26173C9"
    print("proxy_ip:", proxy_ip)
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
            jiucai_url = 'https://www.jiuyangongshe.com/search/new?k={}股票异动解析'.format(name)
            print("jiucai_url:", jiucai_url)
            response = requests.get(jiucai_url, headers=headers, proxies=proxies, timeout=3)
            # print("response.text:", response.text)
            if response.status_code == 200 and response.text.count("股票异动解析") > 0:
                text = response.text

            # print("text:", text)
            time.sleep(0.2)
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

                info = str(info).replace("<div class=\"pre-line\" data-v-314da332=\"\">", "")
                info = info.replace("<div class=\"pre-line\" data-v-69d79c05=\"\">", "")
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


def get_print_jiucai_url(name):
    print("------------------------------")
    jiucai_url = "https://www.jiuyangongshe.com/search/new?k=name&type=5".replace("name", name)
    print("jiucai_url:", jiucai_url)


def get_article_info_v2(name_id):
    proxies = get_proxies()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    print("proxies:", proxies)
    for _ in range(10):
        try:
            href_full_url = "https://www.jiuyangongshe.com/a/{}".format(name_id)
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

            info = str(info).replace("<div class=\"pre-line\" data-v-007e0ec9=\"\">", "")
            info = info.replace("<div class=\"pre-line\" data-v-69d79c05=\"\">", "")
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

    # 题材
    add_page_break = False
    add_he_xin_split = True
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

        # 添加段落
        doc.add_paragraph(title + "\n" + info + "\n\n" + ti_cai_text + "\n")

    # 核心
    he_xin = """
    核心：
        *、先求势，再求利，先找方向，再考虑这个方向能不能起
            *、你拿的标的是不是在当下最强的方向里，是就格局，不是就不格局
            *、你关注的标的是不是在当下最强方向里，是就可以看，不是不要考虑
            *、板块主升，托举龙头主升，这才是是正解
        *、买卖：
            *、买点：流动性在增强的东西
            *、卖点：流动性在减弱的东西
        *、总体方向有这几个
            1、新东西很强
            2、当下题材很强
            3、当下题材见顶，低位很强
            4、市场疲软，老核心很强
            5、市场普涨，抱团倒下
            6、中位高位弱了，市场即将进入退潮
        *、人气 = 社会讨论度 + 资金活跃度
            *、二波前面的连板，是为了看他的人气，二波就是人气的再次聚集
            *、知道的人，讨论的人，关注的人，参与交易的人越多，物品越好交易，也就是物品越好流动
            *、流动性越充足，越容易产生狂热交易，越容易产生流动性溢价，激水漂石
            *、市场上最好的东西享受流动性溢价，龙头就是人气资金流动性最强的地方
            *、社会讨论度决定板块地位，资金活跃度决定龙头地位，板块讨论度带来的资金流动性会把龙头托举起来
        *、买点的核心逻辑
            *、去寻找人气资金流动性强到一定程度，且属于当下市场最强，且还在加强向上的方向
        *、大数定律
            *、赚多出的钱它也会亏回去，亏多出的钱它也会再赚回来，均值是会回归的
            *、去掉概率低的，保留概率高的，提升每一次出手的概率，当操作足够多的时候，盈利就会回归到均值上
            *、高概率事件条件：
                *、大杀的极致冰点之后的情绪向上
                *、处于最强板块中，有板块流动性支撑
                *、社会讨论度最高，资金活跃度最强
                *、市场休息够了，题材休息够了，龙头休息够了
            *、把过程当做目标，眼里只有结果就会笨拙
                *、徒弟：师父，以我的资质，开悟需要多久？师父：十年
                *、徒弟：如果我加倍苦修呢？师父：二十年
                *、徒弟：如果我夜以继日，不休不眠呢？师父：那你将永无开悟之日
        *、越努力越菜
            *、无间地狱
            *、急于求成，气急攻心
            *、我可以输一万次，但最后让我赢就行，我很弱小，需要借助至刚至强者的力量
            *、一期目标：减掉一些东西，降低复杂度，不然太疲劳了，目前只想轻松一点
    """
    doc.add_page_break()
    doc.add_paragraph(he_xin)

    doc.save('result/复盘.docx')

    save_tj(doc)
    save_js(doc)
    save_gz(doc)


def save_tj(doc):
    delete_paragraph(doc)
    # 条件
    condition = ""
    for line in open("总结/条件.txt").readlines():
        condition = condition + line

    doc.add_paragraph(condition)
    doc.save('result/条件.docx')


def save_js(doc):
    delete_paragraph(doc)
    # 龙头断板计数
    condition = ""
    for line in open("总结/龙头断板计数.txt").readlines():
        condition = condition + line

    doc.add_paragraph(condition)
    doc.save('result/龙头断板计数.docx')


def save_gz(doc):
    delete_paragraph(doc)
    # 共振
    condition = ""
    for line in open("总结/共振.txt").readlines():
        if line.strip().startswith("回归常识"):
            doc.add_paragraph(condition)
            doc.add_page_break()
            condition = ""
        condition = condition + line

    doc.add_paragraph(condition)
    doc.save('result/共振.docx')


def delete_paragraph(doc):
    for paragraph in list(doc.paragraphs):
        p = paragraph._element
        p.getparent().remove(p)
        p._p = p._element = None


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
        # get_print_jiucai_url(name)
        # name_id = input("股票名字id：")
        # print("name_id:", name_id)
        # article_info = get_article_info_v2(name_id)
        article_info = get_article_info(name)
        if article_info:
            info_map[name] = article_info

    print("info_map:", info_map)
    # 保存到word
    save_word_text(he_xin, name_list, info_map, "A4")
