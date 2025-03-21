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


if __name__ == '__main__':
    # 数据
    data_map = {
        "华丰股份-断板-20250228": 6,
        "恒为科技-20250229": 4,
        "天正电气-20250304": 4,
        "天正电气-20250305": 5,
        "云鼎-宁水-20250306": 4,
        "云鼎科技-20250307": 5,
        "信隆健康-断板日-20250310": 5,
        "信隆健康-20250311": 6,
        "信隆健康-20250312": 7,
        "信隆健康-20250313": 8,
        "信隆健康-断板日-20250314": 9,
        "明牌珠宝-20250317": 5,
        "明牌珠宝-20250318": 6,
        "奇精机械-20250319": 6,
        "奇精机械-20250320": 7,
    }
    draw_picture(data_map)
