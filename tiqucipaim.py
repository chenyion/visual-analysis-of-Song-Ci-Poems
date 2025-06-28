import json
import os
import pandas as pd

# 定义文件范围
start_index = 0
end_index = 20000
# 初始化存储词牌数量的字典
rhythmic_count = {}

# 遍历指定范围内的文件
for i in range(start_index, end_index + 1):
    file_name = f'ci.song.{i}.json'
    file_path = os.path.join('songcidata', file_name)

    # 检查文件是否存在
    if os.path.exists(file_path):
        try:
            # 打开并读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 遍历每首词
                for poem in data:
                    rhythmic = poem['rhythmic']
                    # 如果词牌已在字典中，数量加1
                    if rhythmic in rhythmic_count:
                        rhythmic_count[rhythmic] += 1
                    # 若词牌不在字典中，初始化为1
                    else:
                        rhythmic_count[rhythmic] = 1
        except Exception as e:
            print(f"读取文件 {file_name} 时出现错误: {e}")

# 将结果转换为DataFrame
result_df = pd.DataFrame.from_dict(rhythmic_count, orient='index', columns=['数量'])
result_df.index.name = '词牌'

# 保存为CSV文件
csv_file_path = '词牌数量统计.csv'
result_df.to_csv(csv_file_path, encoding='utf-8-sig')

print(f"统计结果已保存到 {csv_file_path}")