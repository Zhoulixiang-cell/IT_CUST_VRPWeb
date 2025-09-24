from openai import AsyncOpenAI
from app.core.config import settings
from app.services.xunfei_tts import xunfei_tts_service
from typing import AsyncGenerator, Dict
import base64
import asyncio

class TTSService:
    """文本转语音(TTS)服务：封装OpenAI TTS接口和讯飞TTS接口"""
    def __init__(self):
        self.provider = getattr(settings, 'TTS_PROVIDER', 'xunfei')  # 默认使用讯飞
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-test-placeholder-key":
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"TTS初始化失败: {e}")
                self.client = None

    async def text_to_speech_stream(
        self, text: str, voice: str = "alloy"
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式生成音频，分块返回Base64编码的MP3"""
        
        # 优先使用讯飞TTS
        if self.provider == "xunfei" and hasattr(settings, 'XUNFEI_API_KEY') and settings.XUNFEI_API_KEY:
            async for result in xunfei_tts_service.text_to_speech_stream(text, voice):
                yield result
            return
            
        # 使用OpenAI TTS
        if not self.client:
            # 模拟TTS输出
            yield {
                "type": "tts-chunk",
                "audio": "data:audio/mp3;base64,placeholder",
                "seq": 0,
                "is_end": True
            }
            return
            
        # 处理过长文本
        if len(text) > 4000:
            text = text[:3997] + "..."
            yield {"type": "tts-warning", "message": "文本过长，已截断"}

        try:
            # 调用TTS接口生成音频
            response = await self.client.audio.speech.create(
                model=settings.TTS_MODEL_NAME,
                voice=voice,
                input=text,
                response_format="mp3"
            )
            audio_bytes = await response.aread()

            # 分块处理并返回
            chunk_size = 1024
            total_chunks = len(audio_bytes) // chunk_size + 1
            for i in range(total_chunks):
                start = i * chunk_size
                end = start + chunk_size
                chunk = audio_bytes[start:end]
                base64_chunk = base64.b64encode(chunk).decode("utf-8")
                yield {
                    "type": "tts-chunk",
                    "audio": f"data:audio/mp3;base64,{base64_chunk}",
                    "seq": i,
                    "is_end": i == total_chunks - 1
                }
                await asyncio.sleep(0.05)
        except Exception as e:
            yield {"type": "tts-error", "message": f"语音生成失败：{str(e)}"}

# 创建全局TTS服务实例
tts_service = TTSService()