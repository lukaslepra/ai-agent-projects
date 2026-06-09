# 练习 3：模型选择决策函数
# 目标：把"怎么选模型"的框架写成代码
# TODO 部分需要你自己填完

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def select_model(
    budget_sensitive: bool,
    primary_language: str,       # "chinese" 或 "english"
    doc_length: str,             # "short"(<1000字), "medium"(1000-10000字), "long"(>10000字)
    need_reasoning: bool,
    compliance_required: bool,
) -> dict:
    """
    模型选型决策函数（基于2026年6月最新模型）
    主要模型：
      GPT-5.5          - OpenAI旗舰，编程最强，$5/$30 per 1M token
      Claude Opus 4.8  - Anthropic旗舰，推理强，$5/$25 per 1M token
      Claude Sonnet 4.6 - 均衡主力，$3/$15 per 1M token
      DeepSeek V4-Pro  - 极低价，中文强，$0.44/$1.74 per 1M token
      DeepSeek V4-Flash - 最低价，快速，适合高频调用
      Qwen3.7-Max      - 国内合规首选
    """
    """
    根据需求推荐模型

    Returns:
        {"recommended": 模型名, "reason": 推荐原因, "alternative": 备选模型}
    """
    if compliance_required:
        return {
            "recommended": "qwen3.7-max",
            "reason": "有国内数据合规要求，优先选择国内模型",
            "alternative": "ernie-4.0"
        }

    if need_reasoning:
        if budget_sensitive:
            return {
                "recommended": "deepseek-v4-pro",
                "reason": "DeepSeek V4-Pro 推理能力强且价格极低，约为 GPT-5.5 的 1/44",
                "alternative": "claude-sonnet-4.6"
            }
        else:
            return {
                "recommended": "gpt-5.5",
                "reason": "不限预算时，GPT-5.5 编程和推理能力当前最强",
                "alternative": "claude-opus-4.8"
            }

    if doc_length == "long":
        return {
            "recommended": "claude-sonnet-4.6",
            "reason": "长文档处理 Claude 表现最稳定，200K 上下文窗口，性价比优于 Opus",
            "alternative": "gpt-5.5"
        }

    if budget_sensitive:
        if primary_language == "chinese":
            return {
                "recommended": "deepseek-v4-flash",
                "reason": "预算敏感 + 中文场景首选：DeepSeek V4-Flash 全市场价格最低（¥1/¥2 per M token），中文写作胜率62.7%碾压同价位竞品，1M超长上下文足够覆盖大多数业务场景，性价比无敌",
                "alternative": "doubao-seed-2.0-lite"  # 国内合规 + 同样低价，字节生态加成
            }
        else:
            return {
                "recommended": "claude-haiku-4.5",
                "reason": "预算敏感 + 英文场景首选：Claude Haiku 4.5 是 Claude 系列最轻量版本（¥7/¥36 per M token），英文理解和指令遵循能力继承自 Claude 体系，响应速度快，适合高频英文轻量任务",
                "alternative": "qwen-flash"  # 极低价备选，但英文能力稍弱
            }

    return {
        "recommended": "claude-sonnet-4.6",
        "reason": "不限预算的通用场景最优解：编程得分仅比 Claude Opus 4.7 低1.2%，但价格低40%；SWE-bench Pro表现稳定，200K上下文覆盖绝大多数任务，是Anthropic官方主推的生产主力模型",
        "alternative": "gpt-5.5"
    }


# 测试场景
test_cases = [
    {
        "name": "合同风险审查 Agent（我们的项目三）",
        "params": {
            "budget_sensitive": True,
            "primary_language": "chinese",
            "doc_length": "medium",
            "need_reasoning": False,
            "compliance_required": False,
        }
    },
    {
        "name": "法律文书分析（超长合同）",
        "params": {
            "budget_sensitive": False,
            "primary_language": "chinese",
            "doc_length": "long",
            "need_reasoning": False,
            "compliance_required": False,
        }
    },
    {
        "name": "政府采购平台（数据合规）",
        "params": {
            "budget_sensitive": True,
            "primary_language": "chinese",
            "doc_length": "short",
            "need_reasoning": False,
            "compliance_required": True,
        }
    },
    {
        "name": "数学/逻辑题求解应用",
        "params": {
            "budget_sensitive": True,
            "primary_language": "chinese",
            "doc_length": "short",
            "need_reasoning": True,
            "compliance_required": False,
        }
    },
]

print("模型选择决策系统\n")
print("=" * 60)

for case in test_cases:
    result = select_model(**case["params"])
    print(f"\n场景：{case['name']}")
    print(f"  推荐：{result['recommended']}")
    print(f"  原因：{result['reason'] or '（TODO：待填写）'}")
    print(f"  备选：{result['alternative'] or '（TODO：待填写）'}")
