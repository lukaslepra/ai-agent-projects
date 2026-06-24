# multi_tool_agent.py
# 练习 2：多工具选择
# 目标：配备多个工具，AI 自动判断用哪个

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day17-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# ── 模拟工具函数（实际项目里这里会真正调用外部 API）──────────────

def get_weather(city: str, unit: str = "celsius") -> dict:
    """模拟天气查询"""
    weather_data = {
        "重庆": {"temperature": 32, "condition": "多云"},
        "北京": {"temperature": 28, "condition": "晴"},
        "上海": {"temperature": 30, "condition": "小雨"},
        "成都": {"temperature": 27, "condition": "阴"},
        "广州": {"temperature": 35, "condition": "晴"},
    }
    if city in weather_data:
        return {
            "city": city,
            "temperature": weather_data[city]["temperature"],
            "condition": weather_data[city]["condition"],
            "unit": unit
        }
    return {"error": f"未找到 {city} 的天气数据"}


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """模拟汇率查询"""
    # 基础汇率（以CNY为基准）
    rates_to_cny = {
        "USD": 7.25,
        "EUR": 7.85,
        "JPY": 0.048,
        "CNY": 1.0,
    }

    from_c = from_currency.upper()
    to_c = to_currency.upper()

    if from_c not in rates_to_cny or to_c not in rates_to_cny:
        return {"error": f"不支持的货币：{from_currency} 或 {to_currency}"}

    # 先转为CNY，再转为目标货币
    rate = rates_to_cny[from_c] / rates_to_cny[to_c]
    return {
        "from": from_c,
        "to": to_c,
        "rate": round(rate, 4),
        "note": f"1 {from_c} = {round(rate, 4)} {to_c}"
    }


def get_current_time(timezone: str = "Asia/Shanghai") -> dict:
    """获取当前时间"""
    now = datetime.now()
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    return {
        "timezone": timezone,
        "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": weekdays[now.weekday()]
    }


# ── 工具定义 ──────────────────────────────────────────────────

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的当前天气情况，包括温度和天气状况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：重庆、北京、上海"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位：celsius摄氏度、fahrenheit华氏度，默认celsius"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "查询两种货币之间的实时汇率，支持 USD、EUR、JPY、CNY",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "源货币代码，例如：USD、EUR、JPY、CNY"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "目标货币代码，例如：USD、EUR、JPY、CNY"
                    }
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "时区，例如：Asia/Shanghai，默认为 Asia/Shanghai"
                    }
                },
                "required": []
            }
        }
    }
]


# ── 工具分发函数 ───────────────────────────────────────────────

def dispatch_tool(tool_call) -> str:
    """
    根据工具名分发到对应的本地函数
    """
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    if func_name == "get_weather":
        result = get_weather(**func_args)
    elif func_name == "get_exchange_rate":
        result = get_exchange_rate(**func_args)
    elif func_name == "get_current_time":
        result = get_current_time(**func_args)
    else:
        result = {"error": f"未知工具：{func_name}"}

    return json.dumps(result, ensure_ascii=False)


# ── 主逻辑 ────────────────────────────────────────────────────

def ask(question: str) -> str:
    """
    支持多工具的 Function Calling 循环
    工具调用可能有多个，用 for 循环处理所有 tool_calls
    """
    messages = [{"role": "user", "content": question}]

    # 第一次调用 API
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
        messages=messages,
        tools=tools,
    )

    # 检查是否需要调用工具
    if response.choices[0].finish_reason == "tool_calls":
        # 把 AI 的 assistant 消息加入 messages
        messages.append(response.choices[0].message)

        # 遍历所有工具调用（可能有多个，如同时查北京和上海天气）
        for tool_call in response.choices[0].message.tool_calls:
            result = dispatch_tool(tool_call)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

        # 第二次调用拿最终回答
        final_response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "claude-sonnet-4-6"),
            messages=messages,
            tools=tools,
        )
        return final_response.choices[0].message.content

    return response.choices[0].message.content


if __name__ == "__main__":
    questions = [
        "重庆今天天气怎么样？",
        "现在几点了？",
        "1000美元能换多少人民币？",
        "北京和上海的天气分别是怎样的？",  # 这个会触发两次工具调用
    ]

    for q in questions:
        print(f"问：{q}")
        answer = ask(q)
        print(f"答：{answer}\n")
        print("=" * 50)
