"""
百度语音识别服务
支持音频转文字功能
"""
import base64
import httpx
import json
from typing import AsyncGenerator
from app.core.config import settings

class BaiduASRService:
    """百度语音识别服务"""
    
    def __init__(self):
        self.app_id = settings.BAIDU_APP_ID
        self.api_key = settings.BAIDU_API_KEY
        self.secret_key = settings.BAIDU_SECRET_KEY
        self.access_token = None
        
    async def get_access_token(self):
        """获取百度API访问令牌"""
        if not self.api_key or not self.secret_key:
            return None
            
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    return self.access_token
        except Exception as e:
            print(f"获取百度访问令牌失败: {e}")
        
        return None
    
    async def transcribe_stream(self, audio_data) -> AsyncGenerator[dict, None]:
        """
        语音转文字（流式处理）
        audio_data: 音频文件数据或生成器
        """
        
        if not self.access_token:
            await self.get_access_token()
        
        if not self.access_token:
            yield {
                "type": "stt-error", 
                "message": "百度语音识别未配置或配置错误"
            }
            return
        
        try:
            # 读取音频数据
            if hasattr(audio_data, 'read'):
                audio_bytes = await audio_data.read()
            else:
                audio_bytes = audio_data
            
            # 转换为base64
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # 调用百度语音识别API
            url = "https://vop.baidu.com/server_api"
            headers = {
                "Content-Type": "application/json; charset=utf-8"
            }
            
            payload = {
                "format": "webm",  # 支持webm格式
                "rate": 16000,     # 采样率
                "channel": 1,      # 单声道
                "cuid": "python_client",
                "token": self.access_token,
                "speech": audio_base64,
                "len": len(audio_bytes)
            }
            
            yield {"type": "stt-processing", "message": "正在处理语音..."}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("err_no") == 0:
                        # 识别成功
                        text = "".join(result.get("result", []))
                        yield {
                            "type": "stt-final",
                            "text": text,
                            "confidence": 0.95  # 百度API不返回置信度，使用默认值
                        }
                    else:
                        # 识别失败
                        yield {
                            "type": "stt-error",
                            "message": f"语音识别失败: {result.get('err_msg', '未知错误')}"
                        }
                else:
                    yield {
                        "type": "stt-error",
                        "message": f"API调用失败: {response.status_code}"
                    }
                    
        except Exception as e:
            yield {
                "type": "stt-error",
                "message": f"语音识别异常: {str(e)}"
            }

# 创建百度ASR服务实例
baidu_asr_service = BaiduASRService()