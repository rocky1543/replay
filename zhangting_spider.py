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
    for _ in range(20):
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
        for _ in range(2):
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

                info = str(info).replace("<div class=\"pre-line\" data-v-aa5f53ac=\"\">", "")
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


def save_word_text(ti_cai, info_map, print_type="A5"):
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

        yu_lu_list = [
            "处事：人性之上，规律之下，看盘：先大后小，自上而下，在哪里打仗，能不能赢，谁是大哥",
            "亏钱永远比赚钱容易，躲过下雨天，已经成功了一半，少私寡欲，才能无穷无尽",
            "你关注的主要矛盾一定是在有压倒性优势的个股上，这些一定是大行情时主线中的核心，其他都是次要矛盾，"
            "都应该忽略掉，小行情，行情差，错过买点时的大胆，是你亏钱的根源",

            "慢下来，坚持无减肥，不要犯错，要冷静，看到的强才是真的强，看不到强只能等，大部分的预判都是错的，都是胡思乱想",
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

            "任何一场博弈，都要士气高涨，以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，要有绝对的，压倒性的优势，"
            "如果没有这个条件只能等，在绝对实力面前，一切技术都是花里胡哨",

            "二波：题材大小，决定龙头高度，题材能持续，龙头就能持续，当局势有优势，辅助都很强，"
            "大哥就可以在团战中三杀，四杀，暴走，反之酱油秒躺，大哥也站不住",

            "二波本质是让你看清楚个股的地位，有没有辨识度，有没有人气，有没有群众基础，"
            "看清楚后再出手，你真牛逼，到高位之后还有人气，我再看你，"
            "你经历的痛苦我都不参与，等你准备星辰大海了，我再来",

            "成交量放大，要么是主动买盘变多了，要么是主动卖盘变多了，放量时，吹古拉朽往上攻就是强，放量攻不上去就是弱",
            "把很复杂的东西，简化成你能操作的东西，考虑的东西越少越好，现在最强的东西是什么，"
            "用眼睛看就可以了，不用去想",
            "是不是高潮，就需要想一下有没有下一波更高亢的情绪出来，如果没有，当前就是高潮，反之低潮也一样",

            "开始分歧了，后排股都要卖，在后排都死得差不多的时候，龙头筹码才会松动，"
            "就像打仗，各个部队的战士都挡不住了，都死光了，司令部才会沦陷，然后朝代灭亡，天崩地裂",
            "挣也好，亏也好，卖得好也好，卖得不好也好，爱咋滴咋滴，机会是等出来的，"
            "想那么多做什么，想多了浪费脑子",

            "去弱留强：龙头分歧给机会，羊群仓位立马从小弟切到龙头里，龙头走弱的虹吸效应是小弟死掉的主要原因",

            "一波高潮后，个股中会有很多获利、埋伏、套牢盘，筹码很复杂，筹码已经坏掉了，"
            "小弟没力气了，板块没力气了，大哥也走得不流畅了，所以不是所有的二波都是好的，"
            "你要看板块、跟风、龙头的筹码结构是不是夯实的，需要考虑消息面，当下的市场情绪，"
            "人气能不能拉起一个板块大部分个股的筹码",
            "一波挣大钱之后就变得难做了，这个时候的筹码结构已经变复杂了，就该用小仓位去试了",

            "特这一路但凡研究过镇委书记，州长这些东西，他就做不了总统，"
            "你做股票，这一路但凡研究一下各种小垃圾，你就永远做不到那个最大的龙头",
            "龙头就是人气，人人可参与，是群众基础，是能团结一切能团结的力量，能容纳所有资金，"
            "允许所有资金在某一天自由进出",
            "华映科技牛逼吗？在我眼里就是个垃圾，他涨一万个板也是垃圾，常山，海能达，欧菲光，长城，"
            "上海电气，宗申，四川，这些才是大道",
            "龙头说白了就是学会比较，和其他个股比较，和历史比较，和环境比较",

            "条件成立你才会去买，那就需要分析哪些是主要条件，哪些是次要条件",
            "打板的目的是为了明天的溢出效应，明天有没有溢出效应，和什么有关呢？",
            "这几年一路走来的艰难困苦，有什么值得歌颂的呢",
            "本质上，不是一个有天赋的人，打游戏如此，打球如此，智商也如此"
        ]
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


if __name__ == '__main__':

    # 获取个股代码
    get_code_map()

    # 获取题材涨停的个股
    ti_cai_list = ["涨停"]
    zhang_ting_map = get_zhang_ting_map(ti_cai_list)
    print("zhang_ting_map:", zhang_ting_map)

    count = 0
    for ti_cai, name_list in zhang_ting_map.items():
        print("ti_cai:", ti_cai)
        print("name_list:", name_list)
        if len(name_list) <= 0:
            continue

        # 爬取涨停数据
        info_map = {}
        for name in name_list:
            article_info = get_article_info(name)
            if article_info:
                info_map[name] = article_info

        print("info_map:", info_map)
        if len(info_map) <= 0:
            continue

        # 保存到word
        save_word_text(ti_cai, info_map, "A4")
