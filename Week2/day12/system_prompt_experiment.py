# 练习 3：System Prompt 实验
# 目标：感受 System Prompt 如何改变模型行为
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

def chat_with_system(system_prompt: str, user_message: str) -> str:
    """带 system prompt 的对话"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content

# 同一个问题，用三种不同的 system prompt
user_question = "合同违约了，我应该怎么处理？"

system_prompts = {
    "普通助手": "你是一个助手。",

    "专业律师": (
        "你是一位拥有15年经验的合同律师。"
        "回答要专业且简洁，使用法律术语。"
        "指出潜在风险，并给出修改建议。"
    ),

    "通俗解释": (
        "你是一位专门给普通人解释法律的顾问。"
        "使用最简单的语言，避免法律术语。"
        "回答控制在100字以内。"
    ),
}

for name, system in system_prompts.items():
    print(f"\n{'='*60}")
    print(f"System Prompt 类型：{name}")
    print(f"{'='*60}")
    result = chat_with_system(system, user_question)
    print(result)

# 观察结论：
# 1. System Prompt 能控制什么？
#    -> System Prompt 能设定 AI 的角色、语言风格、专业程度和回答边界
# 2. 三种不同的 System Prompt 有什么差异？
#    -> 普通助手：通用回答；专业律师：专业术语+风险提示；通俗解释：简洁易懂
# 3. 这个实验证明了什么？
#    -> 同一问题，不同角色设定能得到完全不同的回答，System Prompt 是控制模型行为最有效的方式
