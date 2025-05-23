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
        "荣泰健康-断板日-20250328": 3,
        "荣泰健康-20250331": 4,
        "凯美特气-断板日-20250401": 4,
        "凯美特气-20250402": 5,
        "中旗新材-20250402": 3,
        "中旗新材-20250407": 4,
        "中旗新材-20250408": 5,
        "中旗新材-20250409": 6,
        "海鸥住工-20250410": 6,
        "国芳集团-20250411": 6,
        "泰慕士-20250415": 4,
        "泰慕士-20250416": 5,
        "泰慕士-20250417": 6,
        "国光连锁-20250418": 5,
    }
    draw_picture(data_map)
