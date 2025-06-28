import json
import csv

# 定义 JSON 文件路径
json_file_path = 'songcidata/author.song.json'

try:
    # 打开并读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 定义 CSV 文件路径
    csv_file_path = '部分词人经历.csv'

    # 打开 CSV 文件并写入表头
    with open(csv_file_path, 'w', newline='', encoding='utf-8-sig') as csv_file:
        fieldnames = ['name', 'short_description']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 遍历 JSON 数据，提取 name 和 short_description 并写入 CSV 文件
        for author in data:
            name = author.get('name')
            short_description = author.get('short_description')
            writer.writerow({'name': name, 'short_description': short_description})

    print(f"成功将作者信息保存到 {csv_file_path}")

except FileNotFoundError:
    print(f"未找到文件: {json_file_path}")
except json.JSONDecodeError:
    print(f"无法解析 {json_file_path} 为有效的 JSON 数据。")