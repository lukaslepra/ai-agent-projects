# 练习 1：多模型横向对比
# 目标：用同一个 prompt 调用两个模型，观察输出差异
#
# 需要：pip install openai python-dotenv

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 小马代理（Claude）
claude_client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# DeepSeek 直连
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
)

def ask_model(client, model: str, prompt: str, system: str = "你是一个助手。") -> tuple:
    """调用指定模型，返回 (回复内容, token用量)"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=300,
    )
    return response.choices[0].message.content, response.usage

# 同一个问题测试两个模型
test_prompt = "请用3句话解释什么是RAG（检索增强生成），并举一个实际应用场景。"

models = [
    (claude_client,    "claude-sonnet-4-6", "Claude Sonnet 4.6（小马代理）"),
    (deepseek_client,  "deepseek-v4-flash", "DeepSeek V4 Flash（直连）"),
]

print(f"测试 Prompt：{test_prompt}\n")
print("=" * 70)

for client, model_id, label in models:
    print(f"\n【{label}】")
    try:
        content, usage = ask_model(client, model_id, test_prompt)
        print(content)
        print(f"\n[Token：输入={usage.prompt_tokens}, 输出={usage.completion_tokens}]")
    except Exception as e:
        print(f"调用失败：{e}")
    print("-" * 70)

# 看完结果，思考：
# 1. 两个模型的回答质量有差异吗？
# 2. 用在合同审查项目里你会选哪个？
