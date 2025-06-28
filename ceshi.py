import pandas as pd
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Bar, Pie, Scatter, WordCloud, Grid
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType

# 加载数据
df = pd.read_csv('全宋词output.csv')

# 预处理：去除词牌名的空格和特殊字符
df['rhythmic'] = df['rhythmic'].str.replace('・', '·').str.strip()

# 情感类别映射
sentiment_mapping = {
    '积极': '#91cc75',
    '中性': '#fac858',
    '消极': '#ee6666'
}

# 1. 统计每个词牌的情感分布
rhythmic_sentiment = df.groupby(['rhythmic', 'sentiment_class']).size().unstack(fill_value=0)
rhythmic_sentiment['total'] = rhythmic_sentiment.sum(axis=1)
rhythmic_sentiment = rhythmic_sentiment.sort_values('total', ascending=False)

# 2. 计算每个词牌的主要情感主题
rhythmic_sentiment['dominant_sentiment'] = rhythmic_sentiment[['积极', '中性', '消极']].idxmax(axis=1)
rhythmic_sentiment['dominant_ratio'] = rhythmic_sentiment[['积极', '中性', '消极']].max(axis=1) / rhythmic_sentiment[
    'total']

# 3. 计算每个词牌的平均情感得分
rhythmic_avg_score = df.groupby('rhythmic')['sentiment_score'].mean().reset_index()
rhythmic_sentiment = rhythmic_sentiment.merge(rhythmic_avg_score, on='rhythmic')

# 4. 选择高频词牌（出现次数≥10）
high_freq_rhythmic = rhythmic_sentiment[rhythmic_sentiment['total'] >= 10]


# 可视化
def create_visualizations():
    # 词牌情感分布堆叠柱状图
    top_20 = high_freq_rhythmic.head(20)
    bar = (
        Bar(init_opts=opts.InitOpts(width="100%", height="600px", theme=ThemeType.ROMA))
        .add_xaxis(top_20.index.tolist())
        .add_yaxis("积极", top_20['积极'].tolist(), stack="stack1",
                   itemstyle_opts=opts.ItemStyleOpts(color=sentiment_mapping['积极']))
        .add_yaxis("中性", top_20['中性'].tolist(), stack="stack1",
                   itemstyle_opts=opts.ItemStyleOpts(color=sentiment_mapping['中性']))
        .add_yaxis("消极", top_20['消极'].tolist(), stack="stack1",
                   itemstyle_opts=opts.ItemStyleOpts(color=sentiment_mapping['消极']))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="高频词牌情感分布", subtitle="出现频次前20的词牌"),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="shadow"),
            legend_opts=opts.LegendOpts(pos_top="5%"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
            yaxis_opts=opts.AxisOpts(name="词作数量"),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")],
        )
    )

    # 词牌情感主题词云
    wordcloud_data = []
    for rhythmic, row in high_freq_rhythmic.iterrows():
        size = min(100, row['total'] * 2)  # 根据频率调整大小
        color = sentiment_mapping[row['dominant_sentiment']]
        wordcloud_data.append((rhythmic, size, color))

    wc = (
        WordCloud(init_opts=opts.InitOpts(width="100%", height="500px"))
        .add(series_name="", data_pair=wordcloud_data, word_size_range=[12, 60])
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词牌情感主题词云",
                                      subtitle="大小表示出现频率，颜色表示主要情感主题"),
            tooltip_opts=opts.TooltipOpts(formatter=JsCode(
                "function(params){return params.name + ': ' + params.value[1] + '首';}"
            )),
            legend_opts=opts.LegendOpts(is_show=False)
        )
    )

    # 词牌情感得分分布
    scatter_data = []
    for rhythmic, row in high_freq_rhythmic.iterrows():
        scatter_data.append({
            "value": [row['sentiment_score'], row['total']],
            "name": rhythmic,
            "itemStyle": {"color": sentiment_mapping[row['dominant_sentiment']]}
        })

    scatter = (
        Scatter(init_opts=opts.InitOpts(width="100%", height="500px"))
        .add_xaxis(xaxis_data=[])
        .add_yaxis(
            series_name="",
            y_axis=scatter_data,
            symbol_size=JsCode("function(data){return Math.sqrt(data[1]) * 2;}"),
            label_opts=opts.LabelOpts(
                formatter=JsCode("function(params){return params.name;}")
            )
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="词牌情感得分分布",
                                      subtitle="气泡大小表示出现频率"),
            tooltip_opts=opts.TooltipOpts(
                formatter=JsCode(
                    "function(params){"
                    "return '词牌: ' + params.name + '<br/>' + "
                    "'平均情感得分: ' + params.value[0].toFixed(2) + '<br/>' + "
                    "'作品数量: ' + params.value[1];}"
                )
            ),
            xaxis_opts=opts.AxisOpts(
                name="情感得分",
                min=0,
                max=1,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            yaxis_opts=opts.AxisOpts(
                name="作品数量",
                type_="log",
                min=10,
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            visualmap_opts=opts.VisualMapOpts(
                dimension=0,
                min=0,
                max=1,
                range_text=["情感得分范围"],
                textstyle_opts=opts.TextStyleOpts(color="#aaa"),
                in_range={"color": ["#ee6666", "#fac858", "#91cc75"]}
            )
        )
    )

    # 情感主题分布饼图
    sentiment_counts = df['sentiment_class'].value_counts()
    pie = (
        Pie(init_opts=opts.InitOpts(width="50%", height="400px"))
        .add(
            "",
            [list(z) for z in zip(sentiment_counts.index.tolist(), sentiment_counts.tolist())],
            radius=["40%", "70%"],
            label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)")
        )
        .set_global_opts(
            title_opts=opts.TitleOpts(title="宋词情感主题分布"),
            legend_opts=opts.LegendOpts(orient="vertical", pos_left="left"),
            tooltip_opts=opts.TooltipOpts(
                formatter="{a} <br/>{b}: {c}首 ({d}%)"
            )
        )
        .set_colors([sentiment_mapping[s] for s in sentiment_counts.index])
        .set_series_opts(label_opts=opts.LabelOpts(position="outside"))
    )

    # 组合图表
    grid = (
        Grid(init_opts=opts.InitOpts(width="100%", height="1000px", theme=ThemeType.ROMA))
        .add(bar, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="5%", height="30%"))
        .add(wc, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="40%", height="30%"))
        .add(scatter, grid_opts=opts.GridOpts(pos_left="5%", pos_right="5%", pos_top="75%", height="30%"))
        .add(pie, grid_opts=opts.GridOpts(pos_left="65%", pos_top="75%", width="30%", height="25%"))
    )

    return grid


# 生成可视化
chart = create_visualizations()
chart.render("词牌情感分析.html")