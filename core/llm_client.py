"""DeepSeek API客户端封装"""
import os
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """DeepSeek API客户端封装"""

    def __init__(self, api_key: str = None, model: str = "deepseek-chat"):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.model = model
        self.base_url = "https://api.deepseek.com"

    def chat(self, messages: List[dict], temperature: float = 0.7) -> str:
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model,
                temperature=temperature
            )

            langchain_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    langchain_messages.append(SystemMessage(content=msg["content"]))
                else:
                    langchain_messages.append(HumanMessage(content=msg["content"]))

            response = llm.invoke(langchain_messages)
            return response.content
        except Exception as e:
            print(f"[LLMClient] 调用失败: {e}")
            raise
