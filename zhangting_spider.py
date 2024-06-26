# encoding: utf-8
import logging
import re
import time
from datetime import datetime

import akshare as ak
import requests
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


def get_article_info(name):
    print("------------------------------")
    text = ""
    for _ in range(20):
        try:
            jiucai_url = 'https://www.jiuyangongshe.com/search/new?k={}&type=5'.format(name)
            print("jiucai_url:", jiucai_url)
            response = requests.get(jiucai_url, allow_redirects=False)
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
                response = requests.get(href_full_url, allow_redirects=False)
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


def save_word_text(ti_cai, info_map, lao_long_gao_du, cycle_and_action, print_type="A5"):
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
        zhu4 = "1、亏钱永远比赚钱容易，因为市场不好的时候，亏得最惨的一般都是追高的，" \
               "市场好的时候，涨起来的是因为新闻助推的，方向是随机，你不一定跟得上\n" \
               "2、越是急着，越是找不到，当个傻子吧，不是风动，不是幡动，是心在动\n"
        zhu5 = "3、任何一场博弈，完胜的条件是士气要高涨，要以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，" \
               "要有绝对的，压倒性的优势，如果没有这个条件只能等\n" \
               "4、大行情唯唯诺诺的根源是小行情，行情差的大胆\n" \
               "5、环境差：最好的没人要的时候，丑的有人要吗，环境好：先抢最好的，如果抢不到只能将就丑的\n" \
               "6、复盘：自上而下：1、先研究主流题材；2、再研究主流题材人气核心标的；3、有没有二波预期\n" \
               "7、看盘要找出每一个板块异动上涨的原因"

        zhu = ""
        if first_page:
            zhu = zhu4 + zhu5
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


if __name__ == '__main__':

    # 获取个股代码
    get_code_map()

    # 获取题材涨停的个股
    ti_cai_list = ["涨停"]
    zhang_ting_map = get_zhang_ting_map(ti_cai_list)
    print("zhang_ting_map:", zhang_ting_map)

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

        # 老龙高度，当前情绪周期节点，计划
        lao_long_gao_du = 13
        # 个股标签：1:最强龙头，2:缩量秒板跟风，3:放量换手跟风，4:放量弱板跟风，5:老周期中高位

        # 1:一致，2：分歧，3：退潮，4：混沌
        cycle_and_action = emotional_cycle_action.get(1)

        # 保存到word
        save_word_text(ti_cai, info_map, lao_long_gao_du, cycle_and_action, "A4")
