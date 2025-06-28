import requests
import hashlib
import random
import csv
import time

# 百度翻译 API 的配置
appid = '20250627002391296'
secretKey = 'i9HNpuiVE9GaRXd9BMg9'
url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'

def translate_text(text):
    from_lang = 'zh'  # 源语言为中文（文言文属于中文范畴）
    to_lang = 'zh'  # 目标语言为中文（现代文）
    salt = random.randint(32768, 65536)

    # 计算签名
    sign = appid + text + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()

    # 构建请求参数
    data = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
       'sign': sign
    }

    # 发送请求
    response = requests.get(url, params=data)
    result = response.json()

    if 'trans_result' in result:
        return result['trans_result'][0]['dst']
    else:
        print('翻译失败：', result)
        return text

# 读取 CSV 文件
csv_file_path = 'quansongci.csv'
translated_csv_file_path = 'quansongci_translated.csv'
with open(csv_file_path, 'r', encoding='utf-8') as file_in, open(translated_csv_file_path, 'w', encoding='utf-8', newline='') as file_out:
    reader = csv.reader(file_in)
    writer = csv.writer(file_out)

    # 写入表头
    header = next(reader)
    writer.writerow(header)

    # 逐行读取并翻译
    for row in reader:
        translated_row = []
        for cell in row:
            # 假设所有单元格内容都需要翻译，若只有特定列需要翻译，可在此处添加判断条件
            translated_text = translate_text(cell)
            translated_row.append(translated_text)
            time.sleep(1)  # 每次翻译后暂停1秒，可根据实际情况调整时间
        writer.writerow(translated_row)