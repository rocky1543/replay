from datetime import datetime, timedelta

from download_data import download_data
from select_bu_zhang import get_files_in_directory
import pandas as pd
import akshare as ak

code_map = {}
all_date_data = {}


def get_code_map():
    # 获取东方财富网-沪深京 A 股-实时行情
    df = ak.stock_zh_a_spot_em()
    for index, row in df.iterrows():
        code_map[row["名称"].strip()] = {"代码": row["代码"].strip(), "涨跌幅": row["涨跌幅"]}


def download():
    start_day = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    end_day = datetime.now().strftime('%Y%m%d')
    print("start_day:", start_day)
    print("end_day:", end_day)
    download_data(start_day, end_day)

    get_code_map()


def get_all_date_data():
    file_list = get_files_in_directory()
    file_list = file_list[0:5]
    file_list.sort()
    print("file_list:", file_list)

    for file in file_list:
        print("load_file:", file)

        # 将DataFrame保存为CSV文件
        df = pd.read_csv('./close_data/{}'.format(file))

        for index, row in df.iterrows():
            trade_date = row["trade_date"]
            ts_code = row["ts_code"]
            ts_code = ts_code.split(".")[0]
            each_date_data = all_date_data.get(ts_code, {})

            each_date_data[trade_date] = {
                ts_code: ts_code,
                "amount": "{}亿".format(round(row["amount"] / 100000.0, 2))
            }
            all_date_data[ts_code] = each_date_data


def get_amount_info(name):
    code_info = code_map.get(name)
    code = code_info.get("代码")

    data = all_date_data.get(code)
    amount = ""
    for k, v in data.items():
        if not amount:
            amount = v.get("amount")
        else:
            amount = "{},{}".format(amount, v.get("amount"))
    return amount


def get_zhang_ting_list():
    name_list = []
    name_list_sub = []
    for line in open("./input/涨停.txt"):
        if line.strip():
            data = line.strip().split(",")
            name_list_sub.append(data[0])
        else:
            if len(name_list_sub) > 0:
                name_list.append(name_list_sub)
                name_list_sub = []

    if len(name_list_sub) > 0:
        name_list.append(name_list_sub)
    return name_list


if __name__ == '__main__':
    # 获取数据
    download()

    # 获取数据详情
    get_all_date_data()

    name_list = get_zhang_ting_list()
    print("name_list:", name_list)

    for name_list_sub in name_list:
        for name in name_list_sub:
            amount_info = get_amount_info(name)
            print("{}:{}".format(name, amount_info))
        print()
