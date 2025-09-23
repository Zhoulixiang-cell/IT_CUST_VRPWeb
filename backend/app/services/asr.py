from openai import AsyncOpenAI
from app.core.config import settings
from app.services.baidu_asr import baidu_asr_service
from typing import AsyncGenerator, Dict
import asyncio

class ASRService:
    """多语音识别服务：支持OpenAI Whisper和百度语音识别"""
    def __init__(self):
        self.provider = getattr(settings, 'ASR_PROVIDER', 'baidu')  # 默认使用百度
        self.openai_client = None
        
        # 初始化OpenAI客户端（如果配置了）
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-test-placeholder-key":
            try:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"ASR初始化失败: {e}")
                self.openai_client = None

    async def transcribe_stream(
        self, audio_chunks: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式处理音频，返回识别结果"""
        
        # 优先使用百度语音识别
        if self.provider == "baidu" and hasattr(settings, 'BAIDU_API_KEY') and settings.BAIDU_API_KEY:
            # 收集音频数据
            audio_buffer = b""
            async for chunk in audio_chunks:
                audio_buffer += chunk
            
            # 使用百度ASR
            async for result in baidu_asr_service.transcribe_stream(audio_buffer):
                yield result
            return
        
        # 使用OpenAI Whisper
        elif self.provider == "openai" and self.openai_client:
            yield {"type": "stt-interim", "text": "正在识别语音..."}
            await asyncio.sleep(0.5)
            
            # 收集完整音频
            audio_buffer = b""
            async for chunk in audio_chunks:
                audio_buffer += chunk

            try:
                response = await self.openai_client.audio.transcriptions.create(
                    model=settings.ASR_MODEL_NAME,
                    file=("audio.wav", audio_buffer, "audio/wav"),
                    response_format="text"
                )
                yield {"type": "stt-final", "text": response.strip()}
            except Exception as e:
                yield {"type": "stt-error", "message": f"语音识别失败：{str(e)}"}
            return
        
        # 后备模拟模式
        yield {"type": "stt-interim", "text": "正在识别语音..."}
        await asyncio.sleep(0.5)
        yield {"type": "stt-interim", "text": "正在识别语音... 请稍候"}
        await asyncio.sleep(0.5)
        yield {"type": "stt-final", "text": "这是一个测试语音识别结果（模拟模式）"}

# 创建全局ASR服务实例
asr_service = ASRService()