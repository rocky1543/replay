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
            "复盘关键时机是阶段性的顶和底",
            "处事：人性之上，规律之下，看盘：先大后小，自上而下，在哪里打仗，能不能赢，明天有没有更多的人来接盘",
            "亏钱永远比赚钱容易，躲过下雨天，已经成功了一半，少私寡欲，才能无穷无尽",
            "你关注的主要矛盾一定是在核心个股上，其他都是次要矛盾，都应该忽略掉，小行情，行情差，错过买点时的大胆，是你亏钱的根源",

            "二波本质是让你看清楚个股的地位，辨识度，人气，群众基础，看清楚后不等于要买，决定你要不要买，"
            "个股，图形是次要矛盾，时间节点，大盘环境，题材人气，小弟强度才是主要矛盾，你真牛逼，"
            "到高位之后还有人气，我再看你",
            "很多时候，不是技术的问题，是选择标准的问题，成功率来源于更高的要求，而不是饥不择食",

            "慢下来，坚持无减肥，不要犯错，要冷静，看不见猛就往上冲，本质就是贪，大部分的预判都是错的，都是胡思乱想",

            "牛市和熊市的区别：牛市的机会多一些，仅此而已，跟每一个小周期一样，牛市大周期结束都是那90%的人买单",
            "打仗没有什么神秘，打得赢就打，打不赢就走，抓住你的弱点，跟着你打，你打你的，我打我的，我们的部队，走也走得，打也打得",
            "战略上藐视敌人：胜利来源于压倒性优势，万物皆周期，永远会有机会，不以人的意志为转移",
            "战术上重视敌人：过程是艰难曲折的，要慎重，耐心等待机会，当战略战术确定之后，剩下比的就是知己知彼，谁更了解局势",

            "市场不认可的东西都是垃圾，杂毛垃圾会让你操作变形，跟酱油换命不值得，如果从个股看不出确定性，多看看板块，确定性就有了",
            "市场没有量，其实就是玩的人少了，为什么你不挣钱：因为好的机会很少，你却出手很多",

            "任何一场博弈，都是以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，要有绝对的，压倒性的优势，"
            "如果没有这个条件只能等，在绝对实力面前，一切技术都是花里胡哨",

            "当局势有优势，辅助都很强，大哥就可以在团战中三杀，四杀，暴走，反之酱油秒躺，大哥也站不住",

            "成交量放大，要么是主动买盘变多了，要么是主动卖盘变多了，放量时，吹古拉朽往上攻就是强，放量攻不上去就是弱",
            "把很复杂的东西，简化成你能操作的东西，考虑的东西越少越好，现在最强的东西是什么，用眼睛看就可以了，不用去想",
            "是不是高潮，就需要想一下有没有下一波更高亢的情绪出来，如果没有，当前就是高潮，反之低潮也一样",

            "开始分歧了，后排股都要卖，在后排都死得差不多的时候，龙头筹码才会松动，"
            "就像打仗，各个部队的战士都挡不住了，都死光了，司令部才会沦陷，然后朝代灭亡，天崩地裂",

            "去弱留强：龙头分歧给机会，走弱的虹吸效应是小弟死掉的主要原因",

            "一波高潮后，个股中会有很多获利、埋伏、套牢盘，筹码很复杂，筹码已经坏掉了，"
            "小弟没力气了，板块没力气了，大哥也走得不流畅了，这个时候的筹码结构已经变复杂了，就该用小仓位去试了",

            "你做股票，你的注意力在各种小垃圾上，你就做不到那个最大的龙头，龙头就是人气，人人可参与，是群众基础，是能团结一切能团结的力量",
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
    doc.add_paragraph("Q: 我如果是神，明天我拉哪个板块，哪个个股，能得到市场认同，形成合力，能盘活整个市场\n")
    bj = """ 
    主要矛盾：比较的三大方向：时间节点、题材方向、核心强势个股，也就是每天复盘需要考虑的三大方向
    次要矛盾：其他涨停个股，只是未了更好的了解市场
    
    怎么比较？
    一、时间节点：
        1、涨潮：一鼓作气，再而衰，三而竭，便是阶段性顶
        2、退潮：一鼓作气，再而衰，三而竭，便是阶段性底
        3、当卖盘强的时间节点(阶段性顶部)，放弃所有机会
        4、当买盘强的时间节点(阶段性底部)，考虑主线的核心，其他全部放弃
        5、规律：随着时间的变化，买卖强弱关系是相互转化的，就是阴阳的相互循环，即祸兮福所倚，福兮祸所伏
    二、题材板块：
        1、题材大小
        2、所处阶段
        3、资金进攻力度
    三、龙头：
        1、股性：量价关系
        2、人气：群众基础
        3、资金：进攻力度
        
    四、主要矛盾是大盘环境，时间节点，题材板块，次要矛盾是龙头个股，不符合主要矛盾，一律不考虑
    
    五、代码简写：
        if "时间节点" == "卖盘强势":
            "全部放弃"
        else:
            if "方向" == "主线题材" and "个股" == "核心龙头":
                "可以考虑"
            else:
                "全部放弃"
    """
    doc.add_paragraph(bj)
    doc.save('result/{}.docx'.format(ti_cai))


def mo_shi():
    """
    主要矛盾：比较的三大方向，也就是每天复盘需要考虑的三大方向
        1、时间节点
        2、题材方向
        3、核心强势个股
    次要矛盾：
        1、其他涨停个股，只是未了更好的了解市场

    随着时间的变化，买卖强弱关系是可以相互转化的，就像阴阳图一样，往复循环，生生不息
        1、买盘一鼓作气，再而衰，三而竭，便是顶，此时卖盘最强(敌人)
        2、卖盘一鼓作气，再而衰，三而竭，便是底，此时买盘最强(战友)
    当卖盘强的时间节点(阶段性顶部)，放弃所有机会
    当买盘强的时间节点(阶段性底部)，考虑主要方向的主要个股，放弃所有的次要方向，以及所有的主要方向的次要个股

    :return:
    """
    if "时间节点" == "卖盘强势":
        "全部放弃"
    else:
        if "方向" == "主线题材" and "个股" == "核心龙头":
            "可以考虑"
        else:
            "全部放弃"


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
