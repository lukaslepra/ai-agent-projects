# tool_chat.py
# 练习 4（选做）：带工具调用的多轮对话
# 目标：多轮对话 + Function Calling，AI 在连续对话中可以随时调用工具

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

# ── 工具函数 ──────────────────────────────────────────────────

def calculate(operation: str, a: float, b: float) -> float:
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "除数不能为0"
    }
    return ops.get(operation, "不支持的运算")

def get_weather(city: str, unit: str = "celsius") -> dict:
    data = {
        "重庆": {"temperature": 32, "condition": "多云"},
        "北京": {"temperature": 28, "condition": "晴"},
        "上海": {"temperature": 30, "condition": "小雨"},
    }
    if city in data:
        return {"city": city, **data[city], "unit": unit}
    return {"error": f"未找到 {city} 的天气数据"}

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
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "description": "温度单位"}
                },
                "required": ["city"]
            }
        }
    }
]


# ── 工具分发 ──────────────────────────────────────────────────

def dispatch_tool(tool_call) -> str:
    """
    根据工具名分发到对应的本地函数
    """
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    if func_name == "calculate":
        result = calculate(**func_args)
    elif func_name == "get_weather":
        result = get_weather(**func_args)
    else:
        result = {"error": f"未知工具：{func_name}"}

    return json.dumps(result, ensure_ascii=False)


def handle_tool_calls(messages: list, response) -> list:
    """
    处理一次响应中的所有工具调用，返回更新后的 messages
    """
    # 把 AI 的 assistant 消息（含 tool_calls）加入 messages
    messages.append(response.choices[0].message)

    # 遍历所有 tool_calls，分发执行，把结果加入 messages
    for tool_call in response.choices[0].message.tool_calls:
        result = dispatch_tool(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result
        })

    return messages


# ── 主循环 ────────────────────────────────────────────────────

def chat_with_tools():
    """
    多轮对话 + 工具调用主循环
    """
    messages = [{"role": "system", "content": "你是一个助手，可以帮用户查天气和做数学计算。"}]
    print("=== 工具聊天（输入 quit 退出）===\n")

    while True:
        user_input = input("你：").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("再见！")
            break

        # 加入用户消息
        messages.append({"role": "user", "content": user_input})

        # 调用 API
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
            messages=messages,
            tools=tools,
        )

        # 处理工具调用（可能需要多轮，直到 AI 不再要求调用工具）
        while response.choices[0].finish_reason == "tool_calls":
            messages = handle_tool_calls(messages, response)
            response = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
                messages=messages,
                tools=tools,
            )

        # 打印最终回答，并加入 messages 历史
        assistant_reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_reply})
        print(f"AI：{assistant_reply}\n")


if __name__ == "__main__":
    chat_with_tools()
