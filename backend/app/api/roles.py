from fastapi import APIRouter, HTTPException
from typing import List
from app.models.role import Role, RoleCreateRequest
from app.core.config import settings

# 创建角色API路由
router = APIRouter(prefix=f"{settings.API_PREFIX}/roles", tags=["角色管理"])

# 模拟角色数据库
mock_roles_db: List[Role] = [
    Role(
        id="socrates",
        name="苏格拉底",
        description="古希腊哲学家，擅长诘问法引导思考",
        system_prompt="你是苏格拉底，用诘问法引导用户思考，通过3-5个问题帮助用户自己找到答案。语气温和耐心。",
        default_voice="echo",
        avatar_url="https://picsum.photos/id/1025/200/200"
    ),
    Role(
        id="sherlock",
        name="夏洛克·福尔摩斯",
        description="虚构侦探，观察力敏锐，逻辑推理能力强",
        system_prompt="你是夏洛克·福尔摩斯，注重细节和逻辑推理，语气自信略带傲慢，用短句增强节奏感。",
        default_voice="onyx",
        avatar_url="https://picsum.photos/id/1074/200/200"
    )
]

@router.get("/", response_model=List[Role], summary="获取所有角色列表")
async def get_all_roles():
    return mock_roles_db

@router.get("/{role_id}", response_model=Role, summary="获取单个角色详情")
async def get_role(role_id: str):
    role = next((r for r in mock_roles_db if r.id == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail=f"角色 {role_id} 不存在")
    return role

@router.post("/", response_model=Role, summary="创建新角色")
async def create_role(role_req: RoleCreateRequest):
    role_id = role_req.name.lower().replace(" ", "_") + f"_{len(mock_roles_db)}"
    new_role = Role(
        id=role_id,
        name=role_req.name,
        description=role_req.description,
        system_prompt=role_req.system_prompt,
        default_voice=role_req.default_voice,
        avatar_url=f"https://picsum.photos/id/{1080 + len(mock_roles_db)}/200/200"
    )
    mock_roles_db.append(new_role)
    return new_role
