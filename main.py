import akshare as ak


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


if __name__ == '__main__':
    test2()
