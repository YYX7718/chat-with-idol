@echo off
chcp 65001 >nul
echo ========================================
echo   启动聊天占卜偶像 - 后端服务
echo ========================================
echo.

cd backend

echo [1/2] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo.
echo [2/2] 检查依赖包...
if not exist "venv\" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 安装/更新依赖包...
pip install -r requirements.txt -q

echo.
echo ========================================
echo   正在启动后端服务...
echo   服务地址: http://localhost:5000
echo ========================================
echo.
echo 提示: 请保持此窗口运行，不要关闭
echo 提示: 按 Ctrl+C 可以停止服务
echo.

python app.py

pause

