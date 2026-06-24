# Week 3 Day 17 - LLM API实战：Function Calling / Tool Use

> 学员：黑米 | 日期：2026-06-17 | 每日投入：8小时
> **昨天你学会了流式输出和多轮对话，今天学 Function Calling——这是从"聊天机器人"迈向"Agent"的关键一步**

---

## 上午：概念学习（3小时）

### 1. 什么是 Function Calling

普通 LLM 调用是这样的：
```
你问 → AI 用文字回答
```

Function Calling 是这样的：
```
你问 → AI 决定调用哪个函数 → 你执行这个函数 → 把结果返回给 AI → AI 给出最终回答
```

**核心思想：** AI 不直接执行代码，它只是"决策者"——告诉你该调用什么函数、传什么参数。真正执行的是你的 Python 代码。

**为什么重要？**
- 让 AI 能访问实时数据（天气、股价、数据库）
- 让 AI 能操作外部系统（发邮件、查日历、写文件）
- 这就是 Agent 工具调用的底层机制

---

### 2. Function Calling 的完整流程

```
第一步：定义工具
你告诉 API："我有这些工具，每个工具能做什么、需要什么参数"

第二步：发请求
把工具定义 + 用户消息一起发给 API

第三步：AI 决策
AI 判断是否需要调用工具，如果需要：
  返回 finish_reason="tool_calls"，包含工具名和参数
  如果不需要：直接返回文字回答

第四步：你执行函数
拿到 AI 的工具调用请求，在本地执行对应的 Python 函数

第五步：把结果还给 AI
把函数执行结果作为 tool 角色消息加入 messages，再次调用 API

第六步：AI 给出最终回答
AI 看到工具执行结果后，生成最终的自然语言回复
```

---

### 3. 工具定义格式

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",           # 函数名，AI 用这个名字调用
            "description": "获取指定城市的当前天气",  # 告诉 AI 这个工具能干什么
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：重庆、北京"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "温度单位"
                    }
                },
                "required": ["city"]          # 必填参数
            }
        }
    }
]
```

**关键点：**
- `description` 要写清楚，AI 靠这个决定用不用这个工具
- `parameters` 用 JSON Schema 格式描述参数
- `required` 列出必填参数，其余为可选

---

### 4. 解析 AI 的工具调用响应

```python
response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=messages,
    tools=tools,
)

# 判断 AI 是否要调用工具
if response.choices[0].finish_reason == "tool_calls":
    tool_calls = response.choices[0].message.tool_calls
    
    for tool_call in tool_calls:
        func_name = tool_call.function.name        # 工具名："get_weather"
        func_args = json.loads(tool_call.function.arguments)  # 参数：{"city": "重庆"}
        tool_call_id = tool_call.id                # 每次调用的唯一 ID
        
        # 执行本地函数
        result = get_weather(**func_args)
        
        # 把结果加入 messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,   # 必须对应上
            "content": str(result)
        })
```

---

### 5. 多工具 + 并行调用

AI 可以在一次响应中请求调用多个工具（parallel tool calls）：

```python
# AI 可能同时请求：get_weather("重庆") + get_weather("北京")
for tool_call in response.choices[0].message.tool_calls:
    # 逐个处理，每个都要加入 messages
    result = dispatch_tool(tool_call)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
    })
```

**注意：** 所有工具结果都加入 messages 后，才能发下一次请求。

---

### 6. tool_choice 参数

控制 AI 是否必须调用工具：

```python
# 默认：AI 自己决定
tool_choice="auto"

# 强制不调用任何工具
tool_choice="none"

