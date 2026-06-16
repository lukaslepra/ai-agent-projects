# multi_turn.py
# 练习 2：多轮对话管理
# 目标：实现带历史记忆的多轮对话，验证 AI 能记住之前说过的内容

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day16-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

SYSTEM_PROMPT = "你是一个助手，回答简洁，每次不超过50字。"


def chat_once(messages: list) -> str:
    """
    单次调用，返回回复内容
    TODO：调用 API，temperature=0，返回 content
    """
    # 请在这里写代码 ↓
    response = client.chat.completions.create(
        model="claude-sonnet-4-6",
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content


def run_conversation(turns: list) -> None:
    """
    运行多轮对话
    turns: [{"user": "...", "note": "..."}, ...]

    TODO：
    1. 初始化 messages，加入 system prompt
    2. 遍历每一轮：
       a. 把 user 消息 append 到 messages
       b. 调用 chat_once(messages) 得到回复
       c. 把 assistant 回复 append 到 messages
       d. 打印对话内容
    3. 打印最终 messages 长度（验证历史在累积）
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 请在这里写代码 ↓
    for i, turn in enumerate(turns):
        # 把用户输入加入历史
        messages.append({"role": "user", "content": turn["user"]})

        # 调用 API
        reply = chat_once(messages)

        # 把 AI 回复加入历史
        messages.append({"role": "assistant", "content": reply})

        # 打印对话
        print(f"第{i+1}轮 [{turn['note']}]")
        print(f"你：{turn['user']}")
        print(f"AI：{reply}")
        print()

    print(f"--- 对话结束，messages 共 {len(messages)} 条（包含 system）---")


if __name__ == "__main__":
    print("=== 多轮对话测试 ===\n")

    # 测试场景：验证 AI 能记住之前的信息
    conversation = [
        {"user": "我叫黑米，我在学习 Python。", "note": "告知姓名和学习内容"},
        {"user": "我今天完成了第16天的练习。", "note": "告知进度"},
        {"user": "你还记得我叫什么吗？我在学什么？", "note": "验证记忆"},
        {"user": "我今天完成了哪一天的练习？", "note": "验证进度记忆"},
    ]

    run_conversation(conversation)
