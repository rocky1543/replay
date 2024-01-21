import time

import akshare as ak
import tushare as ts
import requests

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
    data = {
        "username":"",
        "password":""
    }


if __name__ == '__main__':
    test4()
