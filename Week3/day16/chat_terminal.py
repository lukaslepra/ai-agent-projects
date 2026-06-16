# chat_terminal.py
# 练习 3：滑动窗口 + 流式对话终端
# 目标：把 streaming + 多轮对话 + 滑动窗口组合，做一个可以真正使用的终端聊天程序

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

SYSTEM_PROMPT = "你是一个有帮助的助手，回答简洁清晰。"
MAX_TURNS = 5  # 最多保留最近5轮对话


def trim_history(messages: list, max_turns: int) -> list:
    """
    保留 system prompt + 最近 max_turns 轮（user+assistant各一条=一轮）
    TODO：
    1. 分离 system 消息和非 system 消息
    2. 非 system 消息只保留最后 max_turns*2 条
    3. 返回 system + 保留的消息
    """
    # 请在这里写代码 ↓
    system_msgs = [m for m in messages if m["role"] == "system"]
    other_msgs = [m for m in messages if m["role"] != "system"]
    trimmed = other_msgs[-(max_turns * 2):]
    return system_msgs + trimmed


def stream_chat(messages: list) -> str:
    """
    流式调用，逐字打印，返回完整回复
    TODO：同练习1的 stream_response，但接收完整 messages 列表
    """
    full_content = ""
    # 请在这里写代码 ↓
    response = client.chat.completions.create(
        model="claude-sonnet-4-6",
        messages=messages,
        stream=True
    )
    for chunk in response:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            print(delta, end="", flush=True)
            full_content += delta
    print()
    return full_content


def run_chat():
    """
    主循环：读取用户输入 → 流式回复 → 维护历史 → 滑动窗口裁剪
    输入 'quit' 或 'exit' 退出
    输入 'history' 查看当前对话历史长度
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("=== 终端聊天（输入 quit 退出，history 查看历史）===\n")

    while True:
        user_input = input("你：").strip()

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("再见！")
            break
        if user_input.lower() == "history":
            non_system = [m for m in messages if m["role"] != "system"]
            print(f"[当前历史：{len(non_system)} 条消息，约 {len(non_system)//2} 轮对话]\n")
            continue

        # TODO：
        # 1. 把用户输入 append 到 messages
        # 2. 调用 trim_history 裁剪（裁剪后再调用 API，避免超长）
        # 3. 打印 "AI：" 后调用 stream_chat 流式输出
        # 4. 把 AI 回复 append 到 messages（注意：append 到原始 messages，不是裁剪后的）
        # 请在这里写代码 ↓
        messages.append({"role": "user", "content": user_input})
        trimmed = trim_history(messages, MAX_TURNS)
        print("AI：", end="")
        reply = stream_chat(trimmed)
        messages.append({"role": "assistant", "content": reply})


if __name__ == "__main__":
    run_chat()
