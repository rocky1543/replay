import time

import akshare as ak
import tushare as ts
import requests
import json


def test1():
    # 获取东方财富网-沪深京 A 股-实时行情
    df = ak.stock_zh_a_spot_em()
    code_map = {}
    for index, row in df.iterrows():
        code_map[row["名称"].strip()] = {"代码": row["代码"].strip(), "涨跌幅": row["涨跌幅"]}
    print("code_map:", code_map)


def test2():
    data = "AMD合作+AI服务器+英伟达+印制电路板\n1、2023年7月4日在投资者互动平台表示， 公司有为英伟达和AMD提供相关产品的PCB配套，截至2023年第一季度，国外营收占比为64.15%。\n2、公司通过供应体系向英伟达提供PCB系列产品，正在积极参与英伟达R系列产品的打样和测试工作。对英伟达出货的主要是R系列产品。\n3、公司在服务器PCB领域布局较早，战略性布局了AI服务器和数据中心业务，在服务器PCB市场占比超20%，是海外龙头AWS供应商，为AWS供应400G及以下交换机PCB产品。\n4、公司已成为国内头部通信服务商多款5G基站产品的主力供应商，已有6G技术储备。\n5、公司主要从事高精密印制电路板的研产销。公司为品牌服务器/数据中心和ODM/OEM厂商提供优质产品。"
    data_arr = data.split("\n", 1)
    print(data_arr)


def test3():
    df = ak.stock_zh_a_spot_em()
    # ak.stock_zh_a_close()

    code_map = {}
    code_list = []
    for index, row in df.iterrows():
        code_map[row["名称"].strip()] = {"代码": row["代码"].strip(), "最高": row["最高"]}
        code_list.append(row["代码"].strip())
    print("code_map:", code_map)
    print("code_list:", code_list)
    print("code_list_len:", len(code_list))

    sz_high_price_day = ["20230828", "20231121", "20231229"]

    start_time = int(time.time() * 1000)
    for i, code in enumerate(code_list[:30]):
        print("code:", code)
        if i % 100 == 0:
            print("count:", i)
            print("use_time:", (int(time.time() * 1000) - start_time))

        hist_df = ak.stock_zh_a_hist(symbol="002176", start_date='20280828', end_date='20240121')
        high_price_list = []
        sz_hp_day_price_list = []
        print("hist_df:", hist_df)
        for index, row in hist_df.iterrows():
            print("index:", index)
            print("row:", row)
            high_price_list.append(row["最高"])

        print("high_price_list:", high_price_list)


def test4():
    # 设置Tushare接口的token，你需要先在Tushare官网注册并获取token
    ts.set_token('087c527f2572b83dd1a7ce2e101c8a45c56101df1652b3ca928bfe3b')

    # 初始化Tushare接口
    pro = ts.pro_api()

    # 获取指定日期的A股收盘数据
    date = '20230620'  # 指定日期
    df = pro.daily(trade_date=date)

    # 输出获取到的收盘数据
    print(df)
    # 将DataFrame保存为CSV文件
    df.to_csv('output.csv')


def test5():
    import requests

    # API密钥
    api_key = "your_api_key"

    def get_data(url):
        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': url,
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }

        response = requests.get(url, headers=headers)
        data = json.loads(response.text)

        return data

    # 示例URL
    example_url = "http://www.ths.com.cn/"
    result = get_data(example_url)
    print(result)


def test6():
    lian_ban_map = {}
    for line in open("input/2-连板情绪.txt"):
        data = line.split("\t")
        # print("data:", data)
        name = data[0].strip()
        ban_num = data[-1].strip()

        lian_ban_list = lian_ban_map.get(ban_num, [])
        lian_ban_list.append(name)
        lian_ban_map[ban_num] = lian_ban_list

    lian_ban_data = []
    for key, val in lian_ban_map.items():
        lian_ban_data.append("{}板: {}".format(key, ",".join(val)))
    print("lian_ban_data:", lian_ban_data)


def test7():
    from selenium import webdriver
    driver = webdriver.Chrome()
    driver.get("https://www.jiuyangongshe.com/search/new?k=%E6%A2%A6%E7%BD%91%E7%A7%91%E6%8A%80&type=5")

    # 设置隐式等待时间为 10 秒
    driver.implicitly_wait(1)

    # 获取页面内容
    page_source = driver.page_source
    print("page_source_111:", page_source)
    driver.quit()


def test8():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # 启动浏览器（以 Chromium 为例）
        browser = p.chromium.launch()
        page = browser.new_page()

        # 打开目标网页
        page.goto("https://www.jiuyangongshe.com/search/new?k=%E6%A2%A6%E7%BD%91%E7%A7%91%E6%8A%80&type=5")

        # 等待页面加载完成（例如等待某个特定元素出现）
        page.wait_for_selector("#target-element-id")  # 替换为目标元素的选择器

        # 获取页面内容
        content = page.content()
        print("content：", content)
        browser.close()
        return content


def test9():
    import numpy as np
    import matplotlib.pyplot as plt

    # 创建数据
    x = np.linspace(-4 * np.pi, 6 * np.pi, 1000)
    y = np.sin(x) + (np.sin(3 * x)) / 3 + (np.sin(5 * x)) / 5

    # 创建图形
    plt.figure(figsize=(10, 6))

    # 绘制曲线
    plt.plot(x, y, label=r'$\sin(x) + \frac{\sin(3x)}{3} + \frac{\sin(5x)}{5}$', color='#FF6B68')

    # 设置坐标轴
    plt.xlim(-2 * np.pi, 6 * np.pi)
    plt.ylim(-2, 2)

    # 添加图例
    plt.legend()

    # 显示图形
    plt.show()


if __name__ == '__main__':
    test9()
