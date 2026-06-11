# conversation.py
# 练习 1：多轮对话管理器
# 目标：实现 ConversationManager 类，管理多轮对话历史

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=r"E:\Agent岗位培训\Week2\day14-practice\.env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


class ConversationManager:
    """
    多轮对话管理器
    核心职责：维护 messages 列表，确保每次调用都带完整历史
    """

    def __init__(self, system_prompt: str, model: str = "claude-sonnet-4-6", max_turns: int = 10):
        self.model = model
        self.max_turns = max_turns
        self.messages = [
            {"role": "system", "content": system_prompt}
        ]
        self.total_tokens = 0  # 累计 token 用量

    def chat(self, user_input: str) -> str:
        """
        发送一轮对话，自动维护历史
        1. 把 user_input 追加到 self.messages
        2. 调用 API
        3. 把 AI 回复追加到 self.messages
        4. 累加 token 用量
        5. return 回复内容
        """
        # 1. 把用户输入追加到 messages
        self.messages.append({"role": "user", "content": user_input})

        # 2. 调用 API（带完整历史）
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )

        # 3. 提取回复内容
        reply = response.choices[0].message.content

        # 4. 把 AI 回复追加到 messages
        self.messages.append({"role": "assistant", "content": reply})

        # 5. 累加 token 用量
        self.total_tokens += response.usage.total_tokens

        # 超限保护（选做）
        self._trim_history()

        return reply

    def _trim_history(self):
        """
        如果对话超过 max_turns 轮，删除最早的一轮（user + assistant 各一条）
        保留：第0条 system prompt 永远不删
        """
        # 对话轮数 = (len(messages) - 1) // 2
        while (len(self.messages) - 1) // 2 > self.max_turns:
            # 删除最早的一轮（messages[1] 是最早的 user，messages[2] 是对应的 assistant）
            del self.messages[1]
            del self.messages[1]  # 删完第一条后，原来的[2]变成了新的[1]

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
