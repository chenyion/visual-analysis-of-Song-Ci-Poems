import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 读取CSV文件
df = pd.read_csv('词牌数量统计.csv')

# 按数量降序排序
df_sorted = df.sort_values(by='数量', ascending=False)

# 提取前十名
top10 = df_sorted.head(10).copy()

# 创建柱形图
plt.figure(figsize=(12, 8))

# 使用更美观的渐变色
colors = plt.cm.viridis(np.linspace(0.2, 0.8, 10))

# 绘制柱状图
bars = plt.bar(top10['词牌'], top10['数量'], color=colors, edgecolor='grey')

# 设置标题和标签
plt.title('宋词十大词牌数量统计', fontsize=16, pad=20)
plt.xlabel('词牌名称', fontsize=12)
plt.ylabel('作品数量', fontsize=12)

# 旋转x轴标签
plt.xticks(rotation=45, ha='right', fontsize=10)

# 添加网格线
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 在柱子上方添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.annotate(f'{height}',
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha='center', va='bottom',
                fontsize=10)

# 添加背景信息
total = df['数量'].sum()
plt.figtext(0.5, 0.01,
            f"词牌总量: {len(df)}种 | 作品总量: {total}首 | 前十占比: {top10['数量'].sum()/total*100:.1f}%",
            ha="center", fontsize=11,
            bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.7))

# 调整布局
plt.tight_layout(rect=[0, 0.05, 1, 0.95])

# 保存并显示
plt.savefig('宋词十大词牌柱形图.png', dpi=300, bbox_inches='tight')
plt.show()


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'WenQuanYi Micro Hei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

# 读取CSV文件
df = pd.read_csv('词牌数量统计.csv')

# 按数量降序排序
df_sorted = df.sort_values(by='数量', ascending=False)

# 提取前十名
top10 = df_sorted.head(10).copy()

# 计算所有词牌的总数量
total = df['数量'].sum()

# 计算前十名的总数量
top10_total = top10['数量'].sum()

# 创建包含"其他"类别的数据
other_count = total - top10_total
other_row = pd.DataFrame({'词牌': ['其他'], '数量': [other_count]})
top10_with_other = pd.concat([top10, other_row])

# 计算占比
top10_with_other['占比'] = top10_with_other['数量'] / total * 100

# 设置颜色
colors = plt.cm.Set3(np.linspace(0, 1, 11))

# 创建饼图
plt.figure(figsize=(10, 10))

# 绘制饼图
wedges, texts, autotexts = plt.pie(
    top10_with_other['数量'],
    labels=top10_with_other['词牌'],
    autopct=lambda p: f'{p:.1f}%' if p > 3 else '',
    startangle=140,
    colors=colors,
    textprops={'fontsize': 10},
    wedgeprops={'edgecolor': 'w', 'linewidth': 1.5, 'linestyle': 'solid'},
    pctdistance=0.85
)

# 设置标题
plt.title('宋词词牌分布占比分析', fontsize=16, pad=20)

# 添加图例
legend_labels = [f"{label} ({count}首, {percent:.1f}%)" for label, count, percent in
                zip(top10_with_other['词牌'], top10_with_other['数量'], top10_with_other['占比'])]
plt.legend(wedges, legend_labels,
          title="词牌详情",
          loc="center left",
          bbox_to_anchor=(1, 0.5),
          fontsize=10)

# 添加中心注释
centre_circle = plt.Circle((0,0), 0.5, color='white', fc='white', linewidth=0)
plt.gca().add_artist(centre_circle)
plt.text(0, 0, f"前十占比\n{top10_total/total*100:.1f}%",
         ha='center', va='center', fontsize=12, fontweight='bold')

# 添加统计信息
stats_text = f"词牌总量: {len(df)}种\n作品总量: {total}首\n前十总量: {top10_total}首"
plt.figtext(0.5, 0.01, stats_text,
            ha='center', fontsize=12,
            bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.7))

# 调整布局
plt.tight_layout(rect=[0, 0.05, 1, 0.95])

# 保存并显示
plt.savefig('宋词词牌占比饼图.png', dpi=300, bbox_inches='tight')
plt.show()