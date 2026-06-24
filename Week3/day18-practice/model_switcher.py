# model_switcher.py
# 练习 4（选做）：带降级策略的模型切换器
# 目标：主模型失败时自动降级到备用模型，保证服务不中断

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

# 模型优先级列表：按顺序尝试，失败就降级到下一个
MODEL_FALLBACK_CHAIN = [
    "claude-sonnet-4-6",   # 首选：效果最好
    "deepseek-chat",        # 备选1：速度快成本低
    "qwen-plus",            # 备选2：兜底
]


# ── 练习 4-A：单次带超时的调用 ────────────────────────────────────

def call_with_timeout(model_id: str, messages: list, timeout: int = 30) -> str:
    """
    调用模型，超过 timeout 秒视为失败（抛出异常）
    TODO：
    1. 调用 API，加上 timeout=timeout 参数（openai SDK 支持 timeout 参数）
    2. 返回回答内容
    3. 不需要自己捕获异常，让异常向上传播（由调用方处理）
    """
    # 请在这里写代码 ↓
    pass


# ── 练习 4-B：自动降级链 ──────────────────────────────────────────

def call_with_fallback(messages: list, timeout: int = 30) -> dict:
    """
    按照 MODEL_FALLBACK_CHAIN 顺序尝试，失败就降级
    TODO：
    1. 遍历 MODEL_FALLBACK_CHAIN
    2. 对每个模型调用 call_with_timeout
    3. 成功：返回 {"model_used": model_id, "content": 回答, "attempts": 尝试次数}
    4. 失败（任何异常）：打印警告，继续尝试下一个模型
    5. 全部失败：返回 {"model_used": None, "content": "所有模型均不可用", "attempts": 尝试次数}
    """
    attempts = 0
    # 请在这里写代码 ↓
    pass


# ── 练习 4-C：带重试的稳定调用 ────────────────────────────────────

def reliable_call(user_message: str, max_retries: int = 3) -> str:
    """
    结合降级 + 重试：整个降级链失败后最多重试 max_retries 次
    TODO：
    1. 构建 messages
    2. 最多重试 max_retries 次调用 call_with_fallback
    3. 成功：打印"第X次尝试成功，使用模型：XXX"并返回内容
    4. 失败：等待 2 秒后重试（time.sleep(2)）
    5. 全部重试失败：返回 "服务暂时不可用，请稍后再试"
    """
    # 请在这里写代码 ↓
    pass


if __name__ == "__main__":
    # 测试 4-B：正常降级
    print("=== 测试 4-B：降级调用 ===")
    messages = [{"role": "user", "content": "你好，今天学了什么？"}]
    result = call_with_fallback(messages)
    print(f"使用模型：{result['model_used']} | 尝试次数：{result['attempts']}")
    print(f"回答：{result['content']}\n")

    # 测试 4-C：稳定调用
    print("=== 测试 4-C：稳定调用 ===")
    answer = reliable_call("用一句话总结 Function Calling 的核心价值")
    print(f"最终回答：{answer}\n")
