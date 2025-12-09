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


def save_word_text(bu_zhang_long, lian_ban, name_list, info_map, print_type="A5"):
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
    add_lian_ban_split = True
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

        if key not in bu_zhang_long and add_lian_ban_split and add_he_xin_split:
            add_lian_ban_split = False
            doc.add_paragraph("- " * 90)

        if key not in lian_ban and key not in bu_zhang_long \
                and not add_lian_ban_split and add_he_xin_split:
            add_he_xin_split = False
            doc.add_paragraph("- " * 90)

        # 添加标题，0表示样式为title
        h1 = doc.add_heading(key, level=2)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加段落
        doc.add_paragraph(title + "\n" + info + "\n\n" + ti_cai_text + "\n")

    # 核心
    he_xin = """
    *、第一天很重要，先找方向，再看羊群会不会往这个方向聚集
        *、板块主升，托举龙头主升，这才是是正解
        *、社会讨论度决定板块地位，资金活跃度决定龙头地位，板块讨论度带来的资金流动性会把龙头托举起来
    *、人气 = 社会讨论度 + 资金活跃度
        *、二波关键词：连板，横盘，辨识度，人气，主线，方向核心，启动初期，量价完美
        *、知道的，讨论的，关注的，参与交易的人越多，物品越好交易，也就是物品越好流动
        *、热点要新才能一下子吸引来很多人，要有共鸣才有持续性，连续加速后就避开一下
        *、市场最核心股就一个，一股之下皆是跟风小弟，要把精力放在最核心的那只灵魂股身上
        *、风来了，情绪就来了，情绪来了，人就聚集了
        *、如果能预判接下来会有很多人来接力，人气足够旺就可以了
    *、大数定律
        *、赚多出的钱它也会亏回去，亏多出的钱它也会再赚回来，均值是会回归的
        *、去掉概率低的，保留概率高的，提升每一次出手的概率，当操作足够多的时候，盈利就会回归到均值上
        *、还需要在提高赢的概率，大杀之后，最强板块的最强人气个股，慢即是快，少即是多
        *、外重者内拙
            *、徒弟：师父，以我的资质，开悟需要多久？师父：十年
            *、徒弟：如果我加倍苦修呢？师父：二十年
            *、徒弟：如果我夜以继日，不休不眠呢？师父：那你将永无开悟之日
    *、龙头：
        *、鹿角，鹰抓，鱼鳞，蛇身，在这种特别着相的情况下，你会被相所带走
        *、我们要找出龙的魂，一切形态随着魂而动，人气就是龙的魂，龙的神
        *、一定要学会放弃，一定要删除，简化，简单，直到可以落地
        *、补涨切换说的是方向，看的都是该方向里的核心，他们可能是市场大哥的小弟
        *、龙头就连板最多、封板最强那一只，毫无争议的第一名，唯一高标，唯一性自带人气，龙头就是板块的脊梁
        *、等同法则：
            *、确认谁是龙头 = 确认谁是第一名；连板龙头 = 连板第一高标；情绪龙头 = 独一无二人气股
        *、龙头基石都是人气：
            *、虹吸效应：强的东西给机会，会吸干地位于他的标的的人气，资金，流动性
            *、束水攻沙：打造高标，维持高标在高位强势需要大量的资金，资金需要收敛，凝聚到一个点
            *、高度不一定是龙头，但是人气、辨识度、流动性收敛的地方肯定是龙头
        *、相：
            *、叫她不凶，她心中已有凶相，而能做到和善，是对凶的克制，是戒
            *、而叫她和善，她心中已有和善之相，她和善只是顺其自然
        *、面带点：
            *、大盘是大的面，板块是小的面，大面推小面向上，小面推点向上，这种向上的力是最强的
            *、以点带面，吸引资金进来，最终还需要面推点，加强上涨
        *、指数：
            *、作用是预判大环境【亏钱效应】和【赚钱效应】
            *、市场不好，题材也走不高，指数上涨或不跌，题材就能走很高的高度
            *、大盘，个股只有【放量上涨】才是健康的
            *、大盘缩量下跌后，跌不动了，然后放量，出现一个赚钱效应
        *、复盘逻辑：
            *、搞懂解决什么具体问题，影响多少人，影响多少钱
            *、为什么小米值那么多钱？是因为智能手机市场值那么多钱，这是多大的市场
        *、大哥：
            *、有比你猛的东西在高举高打，有比你强的东西在吸金，你现在起来算什么，跟风吗
            *、当下谁最强，最猛，人气最旺，最吸金，就是最优解，就好比居庸关的人气和八达岭就没法比
            *、市场没有其他东西比它好了，那么它就是最好的，他比你硬，比你强，凭什么他不行
            *、没有小弟的高标，死的时候很容易A杀，因为没有小弟反哺他
        *、第一天很重要：
            *、转折向下：今天的硬板，明天可能被板块整体回落拉下马
            *、转折向上：今天的烂板，明天可能被板块整体上升推起来
        *、简单过程：
            *、一波潮水起， abcde领涨，然后潮水褪去，随机死去一批，剩下三三两两，如def
            *、然后一波潮水又起，defhy领涨，其中def辨识度更高一些
            *、然后潮水褪去，随机又死一批，剩下fh
            *、如此往复，每次要找潮水褪去谁命最硬，潮水起来谁地位最高 
        *、光神：
            *、退潮的结果就是重新洗牌，推到重来，筛选掉一部分，保留一部分
            *、研究市场情绪的意义就在于如何让自己参与到每一波行情的起始
            *、再爆炸的行情，最多也就是三五天，螺旋式前进是必然规律
            *、当最勇敢的资金有90%被割肉出来的时候，又构成了一个新的起点，开始新的游戏，周而复始
            *、在高潮中永远抱着敬畏的心态，在绝望中永远要充满希望，即：毁灭中诞生
        *、杂文：
            *、上涨的第一天大胆弄，第二天小心弄，第三天谨慎弄
            *、下跌的第一天谨慎弄，第二天小心弄，第三天大胆弄
            *、就跟打游戏一样，别人的技能没放完，你就贸然出击不就是找死嘛
            *、急于求成，气急攻心，无间地狱，任何你放不下，想不开，静不了，去强求的事，都是德不配位而已
            *、任何事物都像那一朵花，盛夏开得再灿烂，夏天过去的时候，都会凋零落到地里，题材如此，风口也如此
            *、人的一切执念都是源自于对有的追求，有求于外者内拙
            *、走不出来，好像也不会死，交易的本质是观察自己做交易，把一个简单的事情做到极致
            *、没有稳定的系统，只有稳定的人，游戏规则是为你制定的，你必须跳出来，跳回到你的生活里
        *、行情好的时候多做，行情不好的时候少做
            *、之前我认为的行情好，以及是高潮了
            *、行情好：大题材，大主流，大容量，大龙头，梯队完整，主线清新，市场有高度，高位有人气
            *、多做：对的时间做对的事情，要有节奏，大周期里做小周期
        *、方法论：
            *、做首板就是看高做低，即：看高位最有人气龙头做他的属性补涨首板
            *、做龙头就是做二板之上最有人气标的，即：只做第一名，二板以上只做龙头
            *、拳头收回来再打出去才有力气，伸出去一半了，已经卸力了
            *、能否继续看的逻辑：有曝光，有流量，有社会讨论度，人气就会持续，题材和龙头就能持续
            *、一轮行情的流程：1、龙头上涨；2、龙头补涨；3、题材切换
            *、龙头：强者恒强，只买最强，只看班级第一学霸；补涨龙=大题材里，高低切；补涨=大题材里，看高做低
        老师：
            *、复盘看看当天炒什么题材，再看看有没有可能二波的
            *、盘中看看今天炒什么题材，看看有没有【首板】可能二波的
            *、二波：市场羊群去哪，你就是哪儿找机会，大盘＞方向＞题材＞龙头
            *、方向：龙头，补涨，补涨龙，切换新题材，老人气核心
            *、老师主要做的还是二波，找对方向，做二波，图已经做好了，资金已经准备好了，就等方向切过来
            *、指数不跌了就大胆干，指数不好，趋势没戏，退潮期，不要盲目大仓位去做
        目标：
            *、资金总是往前排切，往低位切，所以前排和低位才是安全的，所以目标要么前排核心，要么低位首板
    """
    doc.add_page_break()
    doc.add_paragraph(he_xin)

    save_dui(doc)

    doc.save('result/复盘.docx')

    save_tj(doc)
    save_js(doc)
    save_gz(doc)


