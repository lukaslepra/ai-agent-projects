# Week 2 Day 14 - 复习 + 小项目：多轮对话 LLM API + pytest 断言验证

> 学员：黑米 | 日期：2026-06-09 | 每日投入：8小时
> **Week 2 收官日**：把两周所有内容串起来，造出第一个真正能用的 LLM 对话项目

---

## 上午：概念复习（3小时）

今天不学新知识。把 Week 1-2 的核心内容快速串一遍，然后用一个完整项目把它们全用上。

---

### 1. Week 2 核心知识速查表

#### Python 进阶部分

| 知识点 | 一句话核心 | Agent 开发用在哪 |
|--------|-----------|----------------|
| 类和对象（Day 8） | 用 class 封装数据和方法，`__init__` 是构造函数 | LangChain 里每个 Chain、Agent、Tool 都是类 |
| 异步编程（Day 9） | `async def` + `await` 让 IO 不阻塞，`asyncio.gather` 并发 | 同时调用多个 LLM API，速度快3-5倍 |
| 虚拟环境/Git（Day 10） | `venv` 隔离依赖，feature branch 提交代码 | 每个项目独立环境，PR 提交作业 |
| HTTP/requests（Day 11） | `requests.post` 发请求，`raise_for_status` 检查状态 | 所有 LLM API 调用的底层 |
| Token/Temperature（Day 12） | token 是计费单位，temperature 控输出随机性 | 成本控制和输出稳定性 |
| 模型选型（Day 13） | 按场景选模型，先 Flash 验证再升级 | 项目三合同审查的选型逻辑 |

#### LLM 核心概念速查

```
消息结构（必须背下来）：
messages = [
    {"role": "system",    "content": "你的角色设定"},   # 系统提示，定义 AI 行为
    {"role": "user",      "content": "用户说的话"},     # 用户输入
    {"role": "assistant", "content": "AI 上一轮回复"},  # AI 历史回复
    {"role": "user",      "content": "用户继续说的话"}, # 继续对话
]

多轮对话的关键：每次调用都要把完整历史带上，模型没有记忆，上下文全靠 messages 列表
```

---

### 2. 多轮对话的原理

**模型没有记忆**，它每次都只看到你传入的 `messages` 列表。

```
第1轮：
  发送：[system, user("你好")]
  收到：assistant("你好！有什么能帮你？")

第2轮：
  发送：[system, user("你好"), assistant("你好！有什么能帮你？"), user("我叫黑米")]
  收到：assistant("黑米你好！请问有什么问题？")

第3轮：
  发送：[system, user("你好"), assistant(...), user("我叫黑米"), assistant(...), user("我叫什么？")]
  收到：assistant("你叫黑米。")  ← 因为第2轮我们把名字带进去了
```

如果第3轮不带历史，模型就不知道你叫什么了。这就是为什么 Agent 框架里有"Memory"模块——本质上就是管理 messages 列表。

---

### 3. pytest 基础（今天第一次用）

**为什么要写测试？**

合同审查 Agent 上线后，你怎么知道它还在正常工作？每次改代码都手动测一遍？不现实。测试就是"自动检查代码是否按预期工作"。

**最简单的 pytest：**

```python
# test_example.py
def add(a, b):
    return a + b

def test_add():
    assert add(1, 2) == 3          # 通过
    assert add(-1, 1) == 0         # 通过
    assert add(0, 0) == 0          # 通过

# 运行：pytest test_example.py -v
```

**今天要用的断言模式（验证 API 返回格式）：**

```python
response = call_llm(...)

# 检查返回类型
assert isinstance(response, str)            # 必须是字符串
assert len(response) > 0                    # 不能是空字符串
assert len(response) < 2000                 # 不能超长（防止异常）

# 检查结构化返回（JSON 模式）
import json
data = json.loads(response)
assert "risk_level" in data                 # 必须有这个字段
assert data["risk_level"] in ["低", "中", "高"]  # 值必须在预期范围内
assert isinstance(data["reasons"], list)    # 必须是列表
```

---

### 4. 今天的项目目标

**合同风险审查对话助手（项目三的最小原型）**

功能：
1. 用户粘贴一段合同条款
2. AI 分析法律风险（输出 JSON 格式）
3. 用户可以追问（多轮对话）
4. pytest 验证 API 返回格式是否符合预期

这不是玩具项目，是**项目三的第一块砖**。Week 9-11 做的合同审查 Agent 就是在这个基础上加 Multi-Agent、MCP、RAG。

---

## 下午：实操练习（4小时）

练习文件放在：`E:\Agent岗位培训\Week2\day14-practice\`
     
---

### 练习 1：多轮对话管理器（核心）

打开 `E:\Agent岗位培训\Week2\day14-practice\conversation.py`

**目标：** 实现一个 `ConversationManager` 类，管理多轮对话历史，并调用 LLM API。

```python
# conversation.py
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

