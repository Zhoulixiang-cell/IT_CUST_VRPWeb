from pydantic_settings import BaseSettings
import os
from typing import Optional

class Settings(BaseSettings):
    """全局配置类：从.env加载配置，无则使用默认值"""
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gpt-4o"
    TTS_MODEL_NAME: str = "tts-1"
    ASR_MODEL_NAME: str = "whisper-1"

    # 服务配置
    API_PREFIX: str = "/api"
    WS_PREFIX: str = "/ws"
    MAX_CONVERSATION_HISTORY: int = 20  # 对话历史最大长度

    class Config:
        # 从backend根目录的.env文件加载配置
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        env_file_encoding = "utf-8"

# 创建全局配置实例
settings = Settings()
