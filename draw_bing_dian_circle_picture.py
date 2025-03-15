import platform

import matplotlib
import matplotlib.pyplot as plt

# 动态设置字体
if platform.system() == "Windows":
    matplotlib.rcParams['font.family'] = 'SimHei'
elif platform.system() == "Linux":
    matplotlib.rcParams['font.family'] = 'SimHei'
else:  # macOS
    matplotlib.rcParams['font.family'] = 'Songti SC'

# 解决负号显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False


def draw_bing_dian_circle_picture(data_list):
    dates = []

    # 数据
    da_rou = []
    da_mian = []
    da_zhou_qi = []
    xiao_zhou_qi = []

    for data in data_list:
        dates.append(data.get("date") + "\n" + data.get("zui_gao"))
        da_rou.append(data.get("da_rou_count"))
        da_mian.append(data.get("da_mian_count"))
        da_zhou_qi.append(data.get("da_zhou_qi_zui_gao_ban"))
        xiao_zhou_qi.append(data.get("xiao_zhou_qi_zui_gao_ban"))

    # 创建图形和轴
    fig, ax = plt.subplots()

    # 周期连板数据放大
    da_zhou_qi_max = [val * 12 for val in da_zhou_qi]
    xiao_zhou_qi_max = [val * 12 for val in xiao_zhou_qi]

    # 绘制数据
    ax.plot(dates, da_mian, label='大面(>-10%)', color='cyan')
    ax.plot(dates, da_rou, label='大肉(>+10%)', color='magenta')
    ax.plot(dates, da_zhou_qi_max, label='大周期(上一个最高板)', color='orange')
    ax.plot(dates, xiao_zhou_qi_max, label='小周期(当日最高板)', color='purple', linestyle='--')

    # 在每个点上显示数值
    for i, txt in enumerate(da_mian):
        ax.annotate(txt, (dates[i], da_mian[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    for i, txt in enumerate(da_rou):
        ax.annotate(txt, (dates[i], da_rou[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    for i, txt in enumerate(da_zhou_qi):
        ax.annotate(txt, (dates[i], da_zhou_qi_max[i]), textcoords="offset points", xytext=(0, 10), ha='center')
    for i, txt in enumerate(xiao_zhou_qi):
        ax.annotate(txt, (dates[i], xiao_zhou_qi_max[i]), textcoords="offset points", xytext=(0, 10), ha='center')

    # 设置图例
    ax.legend()

    # 设置 y 轴范围，向上留出空间
    max_value = max(max(da_mian), max(da_rou), max(da_zhou_qi_max), max(xiao_zhou_qi_max)) + 30
    plt.ylim(0, max_value)
    plt.xlim(-1, len(da_mian) + 1)

    # 显示网格
    # ax.grid(True)

    # 显示图形
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # 数据
    data_map = [
        {
            "date": "20250313",
            "zui_gao": "信隆健康",
            "da_rou_count": 47,
            "da_mian_count": 11,
            "da_zhou_qi_zui_gao_ban": 8,
            "xiao_zhou_qi_zui_gao_ban": 8,
        },{
            "date": "20250314",
            "zui_gao": "信隆健康",
            "da_rou_count": 109,
            "da_mian_count": 6,
            "da_zhou_qi_zui_gao_ban": 9,
            "xiao_zhou_qi_zui_gao_ban": 9,
        }
    ]

    draw_bing_dian_circle_picture(data_map)
