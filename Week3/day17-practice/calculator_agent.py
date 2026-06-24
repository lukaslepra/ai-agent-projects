# calculator_agent.py
# 练习 1：基础 Function Calling
# 目标：给 AI 配备计算工具，完成完整的 Function Calling 循环

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

# ── 本地工具函数 ──────────────────────────────────────────────

def calculate(operation: str, a: float, b: float) -> float:
    """
    执行基础四则运算
    operation: "add" | "subtract" | "multiply" | "divide"
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "除数不能为0"
        return a / b
    else:
        return f"不支持的运算类型：{operation}"


# ── 工具定义 ──────────────────────────────────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学四则运算：加法、减法、乘法、除法",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "运算类型：add加、subtract减、multiply乘、divide除"
                    },
                    "a": {
                        "type": "number",
                        "description": "第一个数"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        }
    }
]


# ── Function Calling 主逻辑 ────────────────────────────────────

def run_with_tools(user_question: str) -> str:
    """
    完整的 Function Calling 循环：
    1. 发请求给 AI（带工具定义）
    2. 判断 AI 是否要调用工具
    3. 如果要：执行本地函数，把结果加入 messages，再次请求
    4. 返回 AI 的最终回答
    """
    messages = [{"role": "user", "content": user_question}]

    # 第一次调用 API，传入工具定义
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
        messages=messages,
        tools=tools,
    )

    # 检查 AI 是否要调用工具
    if response.choices[0].finish_reason == "tool_calls":
        # 把 AI 的 assistant 消息（含 tool_calls）加入 messages
        messages.append(response.choices[0].message)

        # 遍历所有工具调用请求
        for tool_call in response.choices[0].message.tool_calls:
            func_name = tool_call.function.name
            func_args = json.loads(tool_call.function.arguments)
            tool_call_id = tool_call.id

            # 执行本地函数
            result = calculate(**func_args)

            # 把结果作为 tool 角色消息加入 messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": str(result)
            })

        # 第二次调用 API 拿最终回答
        final_response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
            messages=messages,
            tools=tools,
        )
        return final_response.choices[0].message.content

    # AI 不需要调用工具，直接返回回答
    return response.choices[0].message.content


if __name__ == "__main__":
    questions = [
        "25 乘以 8 等于多少？",
        "1024 除以 32 是多少？",
        "如果我有 156 元，花了 78.5 元，还剩多少钱？",
    ]

    for q in questions:
        print(f"问：{q}")
        answer = run_with_tools(q)
        print(f"答：{answer}\n")
        print("-" * 50)