class ConversationManager:
    """
    多轮对话管理器
    核心职责：维护 messages 列表，确保每次调用都带完整历史
    """

    def __init__(self, system_prompt: str, model: str = "claude-sonnet-4-6"):
        self.model = model
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        self.total_tokens = 0  # 累计 token 用量

    def chat(self, user_input: str) -> str:
        """
        发送一轮对话，自动维护历史
        1. 把用户输入追加到 messages
        2. 调用 API
        3. 把 AI 回复追加到 messages
        4. 返回 AI 回复内容
        """
        # TODO：把 user_input 追加到 self.messages
        # 格式：{"role": "user", "content": user_input}

        # TODO：调用 client.chat.completions.create
        # 参数：model=self.model, messages=self.messages

        # TODO：提取回复内容（response.choices[0].message.content）

        # TODO：把 AI 回复追加到 self.messages
        # 格式：{"role": "assistant", "content": reply}

        # TODO：累加 token 用量到 self.total_tokens
        # response.usage.total_tokens

        # TODO：return reply
        pass

    def get_history(self) -> list:
        """返回完整对话历史（不含 system prompt）"""
        return [m for m in self.messages if m["role"] != "system"]

    def get_token_usage(self) -> int:
        """返回累计 token 用量"""
        return self.total_tokens

    def reset(self):
        """清空对话历史，保留 system prompt"""
        system_msg = self.messages[0]
        self.messages = [system_msg]
        self.total_tokens = 0


# 测试：简单多轮对话
if __name__ == "__main__":
    manager = ConversationManager(
        system_prompt="你是一个助手，回答要简洁，每次不超过50字。"
    )

    questions = [
        "我叫黑米，正在学 Agent 开发。",
        "我刚才说我在学什么？",
        "给我推荐一个学习建议。",
    ]

    for q in questions:
        print(f"\n用户：{q}")
        reply = manager.chat(q)
        print(f"AI：{reply}")

    print(f"\n累计 Token：{manager.get_token_usage()}")
    print(f"对话轮数：{len(manager.get_history()) // 2}")
```

运行成功后，观察：第2个问题 "我刚才说我在学什么？" AI 能正确回答吗？为什么？

---

### 练习 2：合同风险分析器（结构化输出）

打开 `E:\Agent岗位培训\Week2\day14-practice\contract_analyzer.py`

**目标：** 在 ConversationManager 基础上，实现合同条款的结构化风险分析。

```python
# contract_analyzer.py
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os, json
from openai import OpenAI
from dotenv import load_dotenv
from conversation import ConversationManager

