# contract_analyzer.py
# 练习 2：合同风险分析器（结构化输出）
# 目标：在 ConversationManager 基础上，实现合同条款的结构化风险分析

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
import json
from dotenv import load_dotenv
from conversation import ConversationManager

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week2\day14-practice\.env")

# 合同风险分析的系统提示
CONTRACT_SYSTEM_PROMPT = """你是一名专业的合同风险分析助手。

分析用户提供的合同条款时，必须严格按照以下 JSON 格式返回，不要输出任何其他内容：

{
  "risk_level": "低/中/高",
  "risk_points": ["风险点1", "风险点2"],
  "suggestions": ["建议1", "建议2"],
  "summary": "一句话总结"
}

追问时，仍然保持 JSON 格式回复。"""


class ContractAnalyzer:
    def __init__(self):
        self.conversation = ConversationManager(
            system_prompt=CONTRACT_SYSTEM_PROMPT,
            model="claude-sonnet-4-6"
        )

    def analyze(self, clause: str) -> dict:
        """
        分析合同条款，返回结构化结果
        1. 调用 self.conversation.chat(clause)
        2. 用 json.loads() 解析返回的 JSON 字符串
        3. 如果解析失败，返回 {"error": "解析失败", "raw": 原始回复}
        4. return 解析后的字典
        """
        raw = self.conversation.chat(clause)
        try:
            # 有时模型会在 JSON 前后加 ```json ``` 代码块标记，需要去掉
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, IndexError):
            return {"error": "解析失败", "raw": raw}

    def follow_up(self, question: str) -> dict:
        """
        追问（利用多轮对话历史继续分析）
        逻辑和 analyze 完全一样，传入追问内容
        """
        raw = self.conversation.chat(question)
        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, IndexError):
            return {"error": "解析失败", "raw": raw}

    def get_cost_estimate(self) -> str:
        """估算费用（DeepSeek V4-Flash 价格：输入¥1/输出¥2 per M token）"""
        tokens = self.conversation.get_token_usage()
        # 简化估算：假设输入输出各占一半
        cost = (tokens / 2 / 1_000_000 * 1) + (tokens / 2 / 1_000_000 * 2)
        return f"累计 Token：{tokens}，估算费用（DeepSeek V4-Flash）：¥{cost:.6f}"


# 测试场景
if __name__ == "__main__":
    analyzer = ContractAnalyzer()

    # 第一轮：分析合同条款
    clause = """
    甲方违约时，应赔偿乙方直接损失及预期利润损失，
    赔偿金额不设上限，并承担乙方因此产生的全部诉讼费用。
    """
    print("=" * 60)
    print("合同条款：")
    print(clause)
    print("=" * 60)

    result = analyzer.analyze(clause)
    print("\n分析结果：")
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 第二轮：追问（多轮对话）
    print("\n" + "=" * 60)
    followup = "如果我是甲方，这个条款对我最大的风险是什么？该如何谈判？"
    print(f"追问：{followup}")
    print("=" * 60)

    result2 = analyzer.follow_up(followup)
    print("\n追问结果：")
    print(json.dumps(result2, ensure_ascii=False, indent=2))

    print(f"\n{analyzer.get_cost_estimate()}")
