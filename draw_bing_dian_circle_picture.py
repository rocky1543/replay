import matplotlib.pyplot as plt
import numpy as np
import platform
import matplotlib

# 动态设置字体
if platform.system() == "Windows":
    matplotlib.rcParams['font.family'] = 'SimHei'
elif platform.system() == "Linux":
    matplotlib.rcParams['font.family'] = 'SimHei'
else:  # macOS
    matplotlib.rcParams['font.family'] = 'Songti SC'

# 解决负号显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False


def draw_picture(data_map):
    date_list = list(data_map.keys())
    height_list = list(data_map.values())

    # 设置柱状图的宽度
    bar_width = 0.25

    # 设置每组数据的x轴位置
    r1 = np.arange(len(date_list))
    r2 = [x + bar_width for x in r1]

    # 绘制柱状图
    plt.bar(r2, height_list, color='#FF6B68', width=bar_width, edgecolor='grey', label='连板高度')

    # 添加标签和标题
    plt.xlabel('日期', fontweight='bold')
    plt.ylabel('连板高度', fontweight='bold')
    plt.title('空间周期和时间周期')
    plt.xticks([r + bar_width for r in range(len(date_list))], date_list, rotation=35, ha='right')  # 旋转x轴标签避免重叠

    # 添加图例
    plt.legend()

    # 在柱状图上显示数值
    for i in range(len(date_list)):
        # 计算文本位置：在柱子顶部上方一点，在柱子高度的基础上增加5%的偏移量
        text_height = height_list[i] + max(height_list) * 0.05
        plt.text(r2[i], text_height, str(height_list[i]), ha='center', va='bottom', fontsize=9, color='black')

    # 设置 y 轴范围，向上留出空间
    max_value = max(height_list) + 3
    plt.ylim(0, max_value)
    plt.xlim(-0.2, len(date_list) + 1)

    # 显示图表
    plt.tight_layout()
    plt.show()


def draw_bing_dian_circle_picture():
    import matplotlib.pyplot as plt

    # 日期
    dates = [
        "2021/9/17\n红宝丽\n建业股份\n六国化工\n恒润股份",
        "2021/9/22\n红宝丽\n建业股份\n六国化工\n恒润股份",
        "2021/9/23\n广宇发展\n上海电力\n浙江新能\n中闽能源\n金开新能源\n内蒙华电",
        "2021/9/24\n广宇发展\n上海电力 浙江新能",
        "2021/9/27\n潍柴重机\n顺发恒业\n杭州热电\n闽东电力\n上柴股份\n良品铺子",
        "2021/9/28\n潍柴重机\n闽东电力",
        "2021/9/29\n闽东电力",
        "2021/9/30\n闽东电力",
        "2021/10/8\n国电南自"]

    # 数据
    da_mian = [24, 5, 35, 44, 88, 10, 63, 3, 25]
    da_rou = [68, 105, 75, 44, 50, 98, 22, 89, 75]
    da_zhouqi = [4, 4, 4, 4, 4, 4, 4, 5, 5]
    xiao_zhouqi = [3, 4, 3, 4, 2, 3, 4, 5, 3]

    # 公司名称
    companies = [
        "红宝丽\n建业股份\n六国化工\n恒润股份",
        "红宝丽\n建业股份",
        "广宇发展\n上海电力\n浙江新能\n中闽能源\n金开新能源\n内蒙华电",
        "广宇发展\n上海电力 浙江新能",
        "潍柴重机\n顺发恒业\n杭州热电\n闽东电力\n上柴股份\n良品铺子",
        "潍柴重机\n闽东电力",
        "闽东电力",
        "闽东电力",
        "国电南自"
    ]

    # 创建图形和轴
    fig, ax = plt.subplots()

    # 绘制数据
    da_mian_min = [val for val in da_mian]
    da_rou_min = [val for val in da_rou]
    da_zhouqi_max = [val * 12.0 for val in da_zhouqi]
    xiao_zhouqi_max = [val * 12.0 for val in xiao_zhouqi]
    ax.plot(dates, da_mian_min, label='大面', color='cyan')
    ax.plot(dates, da_rou_min, label='大肉', color='magenta')
    ax.plot(dates, da_zhouqi_max, label='大周期', color='orange')
    ax.plot(dates, xiao_zhouqi_max, label='小周期', color='purple', linestyle='--')

    # 在每个点上显示数值
    for i, txt in enumerate(da_mian):
        ax.annotate(txt, (dates[i], da_mian_min[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    for i, txt in enumerate(da_rou):
        ax.annotate(txt, (dates[i], da_rou_min[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    for i, txt in enumerate(da_zhouqi):
        ax.annotate(txt, (dates[i], da_zhouqi_max[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    for i, txt in enumerate(xiao_zhouqi):
        ax.annotate(txt, (dates[i], xiao_zhouqi_max[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    # 设置图例
    ax.legend()

    # 设置x轴刻度
    # plt.xticks(rotation=45)

    # 添加公司名称
    # for i, company in enumerate(companies):
    #     # 计算文本位置：在柱子顶部上方一点，在柱子高度的基础上增加5%的偏移量
    #     text_height = max(da_mian_min[i], da_rou_min[i], da_zhouqi[i], xiao_zhouqi[i]) + 15
    #     ax.text(i, text_height, company, ha='center', va='bottom', fontsize=8, color='black')

    # 设置 y 轴范围，向上留出空间
    max_value = max(max(da_mian_min), max(da_rou_min), max(da_zhouqi_max), max(xiao_zhouqi_max)) + 30
    plt.ylim(0, max_value)
    plt.xlim(-1, len(da_mian) + 1)

    # 显示网格
    # ax.grid(True)

    # 显示图形
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # 数据
    # data_map = {
    #     "新炬网络-20250209": 7,
    #     "新炬网络-20250210": 8,
    #     "新炬网络-20250211": 9,
    #     "新炬网络-20250212": 10,
    #     "梦网-杭钢-20250213": 7,
    #     "梦网-杭钢-20250214": 8,
    #     "杭钢股份-20250217": 9,
    #     "威派格-20250218": 6,
    #     "杭齿前进-20250219": 6,
    #     "杭齿前进-20250220": 7,
    #     "杭齿前进-20250221": 8,
    #     "新时达-20250224": 6,
    #     "卓翼科技-20250225": 5,
    #     "多个股pk-20250226": 4,
    #     "多个股pk-20250227": 5,
    #     "华丰股份-断板-20250228": 6,
    #     "恒为科技-20250229": 4,
    #     "天正电气-20250304": 4,
    #     "天正电气-20250305": 5,
    #     "云鼎-宁水-20250306": 4,
    #     "云鼎科技-20250307": 5,
    #     "信隆健康-断板日-20250310": 5,
    #     "信隆健康-20250311": 6,
    #     "信隆健康-20250312": 7,
    #     "信隆健康-20250313": 8,
    #     "信隆健康-20250314": 9,
    # }
    # draw_picture(data_map)

    draw_bing_dian_circle_picture()
