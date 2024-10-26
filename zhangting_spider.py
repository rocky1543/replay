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
emotional_cycle_action = {
    1: {
        "cycle": "龙头主升一致期",
        "action": "做龙头属性补涨",
        "profit_space": "新龙当前高度和老龙的高度差"
    },
    2: {
        "cycle": "龙头pk或市场分歧期",
        "action": "做龙头or做龙头属性补涨",
        "profit_space": "新龙当前高度和老龙的高度差"
    },
    3: {
        "cycle": "龙头断板退潮期",
        "action": "逃离高位，做龙头属性补涨or新题材低位补涨龙",
        "profit_space": "2、3板和老龙的高度差"
    },
    4: {
        "cycle": "龙头无高度混沌期",
        "action": "老龙头无高度，高度被压制，没有赚钱效应，最好空仓"
    },
}


def get_proxies(proxy_ip):
    # 官网：https://www.qg.net/doc/1697.html
    authKey = "03WMRTUF"
    password = "9D76ED4CAB2E"
    proxyUrl = "http://{}:{}@{}".format(authKey, password, proxy_ip)
    return {
        "http": proxyUrl,
        "https": proxyUrl
    }


def get_article_info(name, proxy_ip):
    print("------------------------------")
    name = name.replace("Ａ", "A")
    proxies = get_proxies(proxy_ip)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }
    print("proxies:", proxies)
    text = ""
    for _ in range(20):
        try:
            jiucai_url = 'https://www.jiuyangongshe.com/search/new?k={}&type=5'.format(name)
            print("jiucai_url:", jiucai_url)
            response = requests.get(jiucai_url, headers=headers, proxies=proxies)
            if response.status_code == 200 and response.text.count("股票异动解析") > 0:
                text = response.text
            time.sleep(0.5)
            # print("text:", text)
        except Exception as e:
            logging.error(e)
        if text:
            break

    href_pattern = re.compile(r'href="(/a/.*?)"')
    href_matches = href_pattern.findall(text)

    if len(href_matches) <= 0:
        return None

    # 输出匹配到的href
    for href in href_matches:
        for _ in range(2):
            try:
                href_full_url = "https://www.jiuyangongshe.com{}".format(href)
                print("href_full_url:", href_full_url)
                response = requests.get(href_full_url, headers=headers, proxies=proxies)
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

                info = str(info).replace("<div class=\"pre-line\" data-v-855c39ec=\"\">", "")
                info = str(info).replace("<div class=\"pre-line\" data-v-421de0aa=\"\">", "")
                info = str(info).replace("<div class=\"pre-line\" data-v-0aa83f20=\"\">", "")
                info = str(info).replace("<div class=\"pre-line\" data-v-28f26548=\"\">", "")
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
                logging.exception(e)


def get_today():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")


