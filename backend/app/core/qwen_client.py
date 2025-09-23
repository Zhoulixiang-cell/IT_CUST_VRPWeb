"""
通义千问 (Qwen) 客户端封装
支持文本生成和流式响应
"""
import httpx
import json
import asyncio
import random
from typing import List, Dict, AsyncGenerator
from app.core.config import settings

class QwenClient:
    """通义千问客户端，兼容OpenAI接口格式"""
    
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        self.model = "qwen-turbo"  # 或者使用 "qwen-plus", "qwen-max"
        
    async def stream_chat_completion(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式调用通义千问，逐Token返回结果"""
        
        if not self.api_key or self.api_key == "":
            # 模拟回复用于测试
            async for result in self._mock_response(messages):
                yield result
            return
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "enable"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000,
                "incremental_output": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                async with client.stream(
                    "POST", 
                    self.base_url, 
                    headers=headers, 
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        yield {"type": "llm-error", "message": f"通义千问调用失败：{response.status_code}"}
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data:"):
                            data_str = line[5:].strip()  # 移除 "data:" 前缀
                            if data_str == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if "output" in data and "text" in data["output"]:
                                    text = data["output"]["text"]
                                    if text:
                                        yield {"type": "llm-token", "token": text}
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            yield {"type": "llm-error", "message": f"通义千问调用异常：{str(e)}"}
    
    async def _mock_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, str], None]:
        """模拟响应（用于测试，无API密钥时）"""
        import asyncio
        import random
        
        role_name = "AI助手"
        
        # 从system prompt中提取角色信息
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
        
        # 基于通义千问的角色化回复
        if role_name == "苏格拉底":
            questions = [
                f"关于'{user_content}'，这是一个值得深思的问题。让我们通过对话来探索真理。",
                f"你提到的'{user_content}'很有意思。但我想问，你是如何理解这个概念的本质的？",
                f"'{user_content}'引发了我的思考。在我们讨论之前，你认为什么是最重要的？"
            ]
            conclusions = [
                "智慧始于承认自己的无知。",
                "通过不断的质疑，我们才能接近真理。",
                "真正的学习在于激发内心的智慧。"
            ]
            mock_response = random.choice(questions) + " " + random.choice(conclusions)
            
        elif role_name == "哈利·波特":
            responses = [
                f"'{user_content}'真是个有趣的话题！这让我想起了在霍格沃茨的美好时光。",
                f"关于'{user_content}'，我觉得就像面对魔法挑战一样，总有解决的办法！",
                f"哇！'{user_content}'让我想起了邓布利多教授说过的话：'幸福可以在最黑暗的时光中找到。'"
            ]
            mock_response = random.choice(responses) + " 让我们一起探索这个神奇的问题吧！"
            
        elif role_name == "夏洛克·福尔摩斯":
            deductions = [
                f"从'{user_content}'这个线索出发，我能推断出几个关键要点。",
                f"'{user_content}'提供了有价值的信息。让我来分析其中的逻辑关系。",
                f"基于'{user_content}'，我的推理告诉我这背后有更深层的含义。"
            ]
            conclusions = [
                "细节往往决定成败。",
                "逻辑是我们最可靠的工具。",
                "真相总是隐藏在表象之下。"
            ]
            mock_response = random.choice(deductions) + " " + random.choice(conclusions)
            
        else:
            mock_response = f"你好！我是{role_name}，很高兴和你讨论'{user_content}'这个话题。"
        
        # 添加通义千问标识
        mock_response += "（当前使用通义千问模拟模式）"
        
        # 模拟流式输出
        for char in mock_response:
            yield {"type": "llm-token", "token": char}
            await asyncio.sleep(0.03)  # 模拟网络延迟
    
    async def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """非流式调用，一次性返回结果"""
        if not self.api_key or self.api_key == "":
            return "这是一个测试回复（通义千问模拟模式）。"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1000
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    return data["output"]["text"]
                else:
                    return f"通义千问调用失败：{response.status_code}"
                    
        except Exception as e:
            return f"通义千问调用异常：{str(e)}"

# 创建全局通义千问客户端实例
qwen_client = QwenClient()