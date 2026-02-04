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
from docx.shared import Inches
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
*、一个简单的高抛低吸游戏而已，为什么玩不赢呢，只有情绪的高低，情绪起始，以下东西才有意义
*、我现在才明白，我为什么发挥不了降魔者的能力，是因为我一直都带着贪婪和恐惧
*、第一天很重要：
    *、炒股炒的是情绪，只看情绪：风来了，情绪就来了，情绪来了，人就聚集了，买盘就汹涌澎湃了
    *、这一段情绪，时机只有2个：这段情绪开始的第一天低位，龙头确认给机会的第一天
    *、这段情绪起来了，就好做了，核心是谁，能不能做，能不能封板
    *、就像一团火，燃烧得很快，很旺，你要做的是，在第一时间参与进去，尽量参与到每一段情绪的起始
    *、每一次大的连板，是市场一段一致的情绪，高位放量，有人恐高看空，这段一致情绪就很难延续了
    *、你要判断的是这段一致情绪什么时候，在哪里发生，然后尽量在起始阶段参与进去
    *、龙头二波，接力，全都靠子子孙孙回流，子子孙孙回流，说明板块资金回流
    *、龙头，子子孙孙都一致了，需要躲一下，每次情绪兴奋，高潮的时候，就是悲剧的开始
    *、情绪高潮，行情基本到头了，很难再有形成这段情绪的条件，这个时候暴跌，习惯性低吸是亏钱的最大原因
    *、只要他的子子孙孙还在活跃，就能超跌低吸，二波，接力；子子孙孙死的死，伤的伤，那就结束了
    *、九阳神功：动于阴末，止于阳极，板块主升，托举龙头主升，这才是是正解
    *、交易的本质就是资金讲故事，然后吸引来一大批人，社会讨论度决定板块地位，资金活跃度决定龙头地位
*、人气 = 社会讨论度 + 资金活跃度
    *、二波关键词：连板，横盘，辨识度，人气非常足，天然合力，方向核心，量价完美，风韵犹存，位置夹在中间
    *、连板情绪龙头就一个，一股之下皆是跟风小弟，要把精力放在最核心的那只灵魂股身上
    *、打板只有三种：首板，接力，二波
*、大数定律
    *、赚多出的钱它也会亏回去，亏多出的钱它也会再赚回来，均值是会回归的
    *、去掉概率低的，保留概率高的，提升每一次出手的概率，当操作足够多的时候，盈利就会回归到均值上
    *、巨大的结果只需要日积月累的微小力量
    *、外重者内拙
        *、徒弟：师父，以我的资质，开悟需要多久？师父：十年
        *、徒弟：如果我加倍苦修呢？师父：二十年
        *、徒弟：如果我夜以继日，不休不眠呢？师父：那你将永无开悟之日
*、龙头：
    *、人气就是龙的魂，一切形态随着魂而动，人气可以通过观察子子孙孙活力而得
    *、高度不一定是龙头，但能带动板块和市场情绪，有人气、辨识度、流动性收敛的地方肯定是龙头
    *、当下谁最强，最猛，人气最旺，最吸金，就是最优解，就好比居庸关的人气和八达岭就没法比
    *、龙头就是主升退潮和指数&情绪拟合的个股，是板块的脊梁，龙头拟合板块指数，板块指数拟合情绪
    *、龙头把板块带起来，补涨就可以套利
    *、情绪周期龙：
        *、每个阶段只有一只票，和连板情绪拟合的高标，他起落和连板情绪【起落同步】，高标要把独苗去掉
    *、主线板块龙：
        *、大龙头支撑板块脊梁，小周期龙头领涨板块，子子孙孙带来活力
        *、他的主升退潮几乎拟合该方向的主升退潮，他跟着板块指数走，板块指数也跟着他走
    *、人气是龙头的基石：
        *、虹吸效应：强的东西给机会，会吸干地位于他的标的的人气，资金，流动性
        *、束水攻沙：打造高标，维持高标在高位强势需要大量的资金，资金需要收敛，凝聚到一个点
    *、相：
        *、叫她不凶，她心中已有凶相，而能做到和善，是对凶的克制，是戒
        *、而叫她和善，她心中已有和善之相，她和善只是顺其自然
*、简单过程：
    *、一波潮水起，几个股领涨，然后潮水褪去，随机死去一批，剩下三三两两
    *、然后一波潮水又起，几个股领涨，其中一两个辨识度更高一些，然后潮水褪去，随机又死一批
    *、如此往复，每次要找潮水褪去谁命最硬，潮水起来谁地位最高 
