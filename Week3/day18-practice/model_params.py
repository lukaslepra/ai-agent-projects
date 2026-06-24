# model_params.py
# 练习 3：模型参数实验
# 目标：理解 max_tokens、stop、presence_penalty、frequency_penalty 的实际效果

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day18-practice\.env")

client = OpenAI(
    api_key=***"OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv("MODEL_NAME", "claude-sonnet-4-6")


# ── 练习 3-A：max_tokens 控制输出长度 ────────────────────────────

def chat_with_max_tokens(user_message: str, max_tokens: int) -> dict:
    """
    用 max_tokens 限制输出长度
    TODO：
    1. 调用 API，加上 max_tokens 参数
    2. 返回 {"content": 回答, "finish_reason": 结束原因, "tokens_used": 实际用了多少token}
    提示：tokens_used 从 response.usage.completion_tokens 获取
          finish_reason 从 response.choices[0].finish_reason 获取
          "stop" = 正常结束，"length" = 被 max_tokens 截断
    """
    # 请在这里写代码 ↓
    pass


# ── 练习 3-B：stop 序列 ───────────────────────────────────────────

def chat_with_stop(user_message: str, stop_sequences: list) -> str:
    """
    用 stop 参数让模型在遇到特定字符串时停止输出
    应用场景：代码生成时遇到 ``` 就停，避免多余内容
    TODO：调用 API，加上 stop=stop_sequences 参数
    """
    # 请在这里写代码 ↓
    pass


# ── 练习 3-C：frequency_penalty 减少重复 ────────────────────────

def chat_with_penalty(user_message: str, frequency_penalty: float) -> str:
    """
    frequency_penalty（0~2）：惩罚已出现的词，值越高越不重复
    presence_penalty（0~2）：鼓励引入新话题，值越高越发散
    TODO：调用 API，加上 frequency_penalty 参数
    """
    # 请在这里写代码 ↓
    pass


if __name__ == "__main__":
    # 测试 3-A：max_tokens 截断效果
    print("=== 测试 3-A：max_tokens 对比 ===")
    question = "详细介绍一下重庆的旅游景点"
    for max_t in [20, 100, 500]:
        result = chat_with_max_tokens(question, max_t)
        print(f"max_tokens={max_t} | finish_reason={result['finish_reason']} | tokens={result['tokens_used']}")
        print(f"内容：{result['content'][:80]}...\n")

    # 测试 3-B：stop 序列
    print("=== 测试 3-B：stop 序列 ===")
    result = chat_with_stop(
        "写一段 Python 代码，用 for 循环打印 1 到 5",
        stop_sequences=["```"]
    )
    print(f"输出（遇到 ``` 停止）：\n{result}\n")

    # 测试 3-C：penalty 对比
    print("=== 测试 3-C：frequency_penalty 对比 ===")
    question = "介绍一下人工智能"
    for penalty in [0.0, 1.5]:
        result = chat_with_penalty(question, penalty)
        print(f"penalty={penalty}：{result[:120]}...\n")
