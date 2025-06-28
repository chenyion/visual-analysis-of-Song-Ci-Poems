import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud
import jieba
import re
import os

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Micro Hei']  # 多备选字体
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 读取数据
df = pd.read_csv("全宋词output.csv")


# 1. 情感分类的意象分析
def analyze_sentiment_keywords(df, sentiment):
    """
    分析特定情感的意象分布
    """
    sentiment_df = df[df["sentiment_class"] == sentiment]

    # 统计高频意象
    keywords = []
    for kw_str in sentiment_df["keywords"].dropna():
        keywords.extend([kw.strip() for kw in kw_str.split(",") if kw.strip()])
    kw_counts = Counter(keywords).most_common(20)

    # 分析analysis字段中的意象描述
    analysis_text = " ".join(sentiment_df["analysis"].dropna().astype(str))
    analysis_keywords = re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]+', analysis_text)
    analysis_counts = Counter(analysis_keywords).most_common(20)

    # 提取内容中的意象词
    content_keywords = []
    for content in sentiment_df["content"]:
        # 使用jieba分词提取名词性意象词
        words = jieba.lcut(content)
        for word in words:
            if len(word) > 1 and not re.match(r'[a-zA-Z0-9]', word):  # 过滤单个字和英文数字
                content_keywords.append(word)
    content_counts = Counter(content_keywords).most_common(50)  # 取更多用于词云

    return {
        "keywords": kw_counts,
        "analysis": analysis_counts,
        "content": content_counts,
        "avg_score": sentiment_df["sentiment_score"].mean()
    }


# 分析积极和消极情感
positive_analysis = analyze_sentiment_keywords(df, "积极")
negative_analysis = analyze_sentiment_keywords(df, "消极")


# 2. 作者风格分析 - 只统计作品超过160的作者
def analyze_author_style(df):
    """
    分析作者的情感风格（只统计作品超过160的作者）
    """
    author_data = {}
    for author, group in df.groupby("author"):
        total = len(group)
        if total < 160:  # 只统计作品超过160的作者
            continue

        positive = len(group[group["sentiment_class"] == "积极"])
        negative = len(group[group["sentiment_class"] == "消极"])
        neutral = len(group[group["sentiment_class"] == "中性"])

        # 计算情感比例
        positive_ratio = positive / total if total > 0 else 0
        negative_ratio = negative / total if total > 0 else 0

        # 提取作者常用意象
        keywords = []
        for kw_str in group["keywords"].dropna():
            keywords.extend([kw.strip() for kw in kw_str.split(",") if kw.strip()])
        top_keywords = Counter(keywords).most_common(5)

        author_data[author] = {
            "total": total,
            "positive_ratio": positive_ratio,
            "negative_ratio": negative_ratio,
            "top_keywords": top_keywords,
            "avg_score": group["sentiment_score"].mean()
        }

    # 找出最积极和最消极的作者（如果存在）
    if author_data:
        most_positive = max(author_data.items(), key=lambda x: x[1]["positive_ratio"])
        most_negative = max(author_data.items(), key=lambda x: x[1]["negative_ratio"])
        return author_data, most_positive, most_negative
    return {}, None, None


author_style, most_positive, most_negative = analyze_author_style(df)


# 3. 词牌名与意象关系分析 - 只统计作品超过160的词牌
def analyze_rhythmic_patterns(df):
    """
    分析词牌名的情感模式和意象偏好（只统计作品超过160的词牌）
    """
    rhythmic_data = {}
    for rhythmic, group in df.groupby("rhythmic"):
        total = len(group)
        if total < 160:  # 只统计作品超过160的词牌
            continue

        # 情感分布
        positive = len(group[group["sentiment_class"] == "积极"])
        negative = len(group[group["sentiment_class"] == "消极"])
        neutral = len(group[group["sentiment_class"] == "中性"])

        # 常用意象
        keywords = []
        for kw_str in group["keywords"].dropna():
            keywords.extend([kw.strip() for kw in kw_str.split(",") if kw.strip()])
        top_keywords = Counter(keywords).most_common(5)

        # 情感分析
        avg_score = group["sentiment_score"].mean()
        sentiment_tendency = "积极" if avg_score > 0.6 else "消极"

        # 分析内容中的常见主题
        analysis_text = " ".join(group["analysis"].dropna().astype(str))
        common_themes = Counter(re.findall(r'[a-zA-Z0-9\u4e00-\u9fa5]{2,}', analysis_text)).most_common(5)

        rhythmic_data[rhythmic] = {
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "top_keywords": top_keywords,
            "avg_score": avg_score,
            "sentiment_tendency": sentiment_tendency,
            "common_themes": common_themes
        }

    return rhythmic_data


