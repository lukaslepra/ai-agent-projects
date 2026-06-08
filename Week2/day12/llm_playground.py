# 练习 5：综合小程序 - "LLM实验台"
# 把前四个练习合成一个交互式小程序
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

def run_playground():
    """交互式 LLM 实验台"""

    print("=" * 60)
    print("LLM 实验台")
    print("=" * 60)

    # 获取用户配置
    system_prompt = input("输入 System Prompt（直接回车用默认）: ").strip()
    if not system_prompt:
        system_prompt = "你是一个助手。"

    temp_input = input("输入 Temperature (0.0-2.0，默认0.7): ").strip()
    try:
        temperature = float(temp_input) if temp_input else 0.7
    except ValueError:
        temperature = 0.7

    print(f"\n配置：System='{system_prompt[:30]}...' | Temperature={temperature}")
    print("开始提问，输入 'quit' 退出\n")

    messages = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == "quit":
            print("实验结束。")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=500,
        )

        reply = response.choices[0].message.content
        usage = response.usage

        messages.append({"role": "assistant", "content": reply})

        print(f"\nAI: {reply}")
        print(f"[Token: 输入={usage.prompt_tokens}, 输出={usage.completion_tokens}]\n")

if __name__ == "__main__":
    run_playground()
