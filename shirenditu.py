import json
import pandas as pd
import plotly.express as px
from collections import defaultdict


def load_data():
    """加载词人路线数据和坐标数据"""
    try:
        with open('luxian.json', 'r', encoding='utf-8') as f:
            poets_data = json.load(f)
        print(f"成功加载 {len(poets_data)} 位词人数据")

        with open('locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
        print("成功加载坐标数据")
        return poets_data, locations
    except Exception as e:
        print(f"数据加载失败: {e}")
        return None, None


def process_data(poets_data, locations):
    """处理数据，统计每个地点的访问情况"""
    location_info = defaultdict(lambda: {
        'count': 0,
        'visits': [],
        'lat': None,
        'log': None
    })

    location_coords = {}
    for loc in locations:
        location_coords[loc['name']] = {'lat': float(loc['lat']), 'log': float(loc['log'])}
        for child in loc.get('children', []):
            location_coords[child['name']] = {'lat': float(child['lat']), 'log': float(child['log'])}

    for poet in poets_data:
        poet_name = poet.get('name', '未知词人')
        visited_locations = set()

        for period in poet.get('path', []):
            age_group = period.get('time', '未知年龄段')
            for loc_name in period.get('route', []):
                if loc_name and loc_name not in visited_locations:
                    visited_locations.add(loc_name)
                    if loc_name in location_coords:
                        coord = location_coords[loc_name]
                        location_info[loc_name]['count'] += 1
                        location_info[loc_name]['visits'].append(f"{poet_name}({age_group})")
                        location_info[loc_name]['lat'] = coord['lat']
                        location_info[loc_name]['log'] = coord['log']

    data_list = []
    for loc_name, info in location_info.items():
        if info['lat'] is not None and info['log'] is not None:
            data_list.append({
                'location': loc_name,
                'count': info['count'],
                'visitors': '<br>'.join(info['visits']),
                'lat': info['lat'],
                'lon': info['log']  # 将log转换为lon
            })

    return pd.DataFrame(data_list)


def create_map(df):
    """创建交互式地图（使用最稳定的API）"""
    # 数据验证
    print("\n坐标范围验证:")
    print(f"经度范围: {df['lon'].min():.2f} - {df['lon'].max():.2f}")
    print(f"纬度范围: {df['lat'].min():.2f} - {df['lat'].max():.2f}")

    # 方案1：使用scatter_geo（最稳定的方案）
    fig = px.scatter_geo(
        df,
        lat='lat',
        lon='lon',
        size='count',
        color='count',
        color_continuous_scale=px.colors.sequential.Viridis,
        hover_name='location',
        hover_data=['count', 'visitors'],
        scope='asia',
        projection='natural earth',
        title='宋朝词人去处分布图',
        height=800
    )

    # 调整地图显示范围
    fig.update_geos(
        resolution=50,
        showcountries=True,
        countrycolor="Black",
        showsubunits=True,
        subunitcolor="Blue",
        lataxis_range=[15, 45],  # 中国纬度范围
        lonaxis_range=[100, 125]  # 中国经度范围
    )

    # 调整布局
    fig.update_layout(
        margin={"r": 0, "t": 50, "l": 0, "b": 0},
        title_x=0.5
    )

    return fig


def main():
    poets_data, locations = load_data()
    if not poets_data or not locations:
        return

    df = process_data(poets_data, locations)
    if df.empty:
        print("错误: 没有有效的地点数据")
        return

    print(f"\n有效地点数量: {len(df)}")
    print("示例数据:")
    print(df.head())

    fig = create_map(df)
    output_file = "song_poets_map.html"
    fig.write_html(output_file)
    print(f"\n地图已保存为 {output_file}")
    fig.show()


if __name__ == "__main__":
    main()