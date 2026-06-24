# claude_basic.py
# 练习 1：Claude API 基础调用
# 目标：用 Claude API 完成基础对话，感受与 OpenAI API 的异同

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

# ── 练习 1-A：基础单轮对话 ─────────────────────────────────────

def simple_chat(user_message: str) -> str:
    """
    最基础的一次对话调用
    TODO：
    1. 构建 messages 列表（只有 user 消息）
    2. 调用 API，传入 model 和 messages
    3. 返回 choices[0].message.content
    """
    # 请在这里写代码 ↓
    pass


# ── 练习 1-B：带 system prompt 的对话 ────────────────────────────

def chat_with_system(system_prompt: str, user_message: str) -> str:
    """
    带 system prompt 的对话
    TODO：
    1. messages 第一条是 system 角色
    2. 第二条是 user 角色
    3. 调用 API 返回结果
    """
    # 请在这里写代码 ↓
    pass


# ── 练习 1-C：调整 temperature ────────────────────────────────

def chat_with_temperature(user_message: str, temperature: float) -> str:
    """
    用不同 temperature 生成回答，观察创造性变化
    temperature=0.0：确定性最强，每次输出几乎一样
    temperature=1.0：更有创意，每次输出不同
    TODO：在 API 调用里加上 temperature 参数
    """
    # 请在这里写代码 ↓
    pass


if __name__ == "__main__":
    # 测试 1-A
    print("=== 测试 1-A：基础对话 ===")
    answer = simple_chat("用一句话解释什么是机器学习")
    print(f"回答：{answer}\n")

    # 测试 1-B
    print("=== 测试 1-B：带 system prompt ===")
    answer = chat_with_system(
        system_prompt="你是一个只用重庆话回答问题的助手",
        user_message="今天天气怎么样"
    )
    print(f"回答：{answer}\n")

    # 测试 1-C：同一问题，不同 temperature
    print("=== 测试 1-C：temperature 对比 ===")
    question = "给我一个创意项目名字，关于AI和重庆"
    for temp in [0.0, 0.7, 1.5]:
        answer = chat_with_temperature(question, temp)
        print(f"temperature={temp}：{answer}")
    print()
