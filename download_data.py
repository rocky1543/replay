import time

import akshare as ak
import tushare as ts


def download_data():
    # 设置Tushare接口的token，你需要先在Tushare官网注册并获取token
    ts.set_token('087c527f2572b83dd1a7ce2e101c8a45c56101df1652b3ca928bfe3b')

    # 初始化Tushare接口
    pro = ts.pro_api()

    day_list = get_day_list()
    for date in day_list[:1]:
        # 获取指定日期的A股收盘数据
        df = pro.daily(trade_date=date)

        # 输出获取到的收盘数据
        print(df)
        # 将DataFrame保存为CSV文件
        df.to_csv('./close_data/收盘数据-{}.csv'.format(date))


def get_day_list():
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    # 起始日期和结束日期
    start_date = datetime.strptime('20230828', '%Y%m%d')
    end_date = datetime.strptime('20240102', '%Y%m%d')

    # 获取日期列表
    date_list = [start_date + relativedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]

    # 输出日期列表
    date_str_list = []
    for date in date_list:
        date_str_list.append(date.strftime('%Y%m%d'))
    return date_str_list


if __name__ == '__main__':
    download_data()
