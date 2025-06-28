import pandas as pd
import random
from pyecharts import options as opts
from pyecharts.charts import Scatter
from pyecharts.globals import ThemeType
import json

# 读取CSV数据
df = pd.read_csv('全宋词output.csv')

# 1. 统计词牌名数量并取前十
rhythmic_counts = df['rhythmic'].value_counts().head(10)
top_rhythmics = rhythmic_counts.index.tolist()

# 2. 筛选只包含前十词牌名的数据
filtered_df = df[df['rhythmic'].isin(top_rhythmics)]

# 3. 创建词牌名到数值的映射
rhythmic_to_num = {name: i for i, name in enumerate(top_rhythmics)}

# 4. 准备数据
all_data = []
colors = [
    "#5470C6", "#91CC75", "#FAC858", "#EE6666", "#73C0DE",
    "#3BA272", "#FC8452", "#9A60B4", "#EA7CCC", "#5470C6"
]

for i, rhythmic in enumerate(top_rhythmics):
    subset = filtered_df[filtered_df['rhythmic'] == rhythmic]
    for _, row in subset.iterrows():
        # 计算x坐标：词牌名对应的数值 + 随机抖动
        x = rhythmic_to_num[rhythmic] + random.uniform(-0.2, 0.2)
        y = row['sentiment_score']
        # 根据情感类别设置形状
        symbol = 'circle' if row['sentiment_class'] == '积极' else 'diamond'
        # 准备提示框内容
        content = row['content'][:30] + "..." if len(row['content']) > 30 else row['content']
        extra_info = {
            "author": row['author'],
            "content": content,
            "rhythmic": rhythmic
        }
        all_data.append({
            "x": x,
            "y": y,
            "symbol": symbol,
            "color": colors[i],
            "size": 8 + y * 8,  # 大小与情感分数相关
            "extra": extra_info
        })

# 5. 按词牌名分组数据（用于系列）
series_data = {rhythmic: [] for rhythmic in top_rhythmics}
for data in all_data:
    rhythmic_name = data['extra']['rhythmic']
    series_data[rhythmic_name].append(data)

# 6. 创建散点图
scatter = Scatter(init_opts=opts.InitOpts(
    theme=ThemeType.ROMA,
    width="1200px",
    height="700px",
    page_title="全宋词情感分析"
))

# 设置全局配置
scatter.set_global_opts(
    title_opts=opts.TitleOpts(
        title="全宋词情感分数分布",
        subtitle="前十词牌名情感分析",
        pos_left="center"
    ),
    tooltip_opts=opts.TooltipOpts(
        formatter=JsCode(
            "function(params) {"
            "   var data = params.data;"
            "   return '词牌名: ' + data.extra.rhythmic + '<br/>'"
            "          + '情感分数: ' + data.value[1].toFixed(2) + '<br/>'"
            "          + '作者: ' + data.extra.author + '<br/>'"
            "          + '内容: ' + data.extra.content;"
            "}"
        )
    ),
    legend_opts=opts.LegendOpts(
        pos_top="50px",
        selected_mode="single"
    ),
    xaxis_opts=opts.AxisOpts(
        name="词牌名",
        type_="value",
        name_location="middle",
        name_gap=30,
        min_=-0.5,
        max_=len(top_rhythmics) - 0.5,
        axislabel_opts=opts.LabelOpts(
            formatter=JsCode(
                f"function(value) {{"
                f"   var names = {json.dumps(top_rhythmics, ensure_ascii=False)};"
                f"   var index = Math.round(value);"
                f"   if (index >= 0 && index < names.length) {{"
                f"       return names[index];"
                f"   }}"
                f"   return '';"
                f"}}"
            )
        ),
        axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
        splitline_opts=opts.SplitLineOpts(is_show=False)
    ),
    yaxis_opts=opts.AxisOpts(
        name="情感分数",
        name_location="end",
        name_gap=20,
        min_=0,
        max_=1,
        axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(width=2)),
        splitline_opts=opts.SplitLineOpts(is_show=True, linestyle_opts=opts.LineStyleOpts(type_="dashed"))
    ),
    datazoom_opts=[
        opts.DataZoomOpts(type_="inside", xaxis_index=0),
        opts.DataZoomOpts(type_="slider", yaxis_index=0, pos_bottom="5%")
    ],
    toolbox_opts=opts.ToolboxOpts(
        pos_top="10px",
        pos_right="10px",
        feature={
            "saveAsImage": {},
            "dataZoom": {},
            "restore": {},
        }
    ),
    visualmap_opts=opts.VisualMapOpts(
        type_="size",
        min_=0,
        max_=1,
        dimension=1,
        range_size=[8, 20],
        orient="horizontal",
        pos_left="center",
        pos_bottom="0%"
    )
)

# 7. 添加系列
for i, rhythmic in enumerate(top_rhythmics):
    data_points = series_data[rhythmic]

    # 准备系列数据
    scatter_data = []
    for point in data_points:
        scatter_data.append([point['x'], point['y'], point])

    scatter.add_js_funcs(
        f"var extraData_{i} = {json.dumps([p['extra'] for p in data_points], ensure_ascii=False)};"
    )

    scatter.add_yaxis(
        series_name=rhythmic,
        y_axis=scatter_data,
        symbol_size=opts.ItemStyleOpts().opts.get("symbol_size", 10),
        symbol=next(iter(data_points))['symbol'] if data_points else 'circle',
        itemstyle_opts=opts.ItemStyleOpts(color=colors[i]),
        label_opts=opts.LabelOpts(is_show=False),
    )

# 8. 渲染图表
scatter.render("sentiment_scatter.html")