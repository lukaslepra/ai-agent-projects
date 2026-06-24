# Week 3 Day 18 - LLM API实战：Claude API + 国产模型API

> 学员：黑米 | 日期：2026-06-24 | 每日投入：8小时
> **昨天你搞定了 Function Calling，今天扩展视野——同一套代码怎么调用 Claude、DeepSeek、通义千问，以及怎么根据任务自动选模型**

---

## 上午：概念学习（3小时）

### 1. 为什么要会多模型调用

在实际 Agent 项目里，你不会只用一个模型。原因很简单：

| 场景 | 最优选择 | 理由 |
|------|----------|------|
| 复杂推理、代码生成 | Claude Sonnet / DeepSeek | 推理能力强 |
| 高并发简单问答 | 通义千问 / DeepSeek | 成本低、速度快 |
| 中文理解、本土化 | 通义千问 / DeepSeek | 中文训练数据更充分 |
| 主力模型挂了 | 备用模型自动降级 | 保证服务不中断 |

**一句话总结：** 不同模型各有擅长，会多模型调用 = 能根据成本、速度、效果三维度做选型。

---

### 2. OpenAI 兼容层：一套代码调所有模型

这是今天最重要的概念。几乎所有主流模型提供商都支持 **OpenAI 兼容 API**：

```python
# 调用 Claude（通过兼容层）
client = OpenAI(
    api_key="你的key",
    base_url="https://api.anthropic.com/v1",  # 或者你的代理地址
)
response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "你好"}]
)

# 调用 DeepSeek（完全一样的代码，只换 base_url 和 model）
client = OpenAI(
    api_key="你的key",
    base_url="https://api.deepseek.com/v1",
)
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "你好"}]
)
```

**关键点：** 代码结构完全一样，只需要换 `base_url` 和 `model` 名字。这就是为什么我们能写一个通用的 `call_model(model_id, messages)` 函数。

---

### 3. 各模型的 API 关键参数对比

虽然接口统一，但各模型有些细节差异：

| 参数 | OpenAI/Claude | DeepSeek | 通义千问 |
|------|--------------|----------|----------|
| `model` | gpt-4o / claude-sonnet-4-6 | deepseek-chat / deepseek-reasoner | qwen-plus / qwen-max |
| `max_tokens` | ✅ 支持 | ✅ 支持 | ✅ 支持（参数名同） |
| `temperature` | 0~2 | 0~2 | 0~2 |
| `stream` | ✅ | ✅ | ✅ |
| `tools` | ✅ Function Calling | ✅ | ✅ |
| 特殊参数 | — | `prefix` (FIM) | `enable_search` (联网搜索) |

**实际工作中的注意点：**
- 不同模型对 `temperature` 的"敏感度"不同：DeepSeek 在 0.7 以上就很发散，通义在 1.0 以上才有明显差异
- 国产模型的 `max_tokens` 上限通常更大，但单次请求延迟也更高
- 代码相关任务用 `deepseek-chat`，中文长文用 `qwen-max`，复杂推理用 Claude

---

### 4. 重要参数详解（今天练习会用到）

**`max_tokens`：控制输出长度**
```python
# 输出被截断时，finish_reason 会是 "length" 而不是 "stop"
response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=messages,
    max_tokens=50,   # 最多输出50个token
)
print(response.choices[0].finish_reason)  # "length" 表示被截断了
print(response.usage.completion_tokens)   # 实际用了多少token
```

**`stop`：遇到特定字符串就停**
```python
# 代码生成场景：遇到 ``` 就停，不输出多余内容
response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=messages,
    stop=["```", "\n\n\n"],  # 遇到这些就停
)
```

**`frequency_penalty` vs `presence_penalty`：控制重复度**
```python
# frequency_penalty（0~2）：惩罚已出现过的词，减少词汇重复
# presence_penalty（0~2）：鼓励引入新话题，增加话题多样性
response = client.chat.completions.create(
    model="claude-sonnet-4-6",
    messages=messages,
    frequency_penalty=1.2,  # 让模型少用重复词汇
)
```

---

### 5. 模型路由器：工程化思维

在生产环境，你不会手动选模型。好的做法是写一个 **路由器**：

```python
ROUTING_RULES = {
    "creative": {"model": "claude-sonnet-4-6", "temperature": 1.2},
    "code":     {"model": "deepseek-chat",     "temperature": 0.2},
    "chat":     {"model": "qwen-plus",         "temperature": 0.7},
}

