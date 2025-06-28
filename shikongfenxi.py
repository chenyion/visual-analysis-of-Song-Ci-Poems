import pandas as pd
import matplotlib.pyplot as plt
import json
import re
from matplotlib.font_manager import FontProperties

# 设置中文字体
font = FontProperties(fname='C:/Windows/Fonts/simhei.ttf')  # 替换为实际中文字体路径

# 读取CSV数据
df = pd.read_csv('全宋词output.csv')

# 读取JSON作者信息
with open('songcidata/author.song.json', 'r', encoding='utf-8') as f:
    authors = json.load(f)

# 构建作者信息字典
author_info = {}
for author in authors:
    name = author['name']
    # 提取生卒年份
    match = re.search(r'\((\d{4})[－—](\d{4}|\D+)', author['description'])
    if match:
        birth = int(match.group(1))
        death = int(re.sub(r'\D', '', match.group(2))) if match.group(2).isdigit() else None
        # 确定朝代
        dynasty = "南宋" if birth >= 1127 or (death and death >= 1127) else "北宋"
    else:
        dynasty = "未知"

    # 提取籍贯省份
    birthplace = "未知"
    for pattern in [r'今属(.+?)省', r'今属(.+?)\)', r'(.+?)人\)']:
        match = re.search(pattern, author['description'])
        if match:
            birthplace = match.group(1)
            if '江' in birthplace: birthplace = '江苏'  # 简化处理
            break

    author_info[name] = {'dynasty': dynasty, 'birthplace': birthplace}

# 关联词作与作者信息
df['dynasty'] = df['author'].map(lambda x: author_info.get(x, {}).get('dynasty', '未知'))
df['province'] = df['author'].map(lambda x: author_info.get(x, {}).get('birthplace', '未知'))

# 过滤有效数据
df = df[df['dynasty'] != '未知']
df = df[df['province'] != '未知']

# 1. 时间分布（朝代情感均值）
dynasty_sentiment = df.groupby('dynasty')['sentiment_score'].mean()

# 2. 空间分布（省份情感均值）
province_sentiment = df.groupby('province')['sentiment_score'].mean().sort_values()

# 可视化
plt.figure(figsize=(14, 10))

# 时间分布图
plt.subplot(2, 1, 1)
dynasty_sentiment.plot(kind='bar', color=['#1f77b4', '#ff7f0e'])
plt.title('宋代词作情感时间分布', fontproperties=font, fontsize=16)
plt.ylabel('平均情感得分', fontproperties=font)
plt.xticks(rotation=0, fontproperties=font)
plt.ylim(0.5, 0.9)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 空间分布图
plt.subplot(2, 1, 2)
province_sentiment.plot(kind='barh', color='#2ca02c')
plt.title('宋代词作情感空间分布', fontproperties=font, fontsize=16)
plt.xlabel('平均情感得分', fontproperties=font)
plt.yticks(fontproperties=font)
plt.xlim(0.5, 0.9)
plt.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('sentiment_spatiotemporal_distribution.png', dpi=300)
plt.show()