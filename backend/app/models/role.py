from pydantic import BaseModel, Field
from typing import Optional

class Role(BaseModel):
    """角色数据模型：定义角色的核心属性"""
    id: str = Field(..., description="角色唯一标识")
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="角色简介")
    system_prompt: str = Field(..., description="角色的System Prompt")
    default_voice: Optional[str] = Field("alloy", description="默认TTS语音")
    avatar_url: Optional[str] = Field(None, description="角色头像URL")

class RoleCreateRequest(BaseModel):
    """角色创建请求模型"""
    name: str
    description: str
    system_prompt: str
    default_voice: Optional[str] = "alloy"
