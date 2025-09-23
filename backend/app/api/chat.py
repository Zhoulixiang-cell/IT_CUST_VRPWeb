from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from app.services.chat_servers import chat_service
from app.services.asr import asr_service
from app.services.tts import tts_service
from app.api.roles import mock_roles_db
from app.core.config import settings
from typing import AsyncGenerator

# 创建聊天API路由
router = APIRouter(prefix=f"{settings.API_PREFIX}/chat", tags=["聊天交互"])

@router.websocket(f"{settings.WS_PREFIX}/session/{settings.API_PREFIX.strip('/')}/{{session_id}}/{{role_id}}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: str,
    role_id: str,
    enable_tts: bool = Query(default=True, description="是否开启TTS音频返回")
):
    """实时聊天WebSocket接口"""
    # 校验角色并初始化会话
    role = next((r for r in mock_roles_db if r.id == role_id), None)
    if not role:
        await websocket.close(code=1008, reason=f"角色 {role_id} 不存在")
        return
    chat_service.init_session(session_id=session_id, role=role)

    await websocket.accept()
    try:
        while True:
            data = await websocket.receive()
            if "text" in data:
                # 处理文本输入
                user_input = data["text"]
                async for chat_data in chat_service.chat_with_llm_stream(
                    session_id=session_id,
                    user_input=user_input
                ):
                    if not enable_tts and chat_data["type"].startswith("tts-"):
                        continue
                    await websocket.send_json(chat_data)
            elif "bytes" in data:
                # 处理音频输入
                await websocket.send_json({"type": "stt-status", "message": "开始识别语音"})
                
                async def audio_generator():
                    yield data["bytes"]
                    
                async for asr_data in asr_service.transcribe_stream(audio_generator()):
                    await websocket.send_json(asr_data)
                    if asr_data["type"] == "stt-final":
                        async for chat_data in chat_service.chat_with_llm_stream(
                            session_id=session_id,
                            user_input=asr_data["text"]
                        ):
                            if not enable_tts and chat_data["type"].startswith("tts-"):
                                continue
                            await websocket.send_json(chat_data)
    except WebSocketDisconnect:
        print(f"会话 {session_id} 已断开")
    except Exception as e:
        await websocket.send_json({"type": "chat-error", "message": f"会话异常：{str(e)}"})
        await websocket.close(code=1011, reason=str(e))

@router.post("/asr", summary="语音转文本HTTP接口")
async def transcribe_audio(file: UploadFile = File(..., description="音频文件")):
    """通过HTTP上传音频文件，返回识别结果"""
    async def asr_generator():
        async for data in asr_service.transcribe_stream(file.file):
            yield f"data: {data}\n\n"
    return StreamingResponse(asr_generator(), media_type="text/event-stream")

@router.post("/tts", summary="文本转语音HTTP接口")
async def text_to_speech(
    text: str = Query(..., description="待转换文本"),
    voice: str = Query(default="alloy", description="TTS语音类型")
):
    """生成TTS音频，流式返回Base64块"""
    async def tts_generator():
        async for data in tts_service.text_to_speech_stream(text=text, voice=voice):
            yield f"data: {data}\n\n"
    return StreamingResponse(tts_generator(), media_type="text/event-stream")
