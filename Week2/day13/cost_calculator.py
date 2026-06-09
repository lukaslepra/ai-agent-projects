# 练习 2：费用计算器
# 目标：写一个函数，输入模型名和 token 数，输出预估费用

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# 模型价格表（人民币/百万token，2026年6月数据）
# 美元汇率按 1 USD ≈ 7.25 RMB 换算
PRICING = {
    # OpenAI
    "gpt-5.5":              {"input": 36,   "output": 218},
    "gpt-5.5-pro":          {"input": 218,  "output": 1305},
    # Anthropic
    "claude-opus-4.8":      {"input": 36,   "output": 181},
    "claude-sonnet-4.6":    {"input": 22,   "output": 109},
    "claude-haiku-4.5":     {"input": 7,    "output": 36},
    # DeepSeek
    "deepseek-v4-pro":      {"input": 13,   "output": 25},
    "deepseek-v4-flash":    {"input": 1,    "output": 2},
    # 豆包（字节跳动）
    "doubao-seed-2.0-pro":  {"input": 3.2,  "output": 16},
    "doubao-seed-2.0-lite": {"input": 0.6,  "output": 3.6},
    # 千问（阿里云）
    "qwen3.7-max":          {"input": 12,   "output": 36},
    "qwen3.7-plus":         {"input": 2,    "output": 8},
    "qwen-plus":            {"input": 0.8,  "output": 2},
    "qwen-flash":           {"input": 0.1,  "output": 0.4},
    # 智谱（GLM）
    "glm-5":                {"input": 2.2,  "output": 10.9},
    "glm-4.5":              {"input": 0.8,  "output": 2},
    # Claude Opus 4.7（新增）
    "claude-opus-4.7":      {"input": 109,  "output": 544},  # $15/$75 per 1M token
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    计算 API 调用费用（人民币）

    Args:
        model: 模型名称
        input_tokens: 输入 token 数
        output_tokens: 输出 token 数

    Returns:
        费用（元），模型不存在时返回 -1.0
    """
    if model not in PRICING:
        return -1.0

    price = PRICING[model]
    cost = (input_tokens / 1_000_000 * price["input"]) + \
           (output_tokens / 1_000_000 * price["output"])
    return cost


def compare_models_cost(input_tokens: int, output_tokens: int):
    """对比所有模型的费用，从低到高排序"""
    print(f"输入 {input_tokens} tokens + 输出 {output_tokens} tokens 的费用对比：\n")

    results = [(model, calculate_cost(model, input_tokens, output_tokens))
               for model in PRICING]
    results.sort(key=lambda x: x[1])

    # 免费模型单独列出，付费模型按价格排序对比
    free_models = [(m, c) for m, c in results if c == 0]
    paid_models = [(m, c) for m, c in results if c > 0]

    if free_models:
        for model, _ in free_models:
            print(f"  {model:<25} 【免费】")

    if paid_models:
        cheapest_cost = paid_models[0][1]
        for model, cost in paid_models:
            ratio = cost / cheapest_cost
            bar = "█" * min(int(ratio * 10), 80)
            print(f"  {model:<25} ¥{cost:.4f}  {bar} ({ratio:.1f}x)")


# 场景1：简单问答
print("=" * 60)
print("场景1：简单问答（输入500 + 输出200 tokens）")
print("=" * 60)
compare_models_cost(500, 200)

# 场景2：合同审查
print("\n" + "=" * 60)
print("场景2：合同审查（输入8000 + 输出1500 tokens）")
print("=" * 60)
compare_models_cost(8000, 1500)

# 场景3：每天1000次批量调用的月度费用
print("\n" + "=" * 60)
print("场景3：每天1000次合同审查的月度费用估算")
print("=" * 60)
print()
for model in PRICING:
    daily = calculate_cost(model, 8000, 1500) * 1000
    monthly = daily * 30
    print(f"  {model:<25} 日费用≈¥{daily:.1f}  月费用≈¥{monthly:.0f}")