# 强制调用某个特定工具
tool_choice={"type": "function", "function": {"name": "get_weather"}}
```

---

### 7. 今天要做什么

**计算器 Agent**：给 AI 配备加减乘除工具，让它能做数学计算，理解 Function Calling 的完整循环。

**信息查询 Agent**：给 AI 配备多个查询工具（天气、汇率、时间），让它根据问题自动选择调用哪个工具。

---

## 下午：实操练习（4小时）

练习文件放在：`E:\Agent岗位培训\Week3\day17-practice\`

---

### 练习 1：基础 Function Calling——计算器

打开 `E:\Agent岗位培训\Week3\day17-practice\calculator_agent.py`

**目标：** 实现完整的 Function Calling 循环，让 AI 调用本地计算函数完成数学题。

```python
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
    # 请在这里写代码 ↓
    # 提示：用 if/elif 分支处理四种运算，除法注意 b==0 的情况
    pass


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

    TODO：
    1. 初始化 messages，加入 user 问题
    2. 第一次调用 API（传入 tools 参数）
    3. 检查 finish_reason 是否为 "tool_calls"
    4. 如果是：
       a. 把 AI 的 assistant 消息加入 messages（包含 tool_calls）
       b. 解析 tool_call：拿到 func_name、func_args、tool_call_id
       c. 调用 calculate(**func_args)
       d. 把结果作为 tool 角色消息加入 messages
       e. 第二次调用 API 拿最终回答
    5. 返回最终回答内容
    """
    messages = [{"role": "user", "content": user_question}]
    # 请在这里写代码 ↓
    pass


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
```

---

### 练习 2：多工具选择

打开 `E:\Agent岗位培训\Week3\day17-practice\multi_tool_agent.py`

**目标：** 给 AI 配备多个工具，让它根据问题内容自动选择调用哪个。

```python
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
    # 请在这里写代码 ↓
    # 用字典存几个城市的模拟天气数据，返回对应城市的数据
    # 格式：{"city": city, "temperature": 数字, "condition": "晴/多云/小雨", "unit": unit}
    # 如果城市不在字典里，返回 {"error": f"未找到 {city} 的天气数据"}
    pass


def get_exchange_rate(from_currency: str, to_currency: str) -> dict:
    """模拟汇率查询"""
    # 请在这里写代码 ↓
    # 用字典存几组汇率：USD/CNY=7.25, EUR/CNY=7.85, JPY/CNY=0.048
    # 支持正向和反向查询
    # 格式：{"from": from_currency, "to": to_currency, "rate": 数字, "note": "说明"}
    pass


def get_current_time(timezone: str = "Asia/Shanghai") -> dict:
    """获取当前时间"""
    # 请在这里写代码 ↓
    # 用 datetime.now() 获取当前时间
    # 格式：{"timezone": timezone, "datetime": 格式化时间字符串, "weekday": 星期几}
    pass


# ── 工具定义 ──────────────────────────────────────────────────

tools = [
    # 请在这里写代码 ↓
    # 参考练习1的格式，为 get_weather、get_exchange_rate、get_current_time
    # 各写一个工具定义，description 要清晰说明用途
]


# ── 工具分发函数 ───────────────────────────────────────────────

def dispatch_tool(tool_call) -> str:
    """
    根据工具名分发到对应的本地函数
    TODO：
    1. 解析 tool_call.function.name 和 arguments
    2. 用 if/elif 分支调用对应函数
    3. 返回 json.dumps(result, ensure_ascii=False)
    """
    # 请在这里写代码 ↓
    pass


# ── 主逻辑 ────────────────────────────────────────────────────

def ask(question: str) -> str:
    """
    支持多工具的 Function Calling 循环
    TODO：同练习1，但工具调用可能有多个（用 for 循环处理所有 tool_calls）
    """
    messages = [{"role": "user", "content": question}]
    # 请在这里写代码 ↓
    pass


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
```

---

### 练习 3：Function Calling + 流式输出

打开 `E:\Agent岗位培训\Week3\day17-practice\tool_stream.py`

**目标：** 把 Function Calling 和流式输出结合，最终回答用流式打印。

```python
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

# 复用练习2的工具函数和工具定义（直接 import 或复制过来）
# 这里用一个简单的计算工具演示

def calculate(operation: str, a: float, b: float) -> float:
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b != 0 else "除数不能为0"}
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

    TODO：
    1. 第一次非流式调用（检查是否需要工具）
    2. 如果需要工具：执行工具，把结果加入 messages
    3. 第二次调用加上 stream=True，流式打印最终回答
    4. 如果不需要工具：直接打印第一次的回答
    """
    messages = [{"role": "user", "content": question}]
    # 请在这里写代码 ↓
    pass


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
```

---

### 练习 4（选做）：带工具调用的多轮对话

打开 `E:\Agent岗位培训\Week3\day17-practice\tool_chat.py`

**目标：** 在多轮对话中集成工具调用，AI 可以在连续对话里随时使用工具。

```python
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

# 工具函数（复用练习2的）
def calculate(operation: str, a: float, b: float) -> float:
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b if b != 0 else "除数不能为0"}
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


def handle_tool_calls(messages: list, response) -> list:
    """
    处理一次响应中的所有工具调用，返回更新后的 messages
    TODO：
    1. 把 AI 的 assistant 消息（含 tool_calls）加入 messages
    2. 遍历所有 tool_calls，分发执行，把结果加入 messages
    3. 返回更新后的 messages
    """
    # 请在这里写代码 ↓
    pass


