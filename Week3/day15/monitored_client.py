# monitored_client.py
# 练习 4（选做）：usage 监控器
# 目标：封装一个 MonitoredClient，每次调用后自动记录 token 消耗，支持查询累计成本

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week3\day15-practice\.env")


# DeepSeek V4-Flash 参考价格（per million tokens）
PRICING = {
    "claude-sonnet-4-6": {"input": 1.0, "output": 2.0},  # 占位，用来练逻辑
    "deepseek-chat": {"input": 1.0, "output": 2.0},
}


class MonitoredClient:
    """
    带 token 监控的 OpenAI 客户端包装器
    自动记录每次调用的 token 消耗和估算成本
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
        )
        self.call_log = []  # 每次调用的记录

    def chat(self, messages: list, model: str = "claude-sonnet-4-6", **kwargs) -> str:
        """
        调用 API 并自动记录监控数据
        TODO：
        1. 调用 self.client.chat.completions.create
        2. 提取 usage（prompt_tokens/completion_tokens/total_tokens）
        3. 计算本次调用成本（从 PRICING 取价格）
        4. 把记录 append 到 self.call_log：
           {"time": datetime.now().isoformat(), "model": model,
            "prompt_tokens": ..., "completion_tokens": ...,
            "cost_rmb": ...（保留6位小数）}
        5. 返回回复内容
        """
        # 请在这里写代码 ↓
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

        usage = response.usage
        price = PRICING.get(model, {"input": 1.0, "output": 2.0})
        cost = (usage.prompt_tokens / 1_000_000 * price["input"] +
                usage.completion_tokens / 1_000_000 * price["output"])

        self.call_log.append({
            "time": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": usage.prompt_tokens,
            "completion_tokens": usage.completion_tokens,
            "cost_rmb": round(cost, 6)
        })

        return response.choices[0].message.content

    def get_stats(self) -> dict:
        """
        返回汇总统计
        TODO：计算并返回：
        {
            "total_calls": 调用次数,
            "total_prompt_tokens": 累计输入 token,
            "total_completion_tokens": 累计输出 token,
            "total_cost_rmb": 累计成本（保留6位小数）,
            "avg_cost_per_call": 平均每次成本
        }
        """
        # 请在这里写代码 ↓
        total_calls = len(self.call_log)
        total_prompt = sum(r["prompt_tokens"] for r in self.call_log)
        total_completion = sum(r["completion_tokens"] for r in self.call_log)
        total_cost = sum(r["cost_rmb"] for r in self.call_log)

        return {
            "total_calls": total_calls,
            "total_prompt_tokens": total_prompt,
            "total_completion_tokens": total_completion,
            "total_cost_rmb": round(total_cost, 6),
            "avg_cost_per_call": round(total_cost / total_calls, 6) if total_calls > 0 else 0
        }

    def print_report(self):
        """打印统计报告"""
        stats = self.get_stats()
        print("\n" + "=" * 50)
        print("📊 API 调用统计报告")
        print("=" * 50)
        print(f"总调用次数：{stats['total_calls']}")
        print(f"累计输入 Token：{stats['total_prompt_tokens']}")
        print(f"累计输出 Token：{stats['total_completion_tokens']}")
        print(f"累计成本（估算）：¥{stats['total_cost_rmb']:.6f}")
        print(f"平均每次成本：¥{stats['avg_cost_per_call']:.6f}")
        print("=" * 50)


if __name__ == "__main__":
    mc = MonitoredClient()

    questions = [
        "什么是 LangChain？用一句话解释。",
        "什么是 RAG？用一句话解释。",
        "什么是 Agent？用一句话解释。",
    ]

    for q in questions:
        reply = mc.chat(
            messages=[
                {"role": "system", "content": "你是一个 AI 技术助手，回答简洁，每次不超过30字。"},
                {"role": "user", "content": q}
            ],
            temperature=0
        )
        print(f"Q: {q}")
        print(f"A: {reply}\n")

    mc.print_report()
