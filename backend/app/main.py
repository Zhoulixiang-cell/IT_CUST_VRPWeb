from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.roles import router as roles_router
from app.core.config import settings

# 创建FastAPI应用
app = FastAPI(
    title="AI角色扮演聊天系统",
    description="基于FastAPI+OpenAI的多角色实时聊天系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需改为具体前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(roles_router)
app.include_router(chat_router)

# 健康检查接口
@app.get("/health", summary="服务健康检查")
async def health_check():
    return {"status": "healthy", "service": "ai-roleplay-chat-backend", "version": "1.0.0"}

# 启动命令：uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