rhythmic_data = analyze_rhythmic_patterns(df)


# 4. 可视化分析
def visualize_analysis(positive_analysis, negative_analysis, author_style, rhythmic_data):
    """
    创建可视化图表
    """
    # 1. 情感意象对比图
    plt.figure(figsize=(14, 10))

    # 积极情感意象
    if positive_analysis["keywords"]:
        plt.subplot(2, 2, 1)
        pos_kw, pos_count = zip(*positive_analysis["keywords"][:10])
        plt.barh(pos_kw, pos_count, color='lightgreen')
        plt.title('积极情感高频意象')
        plt.xlabel('出现频次')

    # 消极情感意象
    if negative_analysis["keywords"]:
        plt.subplot(2, 2, 2)
        neg_kw, neg_count = zip(*negative_analysis["keywords"][:10])
        plt.barh(neg_kw, neg_count, color='lightcoral')
        plt.title('消极情感高频意象')
        plt.xlabel('出现频次')

    # 作者情感倾向 - 只显示作品超过160的作者
    if author_style:
        plt.subplot(2, 2, 3)
        authors = list(author_style.keys())
        pos_ratios = [author_style[a]["positive_ratio"] for a in authors]
        neg_ratios = [author_style[a]["negative_ratio"] for a in authors]

        bar_width = 0.35
        index = np.arange(len(authors))
        plt.bar(index, pos_ratios, bar_width, label='积极比例', color='lightgreen')
        plt.bar(index + bar_width, neg_ratios, bar_width, label='消极比例', color='lightcoral')

        plt.xlabel('作者')
        plt.ylabel('情感比例')
        plt.title('高产作者情感风格分布（作品>160）')
        plt.xticks(index + bar_width / 2, authors, rotation=45)
        plt.legend()
    else:
        plt.subplot(2, 2, 3)
        plt.text(0.5, 0.5, '无满足条件的作者数据',
                 ha='center', va='center', fontsize=12)
        plt.title('高产作者情感风格分布（作品>160）')
        plt.axis('off')

    # 词牌情感得分 - 只显示作品超过160的词牌
    if rhythmic_data:
        plt.subplot(2, 2, 4)
        rhythmics = list(rhythmic_data.keys())
        scores = [rhythmic_data[r]["avg_score"] for r in rhythmics]
        colors = ['lightgreen' if s > 0.6 else 'lightcoral' for s in scores]

        plt.bar(rhythmics, scores, color=colors)
        plt.axhline(y=0.5, color='gray', linestyle='--')
        plt.title('常用词牌情感得分（作品>160）')
        plt.ylabel('情感得分')
        plt.xticks(rotation=45)
        plt.ylim(0, 1)
    else:
        plt.subplot(2, 2, 4)
        plt.text(0.5, 0.5, '无满足条件的词牌数据',
                 ha='center', va='center', fontsize=12)
        plt.title('常用词牌情感得分（作品>160）')
        plt.axis('off')

    plt.tight_layout()
    plt.savefig('宋词情感分析.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. 生成意象词云
    def generate_wordcloud(data, title, filename):
        if not data["content"]:
            print(f"无法生成'{title}'词云：无有效数据")
            return

        try:
            # 尝试使用不同字体路径
            font_path = None
            possible_fonts = [
                'C:/Windows/Fonts/simhei.ttf',  # Windows
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'  # Linux
            ]

            for path in possible_fonts:
                if os.path.exists(path):
                    font_path = path
                    break

            if not font_path:
                # 尝试使用matplotlib内置字体
                from matplotlib.font_manager import findfont, FontProperties
                font_path = findfont(FontProperties(family=['sans-serif']))

            wc = WordCloud(
                font_path=font_path,
                width=800,
                height=600,
                background_color='white',
                max_words=100
            )
            # 将高频词转换为字典格式
            word_freq = {word: freq for word, freq in data["content"][:50]}
            wc.generate_from_frequencies(word_freq)

            plt.figure(figsize=(10, 8))
            plt.imshow(wc, interpolation='bilinear')
            plt.axis('off')
            plt.title(title)
            plt.savefig(filename, dpi=300)
            plt.close()
        except Exception as e:
            print(f"生成词云时出错: {e}")

    generate_wordcloud(positive_analysis, '积极情感意象词云', 'positive_wordcloud.png')
    generate_wordcloud(negative_analysis, '消极情感意象词云', 'negative_wordcloud.png')


# 执行可视化
visualize_analysis(positive_analysis, negative_analysis, author_style, rhythmic_data)

# 5. 输出关键分析结果
print("=" * 80)
print("情感意象分析结果：")
print(f"积极情感平均得分: {positive_analysis['avg_score']:.2f}")
print(f"高频意象: {', '.join([kw for kw, _ in positive_analysis['keywords'][:10]])}")
print(f"常见主题: {', '.join([t for t, _ in positive_analysis['analysis'][:5]])}\n")

print(f"消极情感平均得分: {negative_analysis['avg_score']:.2f}")
print(f"高频意象: {', '.join([kw for kw, _ in negative_analysis['keywords'][:10]])}")
print(f"常见主题: {', '.join([t for t, _ in negative_analysis['analysis'][:5]])}\n")

print("=" * 80)
print("高产作者风格分析（作品>160）：")
if author_style:
    if most_positive:
        print(f"最积极的作者: {most_positive[0]} (积极比例: {most_positive[1]['positive_ratio']:.2f})")
        print(f"常用意象: {', '.join([kw for kw, _ in most_positive[1]['top_keywords']])}\n")

    if most_negative:
        print(f"最消极的作者: {most_negative[0]} (消极比例: {most_negative[1]['negative_ratio']:.2f})")
        print(f"常用意象: {', '.join([kw for kw, _ in most_negative[1]['top_keywords']])}\n")

    # 输出所有高产作者
    print("所有高产作者分析:")
    for author, data in author_style.items():
        print(
            f"- {author}: 作品数={data['total']}, 积极比例={data['positive_ratio']:.2f}, 消极比例={data['negative_ratio']:.2f}")
        print(f"  常用意象: {', '.join([kw for kw, _ in data['top_keywords']])}")
else:
    print("没有找到作品超过160的作者")

print("\n" + "=" * 80)
print("常用词牌分析（作品>160）：")
if rhythmic_data:
    # 找出情感倾向最明显的词牌
    if rhythmic_data:
        most_positive_rhythmic = max(rhythmic_data.items(), key=lambda x: x[1]["avg_score"])
        most_negative_rhythmic = min(rhythmic_data.items(), key=lambda x: x[1]["avg_score"])

    if most_positive_rhythmic:
        print(f"最积极的词牌: {most_positive_rhythmic[0]} (平均分: {most_positive_rhythmic[1]['avg_score']:.2f})")
        print(f"常用意象: {', '.join([kw for kw, _ in most_positive_rhythmic[1]['top_keywords']])}")
        print(f"常见主题: {', '.join([t for t, _ in most_positive_rhythmic[1]['common_themes']])}\n")

    if most_negative_rhythmic:
        print(f"最消极的词牌: {most_negative_rhythmic[0]} (平均分: {most_negative_rhythmic[1]['avg_score']:.2f})")
        print(f"常用意象: {', '.join([kw for kw, _ in most_negative_rhythmic[1]['top_keywords']])}")
        print(f"常见主题: {', '.join([t for t, _ in most_negative_rhythmic[1]['common_themes']])}\n")

    # 输出所有常用词牌
    print("所有常用词牌分析:")
    for rhythmic, data in rhythmic_data.items():
        print(
            f"- {rhythmic}: 作品数={data['total']}, 平均情感分={data['avg_score']:.2f}, 倾向={data['sentiment_tendency']}")
        print(f"  常用意象: {', '.join([kw for kw, _ in data['top_keywords']])}")
        print(f"  常见主题: {', '.join([t for t, _ in data['common_themes']])}")
else:
    print("没有找到作品超过160的词牌")

# 6. 保存完整分析结果到CSV
# 作者风格结果
if author_style:
    author_df = pd.DataFrame.from_dict(author_style, orient='index')
    author_df.reset_index(inplace=True)
    author_df.rename(columns={'index': 'author'}, inplace=True)
    author_df.to_csv('高产作者风格分析.csv', index=False)

# 词牌分析结果
if rhythmic_data:
    rhythmic_df = pd.DataFrame.from_dict(rhythmic_data, orient='index')
    rhythmic_df.reset_index(inplace=True)
    rhythmic_df.rename(columns={'index': 'rhythmic'}, inplace=True)
    rhythmic_df.to_csv('常用词牌分析.csv', index=False)

print("\n分析完成！结果已保存为CSV文件和图表。")