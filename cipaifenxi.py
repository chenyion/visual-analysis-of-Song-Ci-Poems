import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Pie

# 加载数据
data = pd.read_csv('词牌数量统计.csv')

# 按数量降序排序，并选取排名前十的词牌
top_10_data = data.sort_values(by='数量', ascending=False).head(10)

# 计算排名前十词牌的占比
total = top_10_data['数量'].sum()
top_10_data['占比'] = top_10_data['数量'].apply(lambda x: f'{(x / total) * 100:.2f}%')

# 创建饼图
pie = (
    Pie()
    .add(
        "",
        [list(z) for z in zip(top_10_data['词牌'], top_10_data['数量'])],
        radius=["30%", "75%"],
        label_opts=opts.LabelOpts(
            font_size=12,
            formatter="{b}: {c} ({d}%)",
            position="outside",
        ),
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="排名前十词牌占比饼图", subtitle="展示排名前十词牌数量占比情况",
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=25)),
        legend_opts=opts.LegendOpts(orient="vertical", pos_top="15%", pos_left="2%"),
        toolbox_opts=opts.ToolboxOpts(is_show=True)
    )
)

# 渲染图表到 HTML 文件
pie.render("排名前十词牌占比饼图.html")