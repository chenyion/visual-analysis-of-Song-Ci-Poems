import jieba

# 读取停词表文件，假设停词表文件为stop_words.txt，每行一个停词
with open('stop_words.txt', 'r', encoding='utf-8') as file:
    stop_words = {line.strip() for line in file if line.strip()}

# 读取宋词文本内容
with open('ci_song_paragraphs.txt', 'r', encoding='utf-8') as file:
    ci_song_text = file.read()

# 进行分词处理
ci_song_words = jieba.lcut(ci_song_text)

# 过滤停词
filtered_words = [word for word in ci_song_words if word not in stop_words and len(word) > 1]

# 将结果保存为新的txt文件
with open('ci_song_words_filtered.txt', 'w', encoding='utf-8') as out_file:
    out_file.write(' '.join(filtered_words))