def save_word_text(ti_cai, info_map, direction_list, cycle_and_action, print_type="A5"):
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

    add_page_break = False
    first_page = True
    for key, val in info_map.items():
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

        # 添加标题，0表示样式为title
        h1 = doc.add_heading(key, level=2)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # zhu1 = "节点: {}， 老龙高度: {}板".format(cycle_and_action.get("cycle"), lao_long_gao_du)
        # zhu2 = "空间: {}".format(cycle_and_action.get("profit_space"))
        # zhu3 = "计划: {}".format(cycle_and_action.get("action"))
        yu_lu_list = [
            "张良：给你的，你不能全要，不给你的，你不能要",
            "处事：人性之上，规律之下，看盘：先大后小，自上而下，方向在哪里，谁是核心",
            "小行情，行情差，错过买点时的大胆，是你在大行情唯唯诺诺的根源",
            "看到的强才是真的强，看不到强只能等，大部分的预判都是错的，都是胡思乱想",

            "慢下来，坚持无减肥，不要犯错，要冷静",
            "龙头总是万众瞩目，吸引大量的资金, 一波大行情来，你要做的第一件事就是预判谁是大龙头",

            "牛市和熊市的区别：牛市的机会多一些，仅此而已，跟每一个小周期一样，牛市大周期结束都是那90%的人买单",
            "打仗没有什么神秘，打得赢就打，打不赢就走，抓住你的弱点，跟着你打，你打你的，我打我的，我们的部队，"
            "走也走得，打也打得",
            "战略上藐视敌人：胜利来源于压倒性优势，万物皆周期，永远会有机会，不以人的意志为转移",
            "战术上重视敌人：过程是艰难曲折的，要慎重，耐心等待机会，当战略战术确定之后，剩下比的就是知己知彼，"
            "谁更了解局势了",

            "市场不认可的东西都是垃圾，杂毛垃圾会让你操作变形，跟酱油换命不值得",
            "市场没有量，其实就是玩的人少了，为什么你不挣钱：因为好的机会很少，你却出手很多",
            "如果从个股看不出确定性，多看看板块，确定性就有了",

            "任何一场博弈，完胜的条件是士气要高涨，要以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，"
            "要有绝对的，压倒性的优势，如果没有这个条件只能等，在绝对实力面前，一切技术都是花里胡哨",

            "二波：题材大小，决定龙头高度，题材能持续，龙头就能持续",
            "二波：一波行情走完之后，人气会在哪个板块，哪支个股重新聚集，形成新的强大力量，压倒性的向上推动",
            "二波：在市场不是很差的时候，板块很强，板块就可以拧着龙头强劲的往上走",

            "二波：当局势有优势，辅助都很强，大哥就可以在团战中三杀，四杀，暴走，反之酱油秒躺，大哥也站不住",

            "二波：如果题材人气还很强，题材就有再次起来的预期，如果这个逻辑市场不认了，这个二波图形就是个垃圾",
            "成交量放大，要么是主动买盘变多了，要么是主动卖盘变多了，你想知道是哪个变多了，"
            "看盘面是红的还是绿的就好了",
            "你要把很复杂的东西，简化成你能操作的东西，你需要考虑的东西越少越好，现在最强的东西是什么，"
            "用眼睛看就可以了，不用去想",

            "开始分歧了，后排股都要卖，在后排都死得差不多的时候，最强的龙头筹码才会松动，"
            "就像作战，各个部队的战士都挡不住了，都死光了，司令部才会沦陷，然后朝代灭亡，天崩地裂",
            "挣也好，亏也好，卖得好也好，卖得不好也好，爱咋滴咋滴，机会是等出来的，"
            "想那么多做什么，想多了浪费脑子",
            "条件成立你才会去买，那就需要分析哪些是主要条件，哪些是次要条件"
        ]
        direction = "最近方向：" + "，".join(direction_list)
        zhu = ""
        if first_page:
            for i, yu_lu in enumerate(yu_lu_list):
                zhu = zhu + "{}、{}\n".format(i + 10, yu_lu)
        # 添加段落
        doc.add_paragraph(title + "\n" + info + "\n\n" + ti_cai_text + "\n\n" + zhu)
        first_page = False

    # 保存文档
    doc.save('result/{}.docx'.format(ti_cai))


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


def get_proxy_ip(proxy_ip):
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
    return proxy_ip


if __name__ == '__main__':

    # 获取个股代码
    get_code_map()

    # 获取题材涨停的个股
    ti_cai_list = ["涨停"]
    zhang_ting_map = get_zhang_ting_map(ti_cai_list)
    print("zhang_ting_map:", zhang_ting_map)

    count = 0
    proxy_ip = ""
    for ti_cai, name_list in zhang_ting_map.items():
        print("ti_cai:", ti_cai)
        print("name_list:", name_list)
        if len(name_list) <= 0:
            continue

        # 爬取涨停数据
        info_map = {}
        for name in name_list:
            # if count % 2 == 0:
            #     proxy_ip = get_proxy_ip(proxy_ip)
            # count = count + 1

            proxy_ip = get_proxy_ip(proxy_ip)

            article_info = get_article_info(name, proxy_ip)
            if article_info:
                info_map[name] = article_info

        print("info_map:", info_map)
        if len(info_map) <= 0:
            continue

        # 1:一致，2：分歧，3：退潮，4：混沌
        cycle_and_action = emotional_cycle_action.get(1)

        # 最近方向
        direction_list = ["车路云", "自动驾驶", "铜缆", "bcp", "半导体芯片"]
        # 保存到word
        save_word_text(ti_cai, info_map, direction_list, cycle_and_action, "A4")
