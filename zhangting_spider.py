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

    h1 = doc.add_heading("复盘", level=2)
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fu_ban = "复盘三步曲：\n" \
             "1、分析主流板块: 大的主流在哪里，主流没走完，就只能在这个主流里面选股\n" \
             "2、分析时机：通过观察连板天梯的强弱转换，分析情绪强弱变化\n" \
             "3、分析它领涨的个股：寻找主流中各个小周期领涨股\n"
    doc.add_paragraph(fu_ban)
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

            "这并不是我生活的主要，懒一点，低调一点，少管它一点，大善即大恶",
            "你看这火是不是很旺，但过一会它就过去了，美好成为美好的时候，它具备的条件已经开始变化了，导致它慢慢消亡，"
            "像这火烧得很旺的时候已经在慢慢燃尽了",
            "为什么有的人越努力越焦虑？因为他们只看到了努力，却忽视了规律，就像老百姓种地，再着急也要遵循春种秋收"
            "的自然规律，规律是在一定条件下能够稳定、重复发生的事情",
            "看盘：先大后小，自上而下，关注主要，忽略次要，人性之上，规律之下，三大原则：大主流，大未来，大容量，"
            "博弈大忌：贪图对手的小利",
            "龙头就是去理解那个充分条件时产生的砸不死的合力，如果砸死了，证明买的票是垃圾，割肉就好了",
            "赚钱的本质一定是低买高卖：1、情绪低点，足够低位，2、向上有足够强的动力",
            "事情本身是很简单的，但由于涉及利益，恐惧贪婪，患得患失会使人心里变形，做决策不理智，从矛盾对立统一的角度看，"
            "输赢本是一体，只有放下赢的喜悦，才能放下输的痛苦",
            "思考时不能加入太多的变量，不然复杂度会变得非常高，脑子就会混沌",
            "市场没有量，其实就是玩的人少了，条件不充分时的大胆，是你亏钱的根源",
            "在市场极其弱的时候，情绪转强可能很快就到来，这时去找和大盘，板块共振向上的最强个股，"
            "你为什么做不好，因为符合条件的机会是极其少，你却又有一颗无限想操作的心",
            "基本规律：1、涨多了会跌，跌多了会涨，涨得越多，跌得越多，2、大杀之后，经过充分调整的位置才算安全，"
            "3、急没有用，反而会产生反作用，4、高潮过了情绪很容易崩溃",
            "如果你在顶层做了正确的事，底层结果就不会差",

            "好票：1、有资金进场，2、没有透支行情，3、形成好位置",
            "心不死，道不生：好坏，美丑，穷富都是矛盾对立的双方，如果你不能放下其中一方，矛盾双方就在你心里斗争，"
            "内耗，折磨你，直至你不在乎它，它才会消失",

            "",
            "抓住主要：",
            "要给自己定清晰的界限，当下时机，当下板块，当下个股该不该看，不该看的，一律不看",
            "要善于抓大放小，主要问题，重大决策一定要做好，大大小小的事都重视，必然会精力分散，影响重大决策",
            "敌强我弱是客观存在的问题，如何保存力量是主要的矛盾，做好战略防御，及时退却，使自己立于主动地位",

            "其实不需要智慧，只需要做好选择，行情不好的时候，不要出手，行情好的时候，猛干核心",
            "二波本质是让你看清楚个股的地位，辨识度，人气，群众基础，看清楚谁是主要个股，看清楚后不等于要买，"
            "决定你要不要买，个股，图形是次要矛盾，时间节点，大盘环境，题材人气，小弟强度才是主要矛盾，真牛逼，"
            "到高位之后还有人气，我再看你",
            "要从全局考虑，从高低位、新旧题材四个纬度，找出关键点在哪里，明确该做什么，不该做什么",

            "",
            "绝对优势：",
            "当局势有优势，辅助都很强，大哥就可以在团战中三杀，四杀，暴走，反之酱油秒躺，大哥也站不住",
            "打仗没有什么神秘，打得赢就打，打不赢就走，你打你的，我打我的",
            "任何一场博弈，都是以多胜少，以强胜弱，牛刀杀鸡，狮子打兔子，要有绝对的，压倒性的优势，"
            "如果没有这个条件只能等，在绝对实力面前，一切技术都是花里胡哨",

            "",
            "退潮:",
            "市场大哥断板到大杀之前，机会都是你们的，持续杀几天，杀彻底之后，出现新题材盯着前排大胆做",
            "市场大哥都死了，本质是连板天梯(高位股)撑不住了，其他大哥也不能活，板块大哥都死了，就不要去板块里面玩了",
            "亏钱永远比赚钱容易，躲过下雨天已经成功了一半，慢下来，坚持无减肥，不要犯错，要冷静，看不见猛就往上冲，"
            "本质就是贪，大部分的预判都是错的，都是胡思乱想",

            "开始分歧了，后排都要卖，当龙头也断板了，不涨了，最漂亮的那个也没人追了，说明买盘力量已经枯竭了，"
            "高位已经撑不住了",

            "最高标断板的时候，第1、2天要把高位股全卖了，第2、3天情绪会惯性从顶部往下杀，第4天之后"
            "大部分的中高位都死的差不多了，下杀的情绪释放差不多了，高标可能只剩下1、2个，目标少了就清晰了，"
            "也就是最高标断板，会带着好几个高标跟着它一起死，第4天之后，等底部情绪好了，底部会反哺，反推高标，"
            "能不能做，看情绪转强的力度",

            "为什么大杀之后老东西就不行了，因为个股中会有很多获利、埋伏、套牢盘，筹码很复杂，筹码已经坏掉了",
            "怎么判断题材有没有结束：龙头核心A杀，当下属于退潮阶段，龙头人气没散，板块指数量能很足，题材炒作就没结束，"
            "板块小弟很活跃，龙头核心就不会差",

            "",
            "其他：",
            "老师所有的操作都在告诉你，要买就买那个最独一无二的，最强的，宁可不做也要缩小范围，减少目标，"
            "你敢在这个垃圾上冒险，就敢在其他类似的垃圾上冒险",
            "市场不认可的东西都是垃圾，如果从个股看不出确定性，多看看板块，确定性就有了",

            "牛市的机会多一些，仅此而已，跟每一个小周期一样，牛市大周期结束都是那90%的人买单",
            "把很复杂的东西，简化成你能操作的东西，考虑的东西越少越好，现在最强的东西是什么，用眼睛看就可以了，不用去想",

            "华映科技牛逼吗？在我眼里就是个垃圾，他涨一万个板也是垃圾，常山，海能达，四川这些才是大道",
            "主升浪，二波，其实就是做首板，这种首板往往都是发生在情绪好的时候，因为大资金不会瞎发动，而情绪的好坏都会反应在高标身上",
            "夫战，勇气也。一鼓作气，再而衰，三而竭，彼竭我盈，故克之，夫大国，难测也，惧有伏焉，吾视其辙乱，望其旗靡，故逐之",
            "这几年一路走来的艰难困苦，有什么值得歌颂的呢，本质上不是一个有天赋的人，打游戏如此，打球如此，智商也如此"
        ]
        zhu = ""
        if first_page:
            line = 0
            for yu_lu in yu_lu_list:
                if yu_lu:
                    zhu = zhu + "{}、{}\n".format(line + 10, yu_lu)
                    line = line + 1
                else:
                    zhu = zhu + "\n"
        # 添加段落
        doc.add_paragraph(title + "\n" + info + "\n该股炒作核心本质：\n\n" + ti_cai_text + "\n\n" + zhu)
        first_page = False

    # 保存文档
    bj = """ 
    关注的主要三大范围：时间节点、题材方向、核心个股
    一、时间节点：涨潮， 退潮，随着时间变化，买卖强弱关系是会相互转化的，即阴阳循环，祸兮福所倚，福兮祸所伏
    二、题材板块：大新强，大主流，大未来，大容量
    三、龙头：股性，人气，资金强度
    四、代码简写：
        if "时间节点" == "最高标断板～大杀彻底之前":
            "尽可能放弃"
        else:
            if "方向" == "主线题材" and "个股" == "核心龙头":
                "可以考虑"
            else:
                "尽可能放弃"
    
    五、规律是事物存在某种本性，且在一定条件下可以稳定，重复发生的事，如果事物没有那种本性，无论提供什么条件，都不会产生相应的变化。  
    你需要的本性和条件是什么？ 
    本性：
    1、题材三大原则：大主流，大未来，大容量
    2、龙头：
        1、有资金进场，量价图形好，有人气
        2、没有透支行情，有资金维护，分歧整体向上
        3、形成好位置：
            1、充分调整后的二波首板，N型首版
            2、趋势主升浪：强于自身的历史，强于同行，强于板块，强于大盘     
    3、事物固有本性例子：鸡蛋能变成小鸡，石头不能
    
    外在条件：
        1、充要条件：集中力量认真做
        2、必要条件：持续做 
            1、大盘没有系统性风险：最好是放量向上，次之稳住不跌
            2、赚钱的本质一定是低买高卖，所以情绪最好在低点，足够低位，最好是连续大杀几天，杀了再杀之后的低点
            3、情绪转强，大盘，板块，龙头共振向上，买盘要有压倒性优势，足够强劲的动力
            4、板块氛围好，小弟很多很强
            
        3、充分条件：尽量少做
        4、负面条件：坚决不做
            1、龙头断板，连板天梯中的高位股撑不住，高位整体向下杀，要学会放弃
            2、大盘有系统性风险，暴跌带崩情绪，要学会放弃     
        5、外在条件例如：鸡蛋需要特定的温度才能成小鸡
        
    做事万能公式：           
        事物变化的底层规律 = 事物固有本性 + 外在条件
        本性：本身固有的性质
            1、阳性质：规定事物的现在，直接显露，例如白纸的颜色是白的
            2、阴性质：规定事物的未来，隐藏在体内，想显露出来需要外在条件刺激，例如纸遇火可燃
        条件：1、充要条件，2、充分条件，3、必要条件   
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
