from datetime import datetime, timedelta

from download_data import download_data
from select_bu_zhang import get_files_in_directory
import pandas as pd

if __name__ == '__main__':
    # 下载数据
    start_day = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    end_day = datetime.now().strftime('%Y%m%d')
    print("start_day:", start_day)
    print("end_day:", end_day)
    download_data(start_day, end_day)

    file_list = get_files_in_directory()

    file_list = file_list[0:7]

    print("file_list:", file_list)

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
                "pct_chg": row["pct_chg"],
                "amount": "{}亿".format(round(row["amount"] / 100000.0, 2))

            }
            all_date_data[ts_code] = each_date_data

    data = all_date_data.get("600686")
    amount = ""
    for k, v in data.items():
        print("k:", k)
        print("v:", v)
        if not amount:
            amount = v.get("amount")
        else:
            amount = "{},{}".format(amount, v.get("amount"))
    print("600639:", 600639)
    print("amount:", amount)
