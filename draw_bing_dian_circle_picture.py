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
    shang_zhang_jia_shu = []
    da_rou = []
    da_mian = []
    da_zhou_qi = []
    xiao_zhou_qi = []

    for data in data_list:
        dates.append(data.get("date") + "\n" + data.get("zui_gao"))
        shang_zhang_jia_shu.append(data.get("shang_zhang_jia_shu"))
        da_rou.append(data.get("da_rou_count"))
        da_mian.append(data.get("da_mian_count"))
        da_zhou_qi.append(data.get("da_zhou_qi_zui_gao_ban"))
        xiao_zhou_qi.append(data.get("xiao_zhou_qi_zui_gao_ban"))

    # 创建图形和轴
    fig, ax = plt.subplots()

    # 周期连板数据放大
    shang_zhang_jia_shu_min = [val / 35.0 for val in shang_zhang_jia_shu]
    da_zhou_qi_max = [val * 10 for val in da_zhou_qi]
    xiao_zhou_qi_max = [val * 10 for val in xiao_zhou_qi]

    # 绘制数据
    ax.plot(dates, da_mian, label='大面(>-10%)', color='cyan')
    ax.plot(dates, da_rou, label='大肉(>+10%)', color='magenta')
    ax.plot(dates, shang_zhang_jia_shu_min, label='上涨家数', color='blue')
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
    for i, txt in enumerate(shang_zhang_jia_shu):
        ax.annotate(txt, (dates[i], shang_zhang_jia_shu_min[i]), textcoords="offset points", xytext=(0, 10),
                    ha='center')

    # 设置图例
    ax.legend()

    # 设置 y 轴范围，向上留出空间
    max_value = max(max(da_mian), max(da_rou), max(da_zhou_qi_max), max(xiao_zhou_qi_max),
                    max(shang_zhang_jia_shu_min)) + 30
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
            "shang_zhang_jia_shu": 1494,
            "da_rou_count": 47,
            "da_mian_count": 11,
            "da_zhou_qi_zui_gao_ban": 8,
            "xiao_zhou_qi_zui_gao_ban": 8,
        }, {
            "date": "20250314",
            "zui_gao": "信隆健康",
            "shang_zhang_jia_shu": 4495,
            "da_rou_count": 109,
            "da_mian_count": 6,
            "da_zhou_qi_zui_gao_ban": 9,
            "xiao_zhou_qi_zui_gao_ban": 9,
        }, {
            "date": "20250317",
            "zui_gao": "明牌珠宝",
            "shang_zhang_jia_shu": 3146,
            "da_rou_count": 83,
            "da_mian_count": 3,
            "da_zhou_qi_zui_gao_ban": 9,
            "xiao_zhou_qi_zui_gao_ban": 5,
        }, {
            "date": "20250318",
            "zui_gao": "明牌珠宝",
            "shang_zhang_jia_shu": 2985,
            "da_rou_count": 84,
            "da_mian_count": 4,
            "da_zhou_qi_zui_gao_ban": 9,
            "xiao_zhou_qi_zui_gao_ban": 6,
        }
    ]

    """
    市场冰点条件：
        *、高度降至1‐3板，就进入冰点范畴，高度越低越冰
        *、2板及以下的绝对冰点范畴
        *、有一波8板及以上的大行情结束，那紧接着高度大致降到4板就是资金试错位置
        *、涨停超百家、大肉单日超近一周均值一倍，基本进入高潮范畴
        *、大肉单日跌至近一周均值的一半，基本进入冰点范畴
        *、已连续分歧3天左右，跌停超20家，大面超35家，基本就接近左侧试错的冰点范畴
        *、连板数降至 15 只以下，进入冰点或混沌范畴
        *、买点是：冰点 → 混沌期（有时没有）→启动期→主升期
        例子：
        1、在20210922，大肉（作为判断是否高潮的重要指标），直接来到了120家+，直接高潮日。
        2、之后，大面数量从20210923到20210927，连续大幅释放了三日，此阶段，谁打板、接力，任何手法，胜率降低，基本都是大亏米。
        3、20210927大面数量直接达到80家+，叠加盘中可见连板高度下降至2板、上涨家数小于900家，妥妥绝对冰点
        4、20210927日内午后逆势的最高板2板，就有破冰试错价值
        5、20210929日市场自然大分歧，大面又上升到60家+，上涨家数更是仅不到500家，市场几乎全部下跌，恐慌严重，综合下来，20210929再次绝对冰点
    """

    draw_bing_dian_circle_picture(data_map)
