import fnmatch
import json
import os

import akshare as ak
import pandas as pd


def load_data(sz_high_price_day):
    file_list = get_files_in_directory(sz_high_price_day)

    all_date_data = {}
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
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "pct_chg": row["pct_chg"]
            }
            all_date_data[ts_code] = each_date_data

    return all_date_data


def get_files_in_directory(sz_high_price_day):
    # 获取目录下的所有文件和子目录
    all_items = os.listdir("./close_data")

    # 过滤出文件
    files = [item for item in all_items if fnmatch.fnmatch(item, '*.csv')]

    # 过滤出上证高点的几个交易日数据
    sz_high_price_day_file = []
    for file in files:
        file_date = file.split("-")[1].split(".")[0]
        if file_date in sz_high_price_day:
            sz_high_price_day_file.append(file)

    print("sz_high_price_day_file:", sz_high_price_day_file)

    # 取最近15个交易日的数据

    files.sort(reverse=True)
    print("all_files:", files)
    print("all_files_len:", len(files))

    select_file = files[:15]

    for file in sz_high_price_day_file:
        if file not in select_file:
            select_file.append(file)

    select_file = list(set(select_file))
    select_file.sort(reverse=True)
    print("select_files:", select_file)
    print("select_files_len:", len(select_file))

    return select_file


def select_lian_xu_zhang_ting(lian_ban_num):
    all_date_data = load_data([])
    select_code_list = []
    for code, data in all_date_data.items():
        if len(data) < 5:
            continue
        if str(code).startswith("8"):
            continue
        # if code != "002146":
        #     continue

        data = sorted(data.items(), key=lambda x: x[0])
        print("--" * 50)
        print("code:", code)
        print("code_data:", data)

        true_list = []
        for date, values in data:
            high = values.get("high", None)
            close = values.get("close", None)
            pct_chg = values.get("pct_chg", None)
            print("date:", date)
            print("high:", high)
            print("close:", close)
            print("pct_chg:", pct_chg)
            if high == close and pct_chg > 9:
                true_list.append(1)
                if len(true_list) >= lian_ban_num:
                    select_code_list.append(code)
                    break
            else:
                true_list = []

    print("select_code_list:", select_code_list)
    print("select_code_list_len:", len(select_code_list))

    code_map = get_code_map()
    name_code_map = {}
    f = open("./result/连板股.txt", "w")

    result_code_list = []
    for code in select_code_list:
        code_info = code_map.get(code, {})
        name = code_info.get("名称", "")
        if name.count("ST") > 0:
            continue
        name_code_map[name] = code
        result_code_list.append(code)

    f.write(",".join(result_code_list))
    f.flush()
    print("name_code_map:", name_code_map)


def select_ge_gu(sz_high_price_day):
    all_date_data = load_data(sz_high_price_day)
    result = {}
    for code, data in all_date_data.items():
        print("--" * 50)
        print("code:", code)
        print("code_data:", data)
        if str(code).startswith("8"):
            continue

        high_price_list = []
        sz_hp_day_price_list = []
        for date, values in data.items():
            high = values.get("high", None)
            print("date:", date)
            print("values:", values)
            print("high:", high)
            if not high:
                continue

            high_price_list.append(high)
            if str(date) in sz_high_price_day:
                sz_hp_day_price_list.append(high)

        score = 0
        if len(high_price_list) > 5:
            high_price_avg = average(high_price_list)
            sz_hp_day_price_avg = high_price_avg
            if len(sz_hp_day_price_list) > 0:
                sz_hp_day_price_avg = average(sz_hp_day_price_list)

            if high_price_avg > sz_hp_day_price_avg:
                score = (high_price_avg - sz_hp_day_price_avg) / sz_hp_day_price_avg

                score = round(score, 1)
                if score > 0:
                    result[code] = score

        print("high_price_list:", high_price_list)
        print("sz_hp_day_price_list:", sz_hp_day_price_list)
        print("high_price_avg:", high_price_avg)
        print("sz_hp_day_price_avg:", sz_hp_day_price_avg)
        print("score:", score)
        print("--" * 50)

    result = sorted(result.items(), key=lambda item: item[1], reverse=True)
    print("result:", result)
    print("resul_len:", len(result))

    code_map = get_code_map()
    f = open("./result/强势股.txt", "w")
    name_list = []
    name_code_map = {}
    code_list = []
    for val in result:
        code_info = code_map.get(val[0], {})
        name = code_info.get("名称", "")
        if name.count("ST") > 0:
            continue
        name_list.append(name)
        code_list.append(val[0])

        name_code_map[name] = val[0]

    f.write(",".join(code_list))
    f.flush()

    print("name_code_map:", name_code_map)
    print("name_code_map_len:", len(name_code_map))
    return name_list


def average(numbers):
    return sum(numbers) / len(numbers)


def get_code_map():
    # 获取东方财富网-沪深京 A 股-实时行情
    code_map = {}
    df = ak.stock_zh_a_spot_em()
    for index, row in df.iterrows():
        code_map[row["代码"].strip()] = {"名称": row["名称"].strip(), "代码": row["代码"].strip()}
    return code_map


if __name__ == '__main__':
    sz_high_price_day = ["20230828", "20231121", "20231229"]
    # select_list = select_ge_gu(sz_high_price_day)

    # 最近15天的连板数量
    lian_ban_num = 3
    select_lian_xu_zhang_ting(lian_ban_num)
    # print("select_list:", select_list)
    # print("select_list_len:", len(select_list))
