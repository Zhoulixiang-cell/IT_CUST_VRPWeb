from openai import AsyncOpenAI
from app.core.config import settings
from app.core.zhipu_client import zhipu_client
from app.core.qwen_client import qwen_client
from typing import List, Dict, AsyncGenerator

class LLMClient:
    """多大模型支持的LLM客户端：支持OpenAI、智谱AI和通义千问"""
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.openai_client = None
        
        # 初始化OpenAI客户端（如果配置了）
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-test-placeholder-key":
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"OpenAI初始化失败: {e}")
                self.openai_client = None

    async def stream_chat_completion(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式调用LLM，逐Token返回结果"""
        
        # 根据配置选择不同的大模型服务
        if self.provider == "qwen":
            # 使用通义千问
            async for result in qwen_client.stream_chat_completion(messages):
                yield result
            return
        elif self.provider == "zhipu":
            # 使用智谱AI
            async for result in zhipu_client.stream_chat_completion(messages):
                yield result
            return
        elif self.provider == "openai" and self.openai_client:
            # 使用OpenAI
            try:
                stream = await self.openai_client.chat.completions.create(
                    model=settings.LLM_MODEL_NAME,
                    messages=messages,
                    stream=True,
                    temperature=0.7
                )
                async for chunk in stream:
                    token = chunk.choices[0].delta.content
                    if token:
                        yield {"type": "llm-token", "token": token}
                return
            except Exception as e:
                yield {"type": "llm-error", "message": f"OpenAI调用失败：{str(e)}"}
                return
        
        # 如果没有可用的服务，使用模拟回复
        async for result in self._fallback_mock_response(messages):
            yield result
    
    async def _fallback_mock_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, str], None]:
        """后备模拟响应"""
        import asyncio
        import random
        
        role_name = "AI助手"
        if messages and len(messages) > 0:
            # 从system prompt中提取角色名
            for msg in messages:
                if msg.get('role') == 'system':
                    content = msg.get('content', '')
                    if '苏格拉底' in content:
                        role_name = "苏格拉底"
                    elif '哈利' in content:
                        role_name = "哈利·波特"
                    elif '福尔摩斯' in content:
                        role_name = "夏洛克·福尔摩斯"
        
        user_content = messages[-1].get('content', '无内容') if messages else '无内容'
        
        # 角色化的后备响应
        if role_name == "苏格拉底":
            responses = [
                f"关于'{user_content}'，我想邀请你和我一起探索。什么是真正重要的？",
                f"你提到的'{user_content}'很有意思。但我们是否应该先问问自己：我们真的了解这个概念吗？"
            ]
        elif role_name == "哈利·波特":
            responses = [
                f"'{user_content}'听起来像是一个需要魔法来解决的问题！让我们一起想想办法。",
                f"在霍格沃茨，我们学会了面对任何挑战。'{user_content}'也不例外！"
            ]
        elif role_name == "夏洛克·福尔摩斯":
            responses = [
                f"'{user_content}'中隐藏着线索。让我仔细分析一下这个案例。",
                f"基于'{user_content}'这个信息，我需要更多数据来得出结论。"
            ]
        else:
            responses = [f"关于'{user_content}'，这是一个很有意思的话题。"]
        
        mock_response = random.choice(responses) + "（当前为智能模拟模式）"
        
        for char in mock_response:
            yield {"type": "llm-token", "token": char}
            await asyncio.sleep(0.05)

    async def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """非流式调用LLM，一次性返回结果"""
        
        if self.provider == "qwen":
            return await qwen_client.get_chat_completion(messages)
        elif self.provider == "zhipu":
            return await zhipu_client.get_chat_completion(messages)
        elif self.provider == "openai" and self.openai_client:
            try:
                response = await self.openai_client.chat.completions.create(
                    model=settings.LLM_MODEL_NAME,
                    messages=messages,
                    temperature=0.5
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"OpenAI调用失败：{str(e)}"
        
        return "当前为模拟模式，请配置大模型API密钥。"

# 创建全局LLM客户端实例
llm_client = LLMClient()