"""
智谱AI (ChatGLM) 客户端封装
支持文本生成和流式响应
"""
import httpx
import json
import asyncio
from typing import List, Dict, AsyncGenerator
from app.core.config import settings

class ZhipuClient:
    """智谱AI客户端，兼容OpenAI接口格式"""
    
    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.base_url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
        self.model = "glm-4"  # 或者使用 "glm-3-turbo"
        
    async def stream_chat_completion(
        self, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式调用智谱AI，逐Token返回结果"""
        
        if not self.api_key or self.api_key == "your-zhipu-api-key-here":
            # 模拟回复用于测试
            async for result in self._mock_response(messages):
                yield result
            return
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
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
                        yield {"type": "llm-error", "message": f"智谱AI调用失败：{response.status_code}"}
                        return
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # 移除 "data: " 前缀
                            if data_str.strip() == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(data_str)
                                if "choices" in data and len(data["choices"]) > 0:
                                    delta = data["choices"][0].get("delta", {})
                                    content = delta.get("content")
                                    if content:
                                        yield {"type": "llm-token", "token": content}
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            yield {"type": "llm-error", "message": f"智谱AI调用异常：{str(e)}"}
    
    async def _mock_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[Dict[str, str], None]:
        """模拟响应（用于测试，无API密钥时）"""
        import asyncio
        import random
        
        role_name = "AI助手"
        role_system_prompt = ""
        
        # 从system prompt中提取角色信息
        for msg in messages:
            if msg.get('role') == 'system':
                content = msg.get('content', '')
                role_system_prompt = content
                if '苏格拉底' in content:
                    role_name = "苏格拉底"
                elif '哈利' in content:
                    role_name = "哈利·波特"
                elif '福尔摩斯' in content:
                    role_name = "夏洛克·福尔摩斯"
        
        user_content = messages[-1].get('content', '无内容') if messages else '无内容'
        
        # 增强的智能模拟回复
        if role_name == "苏格拉底":
            # 苏格拉底：诘问法引导思考
            questions = [
                f"我的朋友，你提到了'{user_content}'。但我想问你，这个概念的本质是什么？",
                f"关于'{user_content}'，让我们深入思考。你认为这背后的真理是什么？",
                f"'{user_content}'确实值得探讨。但请告诉我，你是如何得出这个观点的？",
                f"很有趣的观点！关于'{user_content}'，你是否想过它与正义和智慧的关系？"
            ]
            follow_up = [
                "真正的智慧在于承认自己的无知。",
                "通过不断的质疑，我们才能接近真理。",
                "让我们继续这场思辨的旅程吧。"
            ]
            mock_response = random.choice(questions) + " " + random.choice(follow_up)
            
        elif role_name == "哈利·波特":
            # 哈利·波特：友善热情，魔法世界视角
            responses = [
                f"嗨！'{user_content}'让我想起了在霍格沃茨学到的东西。在魔法世界中，我们相信每个问题都有解决的办法！",
                f"关于'{user_content}'，这真的很有趣！你知道吗，邓布利多校长曾说过，最黑暗的时候，只要点亮一盏灯就能找到希望。",
                f"哇，'{user_content}'！这让我想起了赫敏总是在图书馆里寻找答案的样子。也许我们也可以一起探索这个问题！",
                f"'{user_content}'确实值得思考。在对抗伏地魔的经历中，我学会了勇气和友谊的重要性。你觉得这些品质如何帮助我们面对挑战？"
            ]
            mock_response = random.choice(responses)
            
        elif role_name == "夏洛克·福尔摩斯":
            # 福尔摩斯：逻辑推理，观察细节
            deductions = [
                f"有趣！从你提出'{user_content}'这个问题，我可以推断出几个关键线索。",
                f"基于'{user_content}'，让我来分析一下背后的逻辑模式。",
                f"'{user_content}'透露了重要信息。正如我常说，细节决定一切。",
                f"观察，推理，验证。'{user_content}'这个问题需要我们运用演绎法来分析。"
            ]
            conclusions = [
                "当你排除了所有不可能的情况，剩下的，无论多么难以置信，都必然是真相。",
                "数据！数据！没有粘土，我无法制造砖块。",
                "游戏开始了！让我们一步步揭开真相的面纱。"
            ]
            mock_response = random.choice(deductions) + " " + random.choice(conclusions)
            
        else:
            mock_response = f"你好！我是{role_name}，关于'{user_content}'，我很乐意与你深入探讨这个话题。"
        
        # 模拟流式输出
        for char in mock_response:
            yield {"type": "llm-token", "token": char}
            await asyncio.sleep(0.03)  # 模拟网络延迟
    
    async def get_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        """非流式调用，一次性返回结果"""
        if not self.api_key or self.api_key == "your-zhipu-api-key-here":
            return "这是一个测试回复（智谱AI模拟模式）。"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"智谱AI调用失败：{response.status_code}"
                    
        except Exception as e:
            return f"智谱AI调用异常：{str(e)}"

# 创建全局智谱AI客户端实例
zhipu_client = ZhipuClient()