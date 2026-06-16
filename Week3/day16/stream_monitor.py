# stream_monitor.py
# 练习 4（选做）：流式输出 + 性能监控
# 目标：流式输出时统计每次响应的字符数和耗时，做成简单的性能监控

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day16-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def stream_with_stats(prompt: str) -> dict:
    """
    流式调用并统计性能数据
    返回：{"content": "...", "chars": 字符数, "elapsed_sec": 耗时秒, "chars_per_sec": 速度}

    TODO：
    1. 记录开始时间（time.time()）
    2. 流式调用，逐字打印，收集完整内容
    3. 记录结束时间，计算耗时
    4. 返回统计字典
    """
    # 请在这里写代码 ↓
    start = time.time()
    full_content = ""

    response = client.chat.completions.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )
    for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_content += delta
    print()

    elapsed = time.time() - start
    chars = len(full_content)
    return {
        "content": full_content,
        "chars": chars,
        "elapsed_sec": round(elapsed, 2),
        "chars_per_sec": round(chars / elapsed, 0) if elapsed > 0 else 0
    }


if __name__ == "__main__":
    test_prompts = [
        "用一句话回答：什么是机器学习？",
        "列出学习Python的5个步骤，每步一句话。",
        "写一段100字左右的短文，介绍重庆的特色美食。",
    ]

    print("=== 流式输出性能监控 ===\n")
    for p in test_prompts:
        print(f"问：{p}")
        print("答：", end="")
        stats = stream_with_stats(p)
        print(f"\n📊 字符数：{stats['chars']} | 耗时：{stats['elapsed_sec']:.2f}s | 速度：{stats['chars_per_sec']:.0f}字/秒\n")
        print("-" * 50)
