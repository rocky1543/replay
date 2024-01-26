import tushare as ts


def download_data(start_day, end_day):
    # 设置Tushare接口的token，你需要先在Tushare官网注册并获取token
    ts.set_token('087c527f2572b83dd1a7ce2e101c8a45c56101df1652b3ca928bfe3b')

    # 初始化Tushare接口
    pro = ts.pro_api()

    day_list = get_day_list(start_day, end_day)
    for date in day_list:
        print("download_data_day:", date)
        # 获取指定日期的A股收盘数据
        df = pro.daily(trade_date=date)

        if len(df) > 100:
            # 将DataFrame保存为CSV文件
            df.to_csv('./close_data/收盘数据-{}.csv'.format(date))


def get_day_list(start_day, end_day):
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    # 起始日期和结束日期
    start_date = datetime.strptime(start_day, '%Y%m%d')
    end_date = datetime.strptime(end_day, '%Y%m%d')

    # 获取日期列表
    date_list = [start_date + relativedelta(days=i) for i in range(0, (end_date - start_date).days + 1)]

    # 输出日期列表
    date_str_list = []
    for date in date_list:
        date_str_list.append(date.strftime('%Y%m%d'))
    return date_str_list


if __name__ == '__main__':
    start_day = "20240116"
    end_day = "20240123"
    download_data(start_day, end_day)
