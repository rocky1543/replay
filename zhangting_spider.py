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


def save_word_text(lian_ban, name_list, info_map, print_type="A5"):
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

        if key not in lian_ban and add_he_xin_split:
            add_he_xin_split = False
            doc.add_paragraph("- " * 90)

        # 添加标题，0表示样式为title
        h1 = doc.add_heading(key, level=2)
        h1.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # 添加段落
        doc.add_paragraph(title + "\n" + info + "\n\n" + ti_cai_text + "\n")

    # 核心
    he_xin = """
    *、第一天很重要，第二天情绪要能续上
    *、先求势，再求利，先找方向，再考虑这个方向能不能起
        *、板块主升，托举龙头主升，这才是是正解
        *、社会讨论度决定板块地位，资金活跃度决定龙头地位，板块讨论度带来的资金流动性会把龙头托举起来
    *、人气 = 社会讨论度 + 资金活跃度
        *、二波前面的连板，是为了看谁更有辨识度，谁更有人气，再来一波的时候盯着最有人气的东西看机会
        *、知道的，讨论的，关注的，参与交易的人越多，物品越好交易，也就是物品越好流动
        *、龙头就是人气资金流动性最强的地方，连续加速后就避开一下，筹码交换的好，再就继续猛干
        *、市场萧条的时候，只要有一个强，大家都看得见，这个时候的人气聚集效应非常好，市场差人气更容易聚焦
        *、市场好时大家都强，一眼望过去不知道谁最强，就像一桶水倒地上，地上水很多，却也很分散，没有激流之劲
        *、一个好的行情就是让低吸的人赚钱，打板的人赚钱，做龙头的人赚钱
        *、这两天缩量6000亿，好多人都不玩了，第二天谁来帮你接力
        *、热点效应本身就是趋势，会有人多少产生兴趣冲进去，兴趣消退而出来，直到整个热点散去，从而趋势退去
        *、热点要新才能一下子吸引来很多人，要有共鸣才有持续性
    *、买点的核心逻辑
        *、低价，钱多，大故事，低价+人气旺更从容
        *、市场最核心股就一个，一股之下皆是跟风小弟，要把精力放在最核心的那只灵魂股身上
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
    *、人气流动规律：
        *、从大到小：先看板块，例如水电强，会吸干机器人/算力的人气和资金
        *、最强的板块中自上而下
        *、总结：
            *、虹吸效应：强的东西给机会，会吸干地位于他的标的的人气，资金，流动性
            *、束水攻沙：打造高标，维持高标在高位强势需要大量的资金，资金需要收敛，凝聚到一个点
            *、高度不一定是龙头，但是人气、辨识度、流动性收敛的地方肯定是龙头
        *、越努力越菜
            *、急于求成，气急攻心，无间地狱，任何你放不下，想不开，静不了，去强求的事，都是德不配位而已
            *、人的一切执念都是源自于对有的追求，有求于外者内拙
            *、走不出来，好像也不会死，交易的本质是观察自己做交易
            *、外重者内拙，就像谈恋爱一样：
                *、人越好，越在乎，越僵硬，越木讷，越傻逼，越像个二愣子
                *、人越渣，越不在乎，谈得越轻松自在，发挥出色，如鱼得水
            *、何为悟道：外重者内拙，有些东西越想越执着，越执着越笨拙，若执着于它，就很难走出来
            *、唯一评判的标准就是：我若执着于它，我就不能做好
        *、相：
            *、叫她不凶，她心中已有凶相，而能做到和善，是对凶的克制，是戒
            *、而叫她和善，她心中已有和善之相，她和善只是顺其自然
        *、面带点：
            *、大盘是大的面，板块是小的面，大面推小面向上，小面推点向上，这种向上的力是最强的
            *、以点带面，吸引资金进来，最终还需要面推点，加强上涨
        *、复盘逻辑：
            *、搞懂解决什么具体问题，影响多少人，影响多少钱，你们知道为什么小米值那么多钱吗？
            *、是因为智能手机市场值那么多钱，全球都在换智能手机，你从这个角度看，这是多大的市场
            *、中国的企业家之所以能挣到钱：1、中国足够大；2、中国足够穷
        *、大哥：
            *、有比你猛的东西在高举高打，有比你强的东西在吸金，你现在起来算什么，跟风吗
            *、你之前再牛逼，现在有比你强的东西，你依然只能臣服他人脚下
            *、当下谁最强，最猛，人气最旺，最吸金，就是最优解，就好比居庸关的人气和八达岭就没法比
        *、市场就两个过程：
            *、整体上升：有明确的板块引领板块市场
                *、只看最强的，其他当强不强，都是垃圾，去看哪个板块主升，推动哪个龙头最强（帝王）
                *、其他皆为跟风，没有地位（臣子）
            *、整体下降：市场推倒从来
                *、新方向：去看哪个板块主升，推动哪个龙头最强
                *、老核心：只看最抗跌的，当弱不弱就是好东西
            *、第一天很重要：
                *、转折向下：今天的硬板，明天可能被板块整体回落拉下马
                *、转折向上：今天的烂板，明天可能被板块整体上升推起来
            *、总结：市场就两个过程起和落，起的时候谁最猛，跌的时候谁最扛揍
            *、简单过程：
                *、一波潮水起， abcde领涨，然后潮水褪去，随机死去一批，剩下三三两两，如def
                *、然后一波潮水又起，defhy领涨，其中def辨识度更高一些
                *、然后潮水褪去，随机又死一批，剩下fh
                *、如此往复，每次要找潮水褪去谁命最硬，潮水起来谁地位最高 
        *、趋势：1、趋势向上：上升猛烈，下降温和；2、趋势向下：下降猛烈，上升温和
        *、每天：
            *、市场有没有大跌的风险，如果没有，你弄的东西是不是最强板块中最强的人气标的
            *、任何事物都像那一朵花，盛夏开得再灿烂，夏天过去的时候，都会凋零落到地里，题材如此，风口也如此
        *、光神：
            *、退潮的结果就是重新洗牌，推到重来，筛选掉一部分，保留一部分
            *、研究市场情绪的意义就在于如何让自己参与到每一波行情的起始
            *、再爆炸的行情，最多也就是三五天，螺旋式前进是必然规律
            *、当最勇敢的资金有90%被割肉出来的时候，又构成了一个新的起点，开始新的游戏，周而复始
            *、在高潮中永远抱着敬畏的心态，在绝望中永远要充满希望
            *、总结：市场永远是走N行结构
        *、杂文：
            *、高潮：有很多人已经赚了很多了，如果不是第一天，很多做短的人都要出来
            *、上涨的第一天大胆弄，第二天小心弄，第三天谨慎弄
            *、下跌的第一天谨慎弄，第二天小心弄，第三天大胆弄
            *、小涨小跌，大涨大跌，努力避开大跌
            *、只是一个闯关游戏，生活该干嘛干嘛，一事顺事事顺
            *、情绪变化永远落后于价格变化，农民需要等到春天来的时候才种地，这就是规律
            *、伟大就是重复的事情做一万次，没有天赋，那就重复
            *、就一句话：希望明天大盘好，市场好，把它带上去
            *、记录情绪变化，记录大盘为什么涨，为什么跌，这样才能知道发生了什么，长期记录才能发现规律
            *、思考的时候，也要先大后小，再自上而下
            *、就跟打游戏一样，别人的技能没放完，你就贸然出击不就是找死嘛
            *、市场一直重复着从安静到沸腾，再从沸腾到安静的过程，所以所有的买点应该都是在市场安静的时候
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
    lian_ban = get_name_list("input/连板股.txt", [])
    fu_pan = get_name_list("./input/复盘股.txt", lian_ban)
    print("lian_ban:", lian_ban)
    print("fu_pan:", fu_pan)

    return lian_ban, lian_ban + fu_pan


if __name__ == '__main__':

    # 获取个股代码
    get_code_map()

    # 获取题材涨停的个股
    lian_ban, name_list = get_replay_name_list()
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
    save_word_text(lian_ban, name_list, info_map, "A4")