def chat_with_tools():
    """
    多轮对话 + 工具调用主循环
    TODO：
    1. 维护 messages 历史（含 system prompt）
    2. 每轮：读取用户输入 → 调用 API → 处理工具调用（如有）→ 打印最终回答
    3. 支持 quit 退出
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

        # 请在这里写代码 ↓
        pass


if __name__ == "__main__":
    chat_with_tools()
```

---

## 晚上：复盘（1小时）

### 复盘问题（用自己的话回答，发给我检查）

1. **Function Calling 的完整流程是什么？AI 在这个过程中扮演什么角色，你的代码扮演什么角色？**

   Function Calling 的完整流程分六步：第一步，在工具定义里告诉 API「我有哪些工具、每个工具需要什么参数」；第二步，把工具定义和用户消息一起发给 API；第三步，AI 判断是否需要调用工具，如果需要就返回 `finish_reason="tool_calls"` 和具体的工具名+参数，如果不需要就直接返回文字；第四步，代码拿到工具调用请求后，执行对应的本地 Python 函数；第五步，把函数执行结果作为 `role: tool` 的消息加回 messages；第六步，再次调用 API，AI 看到工具结果后生成最终的自然语言回复。

   AI 是"决策者"——它只决定调用什么工具、传什么参数，不执行代码；代码是"执行者"——真正跑函数、拿结果、维护消息历史。

2. **为什么第一次调用 API 不能直接用 stream=True（当需要工具调用时）？**

   因为流式模式下，工具调用的参数 `arguments` 是分片 chunk 逐步返回的，需要手动拼接才能得到完整的 JSON 字符串，然后才能解析并执行工具。如果直接用 `stream=True` 但没有正确拼接参数，就无法获得完整的 `tool_call_id` 和 `arguments`，工具根本没法调用。所以最简单的做法是：第一次用非流式拿到完整的工具调用信息，执行工具，第二次（最终回答）再用 `stream=True` 流式输出。

3. **`tool_call_id` 是干什么用的？如果有多个工具调用，它怎么保证对应关系不乱？**

   `tool_call_id` 是每次工具调用的唯一 ID，由 API 生成。当 AI 请求多个工具调用时（比如同时查北京和上海的天气），每个调用都有独立的 ID。把工具结果加回 messages 时，必须带上对应的 `tool_call_id`，这样 AI 才知道"这个结果是对应哪一次工具调用的"。如果 ID 对不上，API 会报错，因为 AI 无法正确关联请求和结果。

4. **工具的 `description` 字段为什么很重要？如果写得很模糊会发生什么？**

   AI 完全靠 `description` 来判断「什么时候该用这个工具」。如果 description 写得模糊，AI 可能：选错工具（把查天气的问题发给计算工具）、该用工具时不用（觉得不相关）、或者乱用工具（把不需要工具的问题也触发工具调用）。比如把 get_weather 的 description 写成「获取信息」，AI 可能对任何问题都尝试调用它。description 是 AI 理解工具能力的唯一依据，要写得准确、具体。

5. **面试题（Week 3 第3题，书面作答）：**

   面试官问："请描述一下你实现过的 Function Calling，遇到了什么问题，怎么解决的？"

   **S（Situation）：** 在学习 LLM API 实战阶段，需要把 AI 从单纯的文字问答升级成能调用外部工具的 Agent，核心就是实现 Function Calling。

   **T（Task）：** 需要实现一个多工具 Agent，让 AI 根据用户问题自动选择调用天气查询、汇率换算或时间查询工具，同时还要把 Function Calling 和流式输出结合起来。

   **A（Action）：** 按照完整的 Function Calling 循环来实现：先用 JSON Schema 格式定义工具（每个工具的 name、description、parameters），第一次非流式调用 API 检查 finish_reason，如果是 tool_calls 就取出工具名和 arguments 执行本地函数，把结果以 `role: tool` 加回 messages，再第二次调用 API 拿最终回答。对于多工具并行调用（比如同时查两个城市天气），用 for 循环遍历所有 tool_calls，逐一执行并加入结果。遇到的主要问题是流式输出时工具调用的处理——如果第一次就用 `stream=True`，arguments 会被拆成碎片，拼接起来很麻烦，所以改成「第一次非流式判断是否需要工具，第二次再用流式输出最终回答」，问题解决。

   **R（Result）：** 最终实现了四个练习：基础计算器 Agent、多工具选择 Agent、Function Calling + 流式输出，以及支持多轮对话的工具聊天。整个 Function Calling 循环跑通，AI 能准确根据问题选择工具、执行并返回自然语言结果。

---

### 完成后 Git 提交（PR 方式）

```bash
git checkout -b day17-function-calling
git add Week3/day17/
git commit -m "Day17: Function Calling / Tool Use 练习完成"
git push -u origin day17-function-calling
# 在 GitHub 上创建 PR，self-review 后 merge
```

---

### 向我汇报

完成练习后把复盘答案（含面试题作答）发给我，我来检查并给出反馈。
