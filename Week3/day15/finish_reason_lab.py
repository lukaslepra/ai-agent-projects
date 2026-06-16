# finish_reason_lab.py
# 练习 2：finish_reason 检测器
# 目标：故意用很小的 max_tokens 让回复被截断，捕获并处理截断情况

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


def safe_call(prompt: str, max_tokens: int) -> dict:
    """
    带 finish_reason 检查的 API 调用
    返回：{"content": "...", "finish_reason": "...", "truncated": True/False, "tokens": {...}}

    TODO：
    1. 调用 API（model="claude-sonnet-4-6", max_tokens=max_tokens）
    2. 提取 content、finish_reason
    3. 如果 finish_reason == "length"，在 content 末尾追加 "...[截断]"
    4. 返回包含 content/finish_reason/truncated/tokens 的字典
       - truncated: bool，是否被截断
       - tokens: {"prompt": ..., "completion": ..., "total": ...}
    """
    # 请在这里写代码 ↓
    response = client.chat.completions.create(
        model="claude-sonnet-4-6",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens
    )

    content = response.choices[0].message.content
    finish_reason = response.choices[0].finish_reason

    if finish_reason == "length":
        content += "...[截断]"

    return {
        "content": content,
        "finish_reason": finish_reason,
        "truncated": finish_reason == "length",
        "tokens": {
            "prompt": response.usage.prompt_tokens,
            "completion": response.usage.completion_tokens,
            "total": response.usage.total_tokens
        }
    }


if __name__ == "__main__":
    long_question = "请详细介绍 LangChain 框架的核心组件，包括 Chain、Agent、Tool、Memory、Retriever 各自的作用和使用场景，并给出每个组件的代码示例。"

    print("=" * 60)
    print("实验：max_tokens 对输出的影响")
    print("=" * 60)

    for max_tok in [20, 100, 500]:
        result = safe_call(long_question, max_tok)
        print(f"\nmax_tokens={max_tok}:")
        print(f"  finish_reason: {result['finish_reason']}")
        print(f"  truncated: {result['truncated']}")
        print(f"  tokens 消耗: {result['tokens']}")
        print(f"  内容（前80字）: {result['content'][:80]}...")
