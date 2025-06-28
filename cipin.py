import jieba
from collections import Counter

# 读取宋词文本
with open('ci_song_paragraphs.txt', 'r', encoding='utf-8') as file:
    ci_song_text = file.read()

# 读取停词表
with open('stop_words.txt', 'r', encoding='utf-8') as file:
    stop_words = {line.strip() for line in file if line.strip()}

# 分词
words = jieba.lcut(ci_song_text)

# 过滤停词和长度小于2的词
filtered_words = [word for word in words if word not in stop_words and len(word) >= 2]

# 统计词频
word_count = Counter(filtered_words)

# 按词频降序排序
sorted_word_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

# 保存为txt文件
txt_path = 'ci_song_word_frequency.txt'
with open(txt_path, 'w', encoding='utf-8') as out_file:
    out_file.write("词语,词频\n")
    for word, count in sorted_word_count:
        out_file.write(f"{word},{count}\n")