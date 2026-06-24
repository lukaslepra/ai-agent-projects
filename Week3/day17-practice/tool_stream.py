# tool_stream.py
# 练习 3：Function Calling + 流式输出
# 目标：工具调用完成后，最终回答用流式输出

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day17-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

def calculate(operation: str, a: float, b: float) -> float:
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "除数不能为0"
    }
    return ops.get(operation, "不支持的运算")

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学四则运算",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        }
    }
]


def run_with_stream(question: str):
    """
    Function Calling + 流式输出：
    - 第一次调用：非流式（因为要解析 tool_calls）
    - 工具执行完毕后，第二次调用用 stream=True
    """
    messages = [{"role": "user", "content": question}]

    # 第一次非流式调用（检查是否需要工具）
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
        messages=messages,
        tools=tools,
    )

    # 如果需要工具：执行工具，把结果加入 messages
    if response.choices[0].finish_reason == "tool_calls":
        # 把 AI 的 assistant 消息加入 messages
        messages.append(response.choices[0].message)

        # 执行所有工具调用
        for tool_call in response.choices[0].message.tool_calls:
            func_args = json.loads(tool_call.function.arguments)
            result = calculate(**func_args)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        # 第二次调用加上 stream=True，流式打印最终回答
        stream = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
            messages=messages,
            tools=tools,
            stream=True
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                print(delta.content, end="", flush=True)
    else:
        # 如果不需要工具：直接打印第一次的回答
        print(response.choices[0].message.content, end="", flush=True)


if __name__ == "__main__":
    questions = [
        "99 乘以 99 等于多少？请详细解释一下这个计算过程。",
        "你好，今天天气不错。",  # 不需要工具调用的情况
    ]

    for q in questions:
        print(f"问：{q}")
        print("答：", end="")
        run_with_stream(q)
        print("\n" + "-" * 50)
