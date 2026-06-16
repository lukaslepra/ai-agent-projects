# temperature_lab.py
# 练习 1：temperature 实验
# 目标：用同一个 prompt，分别在不同 temperature 下调用多次，观察输出稳定性差异

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day15-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 实验用的 prompt（分类任务，答案应该稳定）
CLASSIFY_PROMPT = "把这句话分类为：正面/负面/中性。只回复一个词。"
TEST_TEXT = "这个产品还行，没有想象中那么好用。"


def test_temperature(temp: float, runs: int = 3) -> list:
    """
    用指定 temperature 调用 API 多次，返回结果列表
    TODO：
    1. 循环 runs 次
    2. 每次调用 client.chat.completions.create
       - model: "claude-sonnet-4-6"
       - messages: [system, user]（system 用 CLASSIFY_PROMPT，user 用 TEST_TEXT）
       - temperature: temp
       - max_tokens: 10
    3. 收集每次的回复内容，返回列表
    """
    results = []
    # 请在这里写代码 ↓
    for _ in range(runs):
        response = client.chat.completions.create(
            model="claude-sonnet-4-6",
            messages=[
                {"role": "system", "content": CLASSIFY_PROMPT},
                {"role": "user", "content": TEST_TEXT}
            ],
            temperature=temp,
            max_tokens=10
        )
        results.append(response.choices[0].message.content)

    return results


if __name__ == "__main__":
    temperatures = [0, 0.3, 0.7, 1.0]

    for temp in temperatures:
        results = test_temperature(temp)
        unique = set(results)
        print(f"\ntemperature={temp}:")
        print(f"  结果: {results}")
        print(f"  唯一值数量: {len(unique)}（越少说明越稳定）")
