# stream_basic.py
# 练习 1：基础流式输出
# 目标：实现流式输出，让 AI 的回答像打字机一样逐字出现

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day16-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


def stream_response(prompt: str) -> str:
    """
    流式调用 API，逐字打印输出，返回完整内容
    TODO：
    1. 调用 client.chat.completions.create，stream=True
    2. 迭代每个 chunk，提取 delta.content
    3. 实时 print（end="", flush=True）
    4. 同时把每个 delta 拼接到 full_content
    5. 打印完后换行，返回 full_content
    """
    full_content = ""
    # 请在这里写代码 ↓
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
    print()  # 最后换行

    return full_content


if __name__ == "__main__":
    print("=== 流式输出演示 ===\n")

    prompts = [
        "用3句话介绍什么是大语言模型。",
        "列出5个Python最常用的内置函数，每个用一句话说明。",
    ]

    for p in prompts:
        print(f"问：{p}")
        print("答：", end="")
        result = stream_response(p)
        print(f"\n（共 {len(result)} 字）\n")
        print("-" * 50)
