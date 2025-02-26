import logging

import akshare as ak


def get_code():
    # 获取东方财富网-沪深京 A 股-实时行情
    code_map = {}
    df = ak.stock_zh_a_spot_em()
    for index, row in df.iterrows():
        code_map[row["名称"].strip()] = {"名称": row["名称"].strip(), "代码": row["代码"].strip()}

    code_list = []

    f = open("../result/股票代码.txt", "w")
    for name in open("./input/股票名称.txt").readlines():
        try:
            name = name.strip()
            code_info = code_map.get(name)
            print("name:", name)
            code = code_info.get("代码", "")
            code_list.append(code)

            f.write(code + "\n")
        except Exception as e:
            logging.info("异常")

    return code_list


if __name__ == '__main__':
    code_list = get_code()
    print("code_list:", len(code_list))
