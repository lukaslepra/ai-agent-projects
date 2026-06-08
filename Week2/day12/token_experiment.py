# 练习 1：Token 认知实验
# 目标：直接感受 token 是什么，数量直观可见
#
# 需要安装：pip install tiktoken

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import tiktoken

# 初始化 GPT-4o 使用的编码器
encoder = tiktoken.encoding_for_model("gpt-4o")

# 准备几段不同的文本
texts = [
    "Hello, world!",
    "你好，世界！",
    "我正在学习Agent开发，目标是做一个合同风险审查系统",
    "def get_response(prompt: str) -> str:",
    "1234567890",
]

for text in texts:
    tokens = encoder.encode(text)
    print(f"文本: {text!r}")
    print(f"Token数: {len(tokens)}")
    print(f"Tokens: {tokens}")
    print("-" * 50)

# 观察：中文每个字大约几个token？
# 答：中文每个字通常 1~2 个 token，不像英文单词那么"划算"
# 例："我正在学习Agent开发，目标是做一个合同风险审查系统" -> 15 个 token，约21个字
