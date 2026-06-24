# model_compare.py
# 练习 2：多模型对比调用
# 目标：用同一套代码调用不同模型，对比响应速度和回答风格

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day18-practice\.env")

client = OpenAI(
    api_key=***"OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 今天可用的模型列表（都走同一个 base_url，用 兼容层 调用）
MODELS = {
    "claude-sonnet-4-6": "Claude Sonnet（默认）",
    "deepseek-chat": "DeepSeek V3",
    "qwen-plus": "通义千问 Plus",
}


# ── 练习 2-A：封装通用调用函数 ────────────────────────────────────

def call_model(model_id: str, messages: list, temperature: float = 0.7) -> dict:
    """
    通用模型调用函数，返回包含结果和耗时的字典
    TODO：
    1. 记录开始时间 time.time()
    2. 调用 API，指定 model=model_id
    3. 记录结束时间，计算耗时
    4. 返回 {"model": model_id, "content": 回答内容, "elapsed": 耗时秒数}
    """
    # 请在这里写代码 ↓
    pass


# ── 练习 2-B：多模型横向对比 ──────────────────────────────────────

def compare_models(question: str) -> None:
    """
    用所有模型回答同一个问题，打印对比结果
    TODO：
    1. 遍历 MODELS 字典
    2. 对每个模型调用 call_model
    3. 打印：模型名 | 耗时 | 回答内容（截取前100字）
    提示：如果某个模型调用失败（try/except），打印错误信息并继续下一个
    """
    print(f"问题：{question}")
    print("=" * 60)
    # 请在这里写代码 ↓
    pass


# ── 练习 2-C：模型路由器（按任务选模型）────────────────────────────

def route_and_call(task_type: str, user_message: str) -> str:
    """
    根据任务类型自动选择模型
    路由规则：
    - "creative"（创意写作）→ claude-sonnet-4-6，temperature=1.2
    - "code"（代码任务）    → deepseek-chat，temperature=0.2
    - "chat"（普通对话）    → qwen-plus，temperature=0.7
    - 其他                 → claude-sonnet-4-6，temperature=0.7

    TODO：
    1. 用 if/elif 实现路由逻辑，选择 model_id 和 temperature
    2. 构建 messages
    3. 调用 call_model，返回 content
    """
    # 请在这里写代码 ↓
    pass


if __name__ == "__main__":
    # 测试 2-B：多模型对比
    print("=== 测试 2-B：多模型对比 ===\n")
    compare_models("用一句话解释什么是 Agent？")

    # 测试 2-C：模型路由
    print("\n=== 测试 2-C：模型路由 ===\n")
    tasks = [
        ("creative", "写一首关于重庆火锅的俳句"),
        ("code", "用 Python 写一个快速排序函数"),
        ("chat", "今天学了 Function Calling，感觉很有意思"),
    ]
    for task_type, message in tasks:
        print(f"任务类型：{task_type}")
        result = route_and_call(task_type, message)
        print(f"回答：{result}\n" + "-" * 40)
