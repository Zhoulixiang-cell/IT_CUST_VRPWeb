from openai import AsyncOpenAI
from app.core.config import settings
from typing import List, Dict, AsyncGenerator

class LLMClient:
    """LLM调用工具：封装OpenAI客户端，提供流式/非流式调用"""
    def __init__(self):
        # 为了MVP测试，暂时跳过OpenAI初始化
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-test-placeholder-key":
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"OpenAI初始化失败: {e}")
                self.client = None

    async def stream_chat_completion(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式调用LLM，逐Token返回结果"""
        if not self.client:
            # 模拟回复用于测试
            import asyncio
            role_name = "测试角色"
            if messages and len(messages) > 0:
                # 从system prompt中提取角色名
                for msg in messages:
                    if msg.get('role') == 'system' and '苏格拉底' in msg.get('content', ''):
                        role_name = "苏格拉底"
                    elif msg.get('role') == 'system' and '哈利' in msg.get('content', ''):
                        role_name = "哈利·波特"
                    elif msg.get('role') == 'system' and '福尔摩斯' in msg.get('content', ''):
                        role_name = "夏洛克·福尔摩斯"
            
            user_content = messages[-1].get('content', '无内容') if messages else '无内容'
            mock_response = f"你好！我是{role_name}，你刚才说的是：{user_content}。很高兴与你交流！"
            
            for char in mock_response:
                yield {"type": "llm-token", "token": char}
                await asyncio.sleep(0.05)
            return
            
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
        if not self.client:
            return "这是一个测试回复。"
            
        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content

# 创建全局LLM客户端实例
llm_client = LLMClient()