*、光神：
    *、退潮的结果就是重新洗牌，推到重来，筛选掉一部分，保留一部分
    *、研究市场情绪的意义就在于如何让自己参与到每一波行情的起始
    *、再爆炸的行情，最多也就是三五天，螺旋式前进是必然规律，连续加速后就避开一下
    *、当最勇敢的资金有90%被割肉出来的时候，又构成了一个新的起点，开始新的游戏，周而复始
    *、在高潮中永远抱着敬畏的心态，在绝望中永远要充满希望，市场很差很差的时候，开始孕育新龙头
    *、当阶段见顶的时候，市场就进入了困难模式，在这种模式之下，你做的越多，错的越多
*、92科比：
    *、要么做高，要么做低，要么切换，人气在哪就去哪儿找机会
    *、接力的核心就是人气，龙头自身要有人气，板块要有人气，子子孙孙要有活力
*、群总：
    *、你能团结多少人，你就能干多少事，人气所在，牛股所在，流动性产生溢价
    *、研究这研究那有个毛用，要么空仓，要么核心
*、杂文：
    *、就跟打游戏一样，别人的技能没放完，你就贸然出击不就是找死嘛
    *、任何事物都像那一朵花，盛夏开得再灿烂，夏天过去的时候，都会凋零落到地里
    *、人的一切执念都是源自于对有的追求，有求于外者内拙
    *、没有稳定的系统，只有稳定的人，就像小时候养的小鸡小鸟，过度的关心它，反而会把它弄死
    *、搞懂解决什么具体问题，影响多少人，影响多少钱
    *、为什么小米值那么多钱？是因为智能手机市场值那么多钱，这是多大的市场
    *、你看到一个壮汉很高大，很强壮，其实他已经开始变老了，爆涨过的题材再无高度
*、行情好的时候多做，行情不好的时候少做：之前我认为的行情好，已经是高潮了
    *、行情好：大题材，大主流，大容量，梯队完整，主线清新，有高度，高度有硬度，高位有人气
    *、多做：对的时间做对的事情，在大周期里有节奏的做小周期，大行情=有高度有宽度
*、方法论：
    *、做【首板】就是看高做低，高位拉出空间，【龙头】就是做二板之上谁最有人气，低位小弟会奶他
    *、龙头：班级学霸；补涨龙=大题材里，高低切；补涨=大题材里，看高做低;补涨=跟风=蹭热度
    *、一轮行情的流程：1、龙头上涨；2、龙头补涨；3、题材切换
老师：
    *、复盘看看当天炒什么题材，再看看有没有可能二波的
    *、盘中看看今天炒什么题材，看看有没有【首板】可能二波的
    *、老师主要做的还是二波，找对方向，做二波，图已经做好了，资金已经准备好了，就等方向切过来
养家：
    *、观察赚钱效应：观察人气回流的过程，观察亏钱效应：观察人气消散的过程
    *、整个循环：低位的赚钱，慢慢延伸到高位赚钱，然后高位出现亏钱，再回到低位，高低位都亏钱
    *、除了补涨是眼红效应，跟风大哥一起涨，补涨龙，切换都是一个自然循环，都是高位到头回到低位
    *、爆炸的赚钱效应 = 爆炸的亏钱效应
*、指数：
    *、作用是预判大环境【亏钱效应】和【赚钱效应】，市场不好，题材也走不高
    *、高位靠低位奶，大盘推板块向上，板块推龙头向上，这种向上的力是最强的
情绪周期：
    *、核心思想【他带起的情绪】，切有很多子子孙孙追随他，奶他
    *、在大龙头倒下的时候，退潮强大的亏钱效应，会将带有"高位"属性的票冲得溃不成军
    *、水太烫了，水倒下来的时候，啥都顶不住，退潮的时候，高位的都要跌，他们的属性就是"高"
目标：
    *、资金总是往前排切，往低位切，所以前排和低位才是安全的，所以目标要么前排核心，要么低位首板
    *、高位一定要做前排，不然死的时候出不来，只有大跌后和大涨回调后是安全的，一定要删除，简化到可以落地
    """
    doc.add_page_break()
    doc.add_paragraph(he_xin)

    save_dui(doc)

    # 方法三：同时设置宽高（保持比例）
    doc.add_picture('./市场资金潮汐.jpg', width=Inches(4.5))
    # doc.add_picture('./市场资金潮汐.jpg', width=Inches(3), height=Inches(2))
    # doc.add_picture('./市场资金潮汐.jpg')

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