def route_and_call(task_type: str, message: str) -> str:
    config = ROUTING_RULES.get(task_type, ROUTING_RULES["chat"])
    response = client.chat.completions.create(
        model=config["model"],
        messages=[{"role": "user", "content": message}],
        temperature=config["temperature"],
    )
    return response.choices[0].message.content
```

**为什么这样设计？**
- 路由规则集中管理，换模型只改配置不改业务代码
- 可以扩展：加上成本预算限制、按时段路由、A/B 测试路由
- 这就是 Week 7 多模型路由器项目的雏形

---

### 6. 降级策略（Fallback）：生产级必备

主模型挂了怎么办？答：提前写好降级链。

```python
FALLBACK_CHAIN = ["claude-sonnet-4-6", "deepseek-chat", "qwen-plus"]

def call_with_fallback(messages: list) -> str:
    for model_id in FALLBACK_CHAIN:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=messages,
                timeout=30,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️ {model_id} 失败：{e}，尝试下一个...")
    return "所有模型均不可用"
```

**降级链设计原则：**
1. 主模型优先（效果最好）
2. 备用模型成本低（降级时往往是高峰期，省钱重要）
3. 兜底模型最稳定（即使慢也要能回答）

---

### 7. 今天要做什么

**练习1**：Claude API 基础——单轮对话、system prompt、temperature 实验

**练习2**：多模型横向对比——同一问题发给多个模型，打印耗时和回答

**练习3**：参数实验——max_tokens 截断、stop 序列、frequency_penalty

**练习4（选做）**：降级链——主模型失败自动换备用模型

---

## 下午：实操练习（4小时）

练习文件放在：`E:\Agent岗位培训\Week3\day18-practice\`

---

### 练习 1：Claude API 基础调用

打开 `E:\Agent岗位培训\Week3\day18-practice\claude_basic.py`

**目标：** 完成三个基础调用函数，验证 API 能跑通，感受 temperature 对输出的影响。

**考什么概念：** OpenAI 兼容层的基础用法；system prompt 的位置；temperature 控制随机性

**填哪里：** `simple_chat`、`chat_with_system`、`chat_with_temperature` 三个函数体，每个都是调用 `client.chat.completions.create`，区别在于 messages 结构和参数不同

**怎么运行：**
```bash
cd E:\Agent岗位培训\Week3\day18-practice
python claude_basic.py
```

**预期结果：**
```
=== 测试 1-A：基础对话 ===
回答：机器学习是让计算机从数据中自动学习规律...

=== 测试 1-B：带 system prompt ===
回答：哟，今天天气巴适得很，太阳好大嘛...（重庆话风格）

=== 测试 1-C：temperature 对比 ===
temperature=0.0：重庆AI火锅局（每次几乎一样）
temperature=0.7：麻辣智能体验馆（有些变化）
temperature=1.5：量子辣椒意识流（很发散）
```

**常见报错：**
- `AuthenticationError`：API Key 错了，检查 .env 文件
- `AttributeError: 'NoneType'`：忘记 return 了，检查函数是否有 return 语句
- `ValidationError`：messages 格式错了，确认每条消息都有 `role` 和 `content`

---

### 练习 2：多模型对比调用

打开 `E:\Agent岗位培训\Week3\day18-practice\model_compare.py`

**目标：** 用同一套代码调用多个模型，实现简单的模型路由器。

**考什么概念：** 通用 `call_model` 函数设计；try/except 处理模型调用失败；路由规则集中管理

**填哪里：**
- `call_model`：封装基础调用，加上计时
- `compare_models`：遍历 MODELS 字典，每个都调用，打印对比
- `route_and_call`：if/elif 实现路由，不同任务类型选不同模型和 temperature

**怎么运行：**
```bash
python model_compare.py
```

**预期结果：**
```
问题：用一句话解释什么是 Agent？
============================================================
[claude-sonnet-4-6] 耗时: 1.2s | Agent 是能自主感知环境、决策和行动的 AI 系统...
[deepseek-chat]     耗时: 0.8s | Agent 是具备工具调用能力的自主 AI...
[qwen-plus]         耗时: 0.9s | Agent 是能够自主规划和执行任务的智能体...
```

**常见报错：**
- 某个模型返回 `model not found`：该模型 ID 不在代理支持列表里，换成 claude-sonnet-4-6 继续测试
- `KeyError`：路由规则里没有对应的 task_type，加个 `else` 兜底

---

### 练习 3：模型参数实验

打开 `E:\Agent岗位培训\Week3\day18-practice\model_params.py`

**目标：** 动手感受 max_tokens、stop、frequency_penalty 的实际效果。

**考什么概念：** `finish_reason` 判断截断；`usage` 字段读取 token 用量；stop 序列的工程价值；penalty 参数减少重复

**填哪里：**
- `chat_with_max_tokens`：加 `max_tokens` 参数，返回 content + finish_reason + tokens_used
- `chat_with_stop`：加 `stop=stop_sequences` 参数
- `chat_with_penalty`：加 `frequency_penalty` 参数

**怎么运行：**
```bash
python model_params.py
```

**预期结果：**
```
=== 测试 3-A：max_tokens 对比 ===
max_tokens=20  | finish_reason=length | tokens=20
内容：重庆的旅游景点非常丰富，主要包括解放碑...

