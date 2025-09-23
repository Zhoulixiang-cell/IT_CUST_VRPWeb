from app.core.llm_client import llm_client
from app.services.tts import tts_service
from app.models.role import Role
from typing import List, Dict, AsyncGenerator
from app.core.config import settings

class ChatService:
    """聊天核心服务：整合LLM/ASR/TTS，管理对话历史"""
    def __init__(self):
        # 会话管理：{session_id: {"role": Role对象, "history": 对话历史}}
        self.sessions: Dict[str, Dict] = {}

    def init_session(self, session_id: str, role: Role) -> None:
        """初始化会话：绑定角色并初始化对话历史"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "role": role,
                "history": [{"role": "system", "content": role.system_prompt}]
            }

    def get_session_history(self, session_id: str) -> List[Dict[str, str]]:
        """获取会话历史，自动截断超长记录"""
        if session_id not in self.sessions:
            raise ValueError(f"会话 {session_id} 未初始化")
        history = self.sessions[session_id]["history"]
        if len(history) > settings.MAX_CONVERSATION_HISTORY:
            self.sessions[session_id]["history"] = history[-settings.MAX_CONVERSATION_HISTORY:]
        return self.sessions[session_id]["history"]

    async def chat_with_llm_stream(
        self, session_id: str, user_input: str
    ) -> AsyncGenerator[Dict[str, str], None]:
        """流式聊天：用户输入→LLM响应→TTS音频"""
        if session_id not in self.sessions:
            yield {"type": "chat-error", "message": "会话未初始化，请先选择角色"}
            return

        role = self.sessions[session_id]["role"]
        history = self.get_session_history(session_id)
        history.append({"role": "user", "content": user_input})

        # 流式获取LLM响应
        llm_response = []
        async for llm_data in llm_client.stream_chat_completion(history):
            if llm_data["type"] == "llm-token":
                llm_response.append(llm_data["token"])
                yield llm_data
            else:
                yield llm_data
                return

        # 生成TTS音频
        final_llm_text = "".join(llm_response)
        history.append({"role": "assistant", "content": final_llm_text})
        async for tts_data in tts_service.text_to_speech_stream(
            text=final_llm_text,
            voice=role.default_voice
        ):
            yield tts_data

# 创建全局聊天服务实例
chat_service = ChatService()
