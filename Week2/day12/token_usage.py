# 练习 4：上下文窗口感知 + Token 消耗统计
# 目标：学会从 API 响应中读取 token 用量，观察多轮对话的 token 消耗变化
#
# 需要安装：pip install openai python-dotenv

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

MODEL = os.getenv("MODEL_NAME", "claude-sonnet-4-6")

def chat_and_count_tokens(messages: list) -> tuple:
    """
    发送消息，返回 (回复内容, token消耗统计)
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=200,
    )

    content = response.choices[0].message.content

    # 从 response.usage 中读取 token 用量
    usage = {
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "total_tokens": response.usage.total_tokens,
    }

    return content, usage

# 模拟一次多轮对话，观察随对话增长 token 消耗如何变化
conversation = [
    {"role": "system", "content": "你是一个合同顾问，回答要简洁。"},
]

questions = [
    "什么是违约责任？",
    "违约责任有什么后果？",
    "作为违约方，我应该怎么做？",
]

print("模拟多轮对话 - 观察 Token 消耗变化\n")
total_cost_estimate = 0.0

for q in questions:
    conversation.append({"role": "user", "content": q})

    reply, usage = chat_and_count_tokens(conversation)

    # 把助手的回复也加入对话历史
    conversation.append({"role": "assistant", "content": reply})

    # 按 claude-sonnet-4-6 估算费用（仅供参考）
    # 实际以平台计费为准
    cost = (usage["input_tokens"] / 1000 * 0.003) + \
           (usage["output_tokens"] / 1000 * 0.015)

    total_cost_estimate += cost

    print(f"问：{q}")
    print(f"答：{reply[:100]}...")
    print(f"Token: 输入={usage['input_tokens']}, 输出={usage['output_tokens']}, 本次费用≈¥{cost:.4f}")
    print()

print(f"本次对话总估算费用：¥{total_cost_estimate:.4f}")
print(f"\n思考：随着对话轮次增加，输入 token 为什么越来越多？")
print(f"-> 因为每次请求都会把完整的对话历史发给 API，轮次越多历史越长，输入 token 自然增加。")