max_tokens=100 | finish_reason=length | tokens=100
内容：重庆是一座魅力十足的山城...

max_tokens=500 | finish_reason=stop   | tokens=XXX
内容：（完整回答）
```

**常见报错：**
- `finish_reason` 一直是 `stop` 而不是 `length`：说明 max_tokens 设得够大，回答在限制内就结束了，正常
- `response.usage` 是 None：部分模型在流式模式下不返回 usage，确认没开 `stream=True`

---

### 练习 4（选做）：降级链

打开 `E:\Agent岗位培训\Week3\day18-practice\model_switcher.py`

**目标：** 实现生产级降级策略，主模型失败自动切到备用模型。

**考什么概念：** try/except 捕获 API 异常；fallback 链遍历；重试机制

**填哪里：**
- `call_with_timeout`：调用 API，加 `timeout=timeout` 参数
- `call_with_fallback`：遍历 MODEL_FALLBACK_CHAIN，失败就捕获异常继续下一个
- `reliable_call`：在 fallback 基础上加最多 max_retries 次重试

**怎么运行：**
```bash
python model_switcher.py
```

**预期结果：**
```
=== 测试 4-B：降级调用 ===
使用模型：claude-sonnet-4-6 | 尝试次数：1
回答：你好！今天学了...

=== 测试 4-C：稳定调用 ===
第1次尝试成功，使用模型：claude-sonnet-4-6
最终回答：Function Calling 的核心价值是...
```

**常见报错：**
- 降级链全部失败：检查 base_url 和 API Key 是否正确
- `timeout` 参数报错：openai SDK 版本不同，试试 `http_client` 方式或直接去掉 timeout 参数先跑通

---

## 晚上：复盘（1小时）

### 复盘问题（用自己的话回答，发给我检查）

1. **OpenAI 兼容层是什么意思？为什么 DeepSeek、通义千问也能用 `from openai import OpenAI` 来调用？**

2. **`finish_reason` 有哪几种值？分别代表什么情况？在什么场景下你需要主动判断它？**

3. **模型路由器的核心思路是什么？相比"每次手动指定模型"，它有什么工程上的好处？**

4. **降级链（fallback chain）解决了什么问题？在实际生产环境里，你觉得降级链还可以加什么逻辑让它更健壮？**

5. **面试题（Week 3 第4题，书面作答）：**

   面试官问："你在项目里用过多个模型吗？你是怎么做模型选型的？"

   用 STAR 法回答，结合今天实现的模型路由器和降级链，说出你的思考。

---

### 完成后 Git 提交（PR 方式）

```bash
git checkout -b day18-multi-model
git add Week3/day18-practice/ "Week3/Day18-Claude API与国产模型API.md"
git commit -m "Day18: Claude API + 国产模型API 练习完成"
git push -u origin day18-multi-model
```

---

### 向我汇报

完成练习后把复盘答案（含面试题作答）发给我，我来检查并给出反馈。
