"""
讯飞语音合成服务 - 简化版
"""
from typing import AsyncGenerator, Dict
import asyncio
import base64
from app.core.config import settings


class XunfeiTTSService:
    """讯飞语音合成服务"""
    
    def __init__(self):
        self.api_key = settings.XUNFEI_API_KEY
        self.app_id = settings.XUNFEI_APP_ID
        self.api_secret = settings.XUNFEI_API_SECRET
        
        # 角色语音映射
        self.role_voices = {
            'socrates': 'xiaoyan',      # 苏格拉底：温和男声
            'harry_potter': 'xiaofeng', # 哈利波特：年轻男声
            'sherlock': 'xiaoyu'        # 福尔摩斯：理性男声
        }
        
    def _get_voice_name(self, voice: str):
        """根据角色获取语音名称"""
        if voice in self.role_voices:
            return self.role_voices[voice]
        
        # 默认映射
        voice_map = {
            'alloy': 'xiaoyan',
            'echo': 'xiaofeng', 
            'fable': 'xiaoyu',
            'onyx': 'xiaoming',
            'nova': 'xiaoqian',
            'shimmer': 'xiaoxin'
        }
        
        return voice_map.get(voice, 'xiaoyan')
        
    async def text_to_speech_stream(
        self, text: str, voice: str = "alloy"
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式生成音频，分块返回Base64编码的音频"""
        
        if not all([self.api_key, self.app_id, self.api_secret]):
            yield {
                "type": "tts-error",
                "message": "讯飞语音合成未配置或配置错误"
            }
            return
            
        # 处理过长文本
        if len(text) > 8000:
            text = text[:7997] + "..."
            yield {"type": "tts-warning", "message": "文本过长，已截断"}
            
        try:
            # 获取语音名称
            voice_name = self._get_voice_name(voice)
            
            # 模拟TTS处理
            yield {"type": "tts-info", "message": f"正在使用讯飞语音合成（{voice_name}）..."}
            await asyncio.sleep(0.5)
            
            # TODO: 实现真正的讯飞TTS API调用
            # 这里先使用模拟音频数据
            mock_audio = base64.b64encode(b"mock_audio_data").decode('utf-8')
            
            yield {
                "type": "tts-chunk",
                "audio": f"data:audio/mp3;base64,{mock_audio}",
                "seq": 0,
                "is_end": True
            }
            
        except Exception as e:
            yield {
                "type": "tts-error",
                "message": f"语音合成异常：{str(e)}"
            }


# 创建讯飞TTS服务实例
xunfei_tts_service = XunfeiTTSService()