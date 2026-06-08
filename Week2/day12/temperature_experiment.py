# 练习 2：Temperature 对比实验
# 目标：亲眼看到 temperature 如何影响输出
#
# 需要安装：pip install openai python-dotenv
# 运行前确认 .env 文件在同目录下

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# 修复 Windows 中文输出乱码
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 加载 .env 文件
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

model = os.getenv("MODEL_NAME", "claude-sonnet-4-6")

# 用同一个 prompt 测试不同 temperature
prompt = "给我写一句描述重庆的句子"

temperatures = [0.0, 0.7, 1.5]

print(f"Prompt: {prompt}\n")
print("=" * 60)

for temp in temperatures:
    print(f"\n【Temperature = {temp}】")
    
    # 同一个 temperature 跑 3 次，观察稳定性
    for i in range(3):
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temp,
            max_tokens=100,
        )
        result = response.choices[0].message.content.strip()
        print(f"  第{i+1}次: {result}")
    
    print("-" * 60)

print("\n实验结论：")
print("  temperature=0.0 → 每次输出几乎一样（确定性强）")
print("  temperature=0.7 → 有一定变化（均衡）")
print("  temperature=1.5 → 变化明显，有时天马行空（创造性强）")