load_dotenv()

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
        TODO：
        1. 调用 self.conversation.chat(clause)
        2. 用 json.loads() 解析返回的 JSON 字符串
        3. 如果解析失败，返回 {"error": "解析失败", "raw": 原始回复}
        4. return 解析后的字典
        """
        pass

    def follow_up(self, question: str) -> dict:
        """
        追问（利用多轮对话历史）
        TODO：逻辑和 analyze 完全一样，只是传入的是追问内容
        """
        pass

    def get_cost_estimate(self) -> str:
        """估算费用（DeepSeek V4-Flash 价格）"""
        tokens = self.conversation.get_token_usage()
        # 简化估算：假设输入输出各一半
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
```

---

### 练习 3：pytest 断言验证

打开 `E:\Agent岗位培训\Week2\day14-practice\test_contract_analyzer.py`

**目标：** 写 3 个测试函数，验证 API 返回格式是否符合预期。

```python
# test_contract_analyzer.py
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import pytest
from contract_analyzer import ContractAnalyzer

# 测试用的合同条款（固定，保证测试可重复）
TEST_CLAUSE = """
乙方须在签约后7个工作日内完成全部交付物，
如逾期，每日按合同总金额的5%计算违约金，无上限。
"""

@pytest.fixture
def analyzer():
    """pytest fixture：每个测试函数运行前自动创建一个新的 analyzer"""
    return ContractAnalyzer()


def test_analyze_returns_dict(analyzer):
    """测试1：analyze 必须返回字典"""
    result = analyzer.analyze(TEST_CLAUSE)
    # TODO：断言 result 是 dict 类型
    # assert isinstance(result, dict)
    pass


def test_analyze_has_required_fields(analyzer):
    """测试2：返回结果必须包含4个必填字段"""
    result = analyzer.analyze(TEST_CLAUSE)
    # TODO：断言 result 包含 risk_level、risk_points、suggestions、summary
    # 提示：用 assert "字段名" in result
    pass


def test_risk_level_is_valid(analyzer):
    """测试3：risk_level 的值只能是 低/中/高 之一"""
    result = analyzer.analyze(TEST_CLAUSE)
    # TODO：断言 result["risk_level"] in ["低", "中", "高"]
    pass


# 运行方式：
# cd E:\Agent岗位培训\Week2\day14-practice
# pytest test_contract_analyzer.py -v
```

运行 pytest，观察：
- 测试通过时输出什么？
- 如果故意写一个失败的断言，输出是什么？

---

### 练习 4（选做）：Token 超限保护

**真实场景：** 多轮对话越聊越长，messages 列表越来越大，Token 成本越来越高。当上下文超过模型限制（比如 200K），API 会报错。

给 `ConversationManager` 加一个 `max_turns` 参数，当对话超过指定轮数时，自动删除最早的一轮（保留 system prompt）：

```python
class ConversationManager:
    def __init__(self, system_prompt: str, model: str = "claude-sonnet-4-6", max_turns: int = 10):
        self.max_turns = max_turns
        # ... 其他初始化

    def _trim_history(self):
        """
        如果对话超过 max_turns 轮，删除最早的一轮（user + assistant 各一条）
        保留：第0条 system prompt 永远不删
        """
        # 对话轮数 = (len(messages) - 1) // 2  （减去 system prompt，每轮两条）
        # TODO：当轮数超过 max_turns，删除 messages[1] 和 messages[2]
        pass
```

---

## 晚上：复盘（1小时）

### 复盘问题（用自己的话回答，发给我检查）

1. **多轮对话的"记忆"是怎么实现的？如果不把历史带上会怎样？**

   模型本身没有记忆，每次调用都是独立的。"记忆"是通过在每次请求时把完整的 messages 列表传进去实现的——里面包含 system 提示、用户的每句话和 AI 的每次回复，按时间顺序排列。如果不带历史，模型就相当于失忆了，你说"我叫黑米"，下一轮再问"我叫什么"，它根本不知道，只能乱猜。

2. **pytest 的 `assert` 和普通 `if` 判断有什么区别？为什么要用 pytest 而不是手动 print 检查？**

   普通 `if` 失败了需要自己写 `print` 输出提示，而且只能一个个跑。`assert` 失败会直接抛出 AssertionError 并停住，pytest 会捕获它，告诉你哪一行断言挂了、期望值是什么、实际值是什么，非常直观。用 pytest 的核心好处是自动化——写好一次，以后每次改代码只要 `pytest -v` 跑一下，几十个测试都帮你检查，不用手动挨个 print 验证。

3. **ConversationManager 的 `reset()` 方法用在什么场景？合同审查项目里什么时候需要重置？**

   `reset()` 用于切换新任务时清空历史，同时保留 system prompt（角色设定不变）。合同审查里，每次分析一份全新的合同时就应该 reset——因为上一份合同的分析历史对新合同毫无意义，带着它反而会干扰模型判断，而且浪费 token。如果用户在同一份合同上追问，则不需要 reset，多轮历史正是追问的依据。

4. **今天的 ContractAnalyzer 和项目三的完整合同审查 Agent 差距在哪里？还缺哪些模块？**

   今天的版本是单文件、单条款、纯对话的最小原型。项目三要达到生产级，还缺：
   - **文档解析模块**：支持上传 PDF/Word 合同，自动分块，不是手动粘贴文本
   - **RAG 模块**：把法律法规、合同模板语料库做成向量数据库，检索增强分析质量
   - **Multi-Agent 协作**：拆分成"提取 Agent + 分析 Agent + 建议 Agent"，各司其职，结果更准
   - **MCP 协议接入**：让 Agent 能调用外部工具（法律数据库查询、条款比对等）
   - **持久化存储**：分析结果入库，支持历史查询和报告导出
   - **API 服务层**：用 FastAPI 包装成接口，前端或其他系统可以直接调用

5. **Week 2 总结：你现在能用自己的话解释 Token、Temperature、多轮对话、模型选型这4个概念吗？**

   - **Token**：模型处理文字的最小单元，中文约1.5字一个 token，也是计费单位。理解 token 就是理解成本和上下文窗口上限。
   - **Temperature**：控制模型输出的随机程度，0 最稳定适合结构化任务（如合同分析），1 以上更有创意适合写作。
   - **多轮对话**：模型没有记忆，通过每次请求带上完整 messages 历史列表来"假装有记忆"，这是所有 Agent Memory 模块的底层逻辑。
   - **模型选型**：按任务场景选模型，简单任务用轻量便宜的（DeepSeek V4-Flash），复杂推理用强力的（Claude Sonnet / GPT-4o），先小模型验证逻辑再升级，控制成本。
---

### 完成后 Git 提交

```powershell
cd C:\Users\pc\agent-learning-notes

git add Week2/day14/
git commit -m "day14: Week2收官 - 多轮对话管理器 + 合同风险分析器 + pytest验证"

$env:https_proxy = "http://127.0.0.1:7897"
git push origin main
```

---

### Week 2 收官 🎉

完成 Day 14 后，你掌握的技能栈：

```
Python 基础          ✅ 变量/列表/字典/函数/类/异步/异常处理
HTTP & API           ✅ requests 库、API Key 管理、错误处理
LLM 基础             ✅ Token、Temperature、System Prompt、上下文窗口
模型选型             ✅ 六大模型对比、费用计算、选型框架
多轮对话             ✅ messages 列表管理、历史维护
结构化输出           ✅ JSON 模式、格式约束
测试基础             ✅ pytest 断言验证 API 返回格式
```

**Week 3 预告（明天开始）：**

进入 Phase 2——LLM API 实战。Day 15 开始系统学 OpenAI API 完整用法（Streaming、Function Calling、Tool Use），并启动面试题训练（每周2道，书面回答）。

---

### 向我汇报

完成练习后把复盘答案发给我，我来检查并给出反馈。