def save_sc(doc):
    # delete_paragraph(doc)
    doc.add_page_break()
    # 条件
    condition = ""
    for line in open("./市场2部分.txt").readlines():
        condition = condition + line

    doc.add_paragraph(condition)
    # doc.save('result/条件.docx')


def save_dui(doc):
    # delete_paragraph(doc)
    doc.add_page_break()
    # 条件
    condition = ""
    for line in open("每天计划.txt").readlines():
        condition = condition + line

    doc.add_paragraph(condition)
    # doc.save('result/条件.docx')


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
    bu_zhang_long = get_name_list("input/1-龙头属性.txt", [])
    lian_ban = get_name_list("input/2-连板情绪.txt", bu_zhang_long)
    filter_list = bu_zhang_long + lian_ban
    fu_pan = get_name_list("input/3-大盘核心.txt", filter_list)
    print("bu_zhang_long:", bu_zhang_long)
    print("lian_ban:", lian_ban)
    print("fu_pan:", fu_pan)

    return bu_zhang_long, lian_ban, bu_zhang_long + lian_ban + fu_pan


if __name__ == '__main__':

    # 获取个股代码
    get_code_map()

    # 获取题材涨停的个股
    bu_zhang_long, lian_ban, name_list = get_replay_name_list()
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
    save_word_text(bu_zhang_long, lian_ban, name_list, info_map, "A4")
