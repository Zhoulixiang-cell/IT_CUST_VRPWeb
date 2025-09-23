from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict, AsyncGenerator

class LLMClient:
    """LLM调用工具：封装OpenAI客户端，提供流式/非流式调用"""
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if not settings.OPENAI_API_KEY:
            raise ValueError("请在.env文件中配置OPENAI_API_KEY")

    async def stream_chat_completion(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式调用LLM，逐Token返回结果"""
        try:
            stream = await self.client.chat.completions.create(
                model=settings.LLM_MODEL_NAME,
                messages=messages,
                stream=True,
                temperature=0.7
            )
            async for chunk in stream:
                token = chunk.choices[0].delta.content
                if token:
                    yield {"type": "llm-token", "token": token}
        except Exception as e:
            yield {"type": "llm-error", "message": f"LLM调用失败：{str(e)}"}

    async def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """非流式调用LLM，一次性返回结果"""
        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content

# 创建全局LLM客户端实例
llm_client = LLMClient()
