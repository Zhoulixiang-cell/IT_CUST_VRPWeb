@echo off
chcp 65001 > nul
title AI角色扮演项目启动器

echo.
echo ==========================================
echo    AI 角色扮演项目启动器
echo ==========================================
echo.

echo [1/3] 检查项目环境...
if not exist "backend\app\main.py" (
    echo 错误: 未找到后端文件，请确认在正确目录
    pause
    exit /b 1
)

if not exist "frontend\package.json" (
    echo 错误: 未找到前端文件，请确认在正确目录
    pause
    exit /b 1
)

echo [2/3] 启动后端服务 (端口: 8000)...
cd backend
start "AI后端服务" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..

echo [3/3] 启动前端服务 (端口: 3001)...
cd frontend
start "AI前端界面" cmd /k "npm run dev"
cd ..

echo.
echo ==========================================
echo  🎉 项目启动完成！
echo ==========================================
echo.
echo 📱 前端访问地址: http://localhost:3001
echo 🔧 后端API地址:  http://localhost:8000
echo 📖 API文档地址:  http://localhost:8000/docs
echo.
echo 💡 温馨提示:
echo    - 如需配置API密钥，请编辑 backend\.env 文件
echo    - 详细配置说明请查看 "多大模型支持配置指南.md"
echo    - 关闭此窗口不会停止服务，请在对应终端窗口按 Ctrl+C
echo.
echo 按任意键退出启动器...
pause > nul