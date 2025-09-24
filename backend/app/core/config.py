from pydantic_settings import BaseSettings
import os
from typing import Optional, List
import json

class Settings(BaseSettings):
    """全局配置类：从.env加载配置，无则使用默认值"""
    # OpenAI配置（保留兼容性）
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL_NAME: str = "gpt-4o"
    TTS_MODEL_NAME: str = "tts-1"
    ASR_MODEL_NAME: str = "whisper-1"
    
    # 智谱AI配置
    ZHIPU_API_KEY: str = "your-zhipu-api-key-here"
    
    # 通义千问配置
    QWEN_API_KEY: str = ""
    
    # 讯飞语音配置
    XUNFEI_API_KEY: str = ""
    XUNFEI_APP_ID: str = ""
    XUNFEI_API_SECRET: str = ""
    
    # 百度语音配置
    BAIDU_APP_ID: str = ""
    BAIDU_API_KEY: str = ""
    BAIDU_SECRET_KEY: str = ""
    
    # 语音服务选择："openai", "baidu", "xunfei"
    ASR_PROVIDER: str = "xunfei"
    TTS_PROVIDER: str = "xunfei"
    
    # LLM服务选择："openai" 或 "zhipu" 或 "qwen"
    LLM_PROVIDER: str = "zhipu"

    # 数据库配置
    DATABASE_URL: Optional[str] = None
    
    # Redis配置
    REDIS_URL: Optional[str] = None
    
    # 应用配置
    DEBUG: bool = True
    SECRET_KEY: str = "default-secret-key"
    CORS_ORIGINS: str = '["http://localhost:3000"]'
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # 服务配置
    API_PREFIX: str = "/api"
    WS_PREFIX: str = "/ws"
    MAX_CONVERSATION_HISTORY: int = 20  # 对话历史最大长度
    
    @property
    def cors_origins_list(self) -> List[str]:
        """将CORS_ORIGINS字符串转换为列表"""
        try:
            return json.loads(self.CORS_ORIGINS)
        except:
            return ["http://localhost:3000"]

    class Config:
        # 从backend根目录的.env文件加载配置
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
        env_file_encoding = "utf-8"
        # 允许额外字段
        extra = 'allow'

# 创建全局配置实例
settings = Settings()
