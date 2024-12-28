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

    h1 = doc.add_heading("时间节点", level=2)
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    time_point = "1、涨潮：买盘一鼓作气， 再而衰， 三而竭， 阶段性顶\n" \
                 "2、退潮：卖盘一鼓作气， 再而衰， 三而竭， 阶段性底\n" \
                 "3、今天比昨天：强，弱"

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

            "看盘：先大后小，自上而下",
            "事情本身是很简单的，但由于涉及金钱利益，恐惧贪婪，患得患失会使人心里变形，做决策不理智，"
            "从矛盾对立统一的角度看，输赢本事一体，输得起才能赢得起，只拿属于自己的那一份，你可以永久的做下去",
            "思考时不能加入太多的变量，不然复杂度会变得非常高，脑子就会混沌",
            "向内求，人性无善无恶，向外求，人性有善恶，人性之上，规律之下",
            "市场没有量，其实就是玩的人少了，为什么你不挣钱：因为好的机会很少，你却出手很多",

            "抓住主要：",
            "要善于抓大放小，主要问题，重大决策一定要做好，大大小小的事都重视，必然会精力分散，影响重大决策",
            "敌强我弱是客观存在的问题，此时如何保存力量是主要的矛盾，做好战略防御，及时退却，使自己立于主动地位",

            "化繁为简：找出主要矛盾，忽略所有次要矛盾，小行情，行情差，大杀前错过买点时的大胆，是你亏钱的根源",
            "其实不需要智慧，只需要做好选择，行情不好的时候，不要出手，行情好的时候，猛干核心",
            "二波本质是让你看清楚个股的地位，辨识度，人气，群众基础，看清楚后不等于要买，决定你要不要买，"
            "个股，图形是次要矛盾，时间节点，大盘环境，题材人气，小弟强度才是主要矛盾，真牛逼，"
            "到高位之后还有人气，我再看你",

            "时间节点:",
            "市场大哥断板到大杀之前，机会都是你们的，持续杀几天，杀彻底之后，出现新题材盯着前排大胆做",
            "每半个月，只有几天捕鱼期，不在这个时间范围内，风浪会很大，浪涨3天，要跌2天，浪涨10天，要跌6天",

            "市场大哥都死了，其他大哥也不能活，连板天梯就撑不住了，板块大哥都死了，就不要去板块里面玩了",
            "亏钱永远比赚钱容易，躲过下雨天已经成功了一半，市场整体比昨天弱时，欣赏别人赚钱就好了",
            "慢下来，坚持无减肥，不要犯错，要冷静，看不见猛就往上冲，本质就是贪，大部分的预判都是错的，都是胡思乱想",

            "绝对优势：",
            "当局势有优势，辅助都很强，大哥就可以在团战中三杀，四杀，暴走，反之酱油秒躺，大哥也站不住",
            "打仗没有什么神秘，打得赢就打，打不赢就走，抓住你的弱点，跟着你打，你打你的，我打我的",
            "要从全局考虑，从高低位、新旧题材四个纬度，找出关键点在哪里，明确该做什么，不该做什么，"
            "永远都会有机会，不以人的意志为转移",
            "任何一场博弈，都是以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，要有绝对的，压倒性的优势，"
            "如果没有这个条件只能等，在绝对实力面前，一切技术都是花里胡哨",

            "退潮：",
            "开始分歧了，后排都要卖，当龙头也断板了，不涨了，最漂亮的那个也没人追了，说明买盘力量已经枯竭了，"
            "高位已经撑不住了，就像楼市，北京房价都跳水了，其他城市肯定好不到哪去",

            "最高标断板的时候，高位情绪就弱了，第1、2天要把高位股全卖了，第2、3天情绪会惯性从顶部往下杀，"
            "第4天之后大部分的中高位都死的差不多了，下杀的情绪释放差不多了，高标可能只剩下1、2个，目标少了就清晰了，也就是最高标断板，会带着好几个高标跟着它一起死，第4天之后，"
            "等底部情绪好了，底部会反哺，反推高标",

            "一波高潮至大杀之后，为什么老东西就不行了，因为个股中会有很多获利、埋伏、套牢盘，筹码很复杂，"
            "筹码已经坏掉了，小弟没力气了，板块没力气了，大哥也走得不流畅了",

            "--------------------------------------------------------------------------",
            "老师所有的操作都在告诉你，要买就买那个最独一无二的，最强的，宁可不做也要缩小范围，减少目标",
            "市场不认可的东西都是垃圾，如果从个股看不出确定性，多看看板块，确定性就有了",

            "牛市和熊市的区别：牛市的机会多一些，仅此而已，跟每一个小周期一样，牛市大周期结束都是那90%的人买单",
            "把很复杂的东西，简化成你能操作的东西，考虑的东西越少越好，现在最强的东西是什么，用眼睛看就可以了，不用去想",
            "是不是高潮，就需要想一下有没有下一波更高亢的情绪出来，如果没有，当前就是高潮，反之低潮也一样",

            "自我约束：1、调整了几天的二波，2、大杀之后的N型首版，3、强得令人发指的、独一无二的龙头，"
            "其他垃圾以及除龙头以外的二板以上跟我一毛钱关系都没有，引入太多变量，只会增加复杂度",

            "华映科技牛逼吗？在我眼里就是个垃圾，他涨一万个板也是垃圾，常山，海能达，四川这些才是大道",
            "主升浪，二波，其实就是做首板，这种首板往往都是发生在情绪好的时候，因为大资金不会瞎发动，而情绪的好坏都会反应在高标身上",
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
    doc.add_paragraph("Q: 明天拉哪个板块，哪个个股，能得到市场认同，形成合力，能盘活整个市场")
    bj = """ 
    主要矛盾：三大范围：时间节点、题材方向、核心个股
    一、时间节点：
        1、涨潮：向下持续杀几天，杀彻底之后诞生
        2、退潮：市场最高标断板，小弟推不上去，买盘动力衰竭
        3、规律：随着时间的变化，买卖强弱关系是会相互转化的，即阴阳循环，祸兮福所倚，福兮祸所伏
        4、高位出现亏损，空头占优，此时模式的使用应该降低频率，高位出现盈利，多头占优，此时模式的使用应该大胆起来
        
    二、题材板块：
        1、大
        2、新
        3、强
        
    三、龙头：
        1、股性：量价关系
        2、人气：群众基础
        3、资金：买盘力量
        
    四、代码简写：
        if "时间节点" == "最高标断板～大杀彻底之前":
            "全部放弃"
        else:
            if "方向" == "主线题材" and "个股" == "核心龙头":
                "可以考虑"
            else:
                "全部放弃"
    
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
