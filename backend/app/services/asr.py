from openai import AsyncOpenAI
from app.core.config import settings
from typing import AsyncGenerator, Dict
import asyncio

class ASRService:
    """语音转文本(ASR)服务：封装OpenAI Whisper接口"""
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sk-test-placeholder-key":
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                print(f"ASR初始化失败: {e}")
                self.client = None

    async def transcribe_stream(
        self, audio_chunks: AsyncGenerator[bytes, None]
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式处理音频，返回识别结果"""
        if not self.client:
            # 模拟语音识别
            yield {"type": "stt-interim", "text": "正在识别语音..."}
            await asyncio.sleep(0.5)
            yield {"type": "stt-interim", "text": "正在识别语音... 请稍候"}
            await asyncio.sleep(0.5)
            yield {"type": "stt-final", "text": "这是一个测试语音识别结果"}
            return
            
        # 模拟中间识别反馈
        yield {"type": "stt-interim", "text": "正在识别语音..."}
        await asyncio.sleep(0.5)
        yield {"type": "stt-interim", "text": "正在识别语音... 请稍候"}
        await asyncio.sleep(0.5)

        # 收集完整音频
        audio_buffer = b""
        async for chunk in audio_chunks:
            audio_buffer += chunk

        # 调用Whisper识别
        try:
            response = await self.client.audio.transcriptions.create(
                model=settings.ASR_MODEL_NAME,
                file=("audio.wav", audio_buffer, "audio/wav"),
                response_format="text"
            )
            yield {"type": "stt-final", "text": response.strip()}
        except Exception as e:
            yield {"type": "stt-error", "message": f"语音识别失败：{str(e)}"}

# 创建全局ASR服务实例
asr_service = ASRService()