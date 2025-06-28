import pandas as pd
import requests
import json
import time
import os
import concurrent.futures
from tqdm import tqdm
import logging
import re
from threading import Lock

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# 配置参数
API_KEY = "sk-61d342dcc66848f396646a56909af0f2"  # 替换为实际API密钥
CSV_PATH = "quansongci.csv"  # 输入文件路径
OUTPUT_CSV = "全宋词_情感分析结果.csv"  # 输出文件路径
MODEL = "deepseek-chat"  # 使用deepseek-chat模型
MAX_WORKERS = 300  # 并发工作线程数（根据API配额调整）
REQUESTS_PER_MINUTE = 500  # 每分钟请求限制（免费账户建议10-20，付费账户可提高）
SAVE_INTERVAL = 150  # 每处理多少条保存一次进度
ERROR_RETRY = 3  # 错误重试次数
MAX_TOKENS = 500  # 最大token限制（防止长文本消耗过多）


# 速率控制器
class RateLimiter:
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.interval = 60.0 / requests_per_minute
        self.last_request_time = 0
        self.lock = Lock()

    def wait(self):
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time
            wait_time = max(0, self.interval - elapsed)
            if wait_time > 0:
                time.sleep(wait_time)
            self.last_request_time = time.time()


# DeepSeek API 请求函数（优化版）
def analyze_sentiment(text, limiter, retry_count=0):
    if retry_count >= ERROR_RETRY:
        return {
            "sentiment_class": "error",
            "sentiment_score": -1,
            "keywords": [],
            "analysis": "超过最大重试次数"
        }

    # 简化长文本（保留前300字符）
    if len(text) > 300:
        text = text[:300] + "..."

    # 等待速率限制
    limiter.wait()

    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # 优化的提示词
    prompt = f"""
作为中国古典文学专家，请分析以下宋词的情感倾向：
[宋词内容]
{text}

要求：
1. 情感分类：积极、消极或中性（三选一）
2. 情感强度：0.0（最弱）到1.0（最强）的浮点数
3. 情感关键词：提取1-3个最能体现情感的关键词
4. 简要分析：15字内说明判断依据

返回格式必须是纯JSON：
{{
    "sentiment_class": "分类结果",
    "sentiment_score": 强度值,
    "keywords": ["关键词1", "关键词2"],
    "analysis": "简要分析"
}}
"""

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": MAX_TOKENS,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()

        # 提取模型返回内容
        content = result["choices"][0]["message"]["content"].strip()

        # 处理JSON响应
        if content.startswith("```json"):
            content = re.sub(r'^```json\s*|\s*```$', '', content)

        data = json.loads(content)

        # 验证结果格式
        required_keys = ["sentiment_class", "sentiment_score", "keywords", "analysis"]
        if all(key in data for key in required_keys):
            return data
        else:
            raise ValueError("返回JSON缺少必要字段")

    except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
        logger.warning(f"请求失败（重试 {retry_count + 1}/{ERROR_RETRY}）: {str(e)}")
        time.sleep(2 ** retry_count)  # 指数退避
        return analyze_sentiment(text, limiter, retry_count + 1)


# 主处理流程（使用线程池并发处理）
def process_dataset():
    # 读取CSV文件
    if os.path.exists(OUTPUT_CSV):
        df = pd.read_csv(OUTPUT_CSV)
        logger.info(f"检测到已有进度文件，从中断处继续处理（当前行数: {len(df)}）")
    else:
        df = pd.read_csv(CSV_PATH)
        # 初始化结果列
        df["sentiment_class"] = ""
        df["sentiment_score"] = None
        df["keywords"] = ""
        df["analysis"] = ""
        df["processed"] = False

    # 创建进度条
    total = len(df)
    progress_bar = tqdm(total=total, desc="情感分析进度")

    # 更新已处理进度
    if "processed" in df.columns:
        processed_count = df["processed"].sum()
        progress_bar.update(processed_count)

    # 创建速率限制器
    limiter = RateLimiter(REQUESTS_PER_MINUTE)

    # 使用线程池并发处理
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}

        for index, row in df.iterrows():
            # 跳过已处理的行
            if "processed" in df.columns and df.at[index, "processed"]:
                continue

            text = row["content"]

            if pd.isna(text) or not text.strip():
                df.at[index, "sentiment_class"] = "skip"
                df.at[index, "processed"] = True
                progress_bar.update(1)
                continue

            # 提交任务到线程池
            future = executor.submit(analyze_sentiment, text, limiter)
            futures[future] = index

        # 处理完成的任务
        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                result = future.result()
                # 更新DataFrame
                df.at[index, "sentiment_class"] = result["sentiment_class"]
                df.at[index, "sentiment_score"] = result["sentiment_score"]
                df.at[index, "keywords"] = ", ".join(result["keywords"])
                df.at[index, "analysis"] = result["analysis"]
                df.at[index, "processed"] = True

                progress_bar.update(1)

                # 定期保存进度
                if progress_bar.n % SAVE_INTERVAL == 0:
                    df.to_csv(OUTPUT_CSV, index=False)
                    logger.info(f"已保存进度 ({progress_bar.n}/{total})")

            except Exception as e:
                logger.error(f"处理行 {index} 时出错: {str(e)}")
                df.at[index, "sentiment_class"] = "error"
                df.at[index, "processed"] = True
                progress_bar.update(1)

    # 最终保存
    df.to_csv(OUTPUT_CSV, index=False)
    progress_bar.close()
    logger.info(f"分析完成! 共处理 {len(df)} 首宋词，结果已保存至: {OUTPUT_CSV}")


if __name__ == "__main__":
    process_dataset()