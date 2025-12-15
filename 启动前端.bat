@echo off
chcp 65001 >nul
echo ========================================
echo   启动聊天占卜偶像 - 前端服务
echo ========================================
echo.

cd frontend

echo [1/2] 检查 Node.js 环境...
node --version
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

npm --version
if errorlevel 1 (
    echo 错误: 未找到 npm，请先安装 Node.js
    pause
    exit /b 1
)

echo.
echo [2/2] 检查依赖包...
if not exist "node_modules\" (
    echo 安装依赖包（这可能需要几分钟）...
    npm install
) else (
    echo 依赖包已存在，跳过安装
)

echo.
echo ========================================
echo   正在启动前端服务...
echo   服务地址: http://localhost:3000
echo ========================================
echo.
echo 提示: 请保持此窗口运行，不要关闭
echo 提示: 按 Ctrl+C 可以停止服务
echo 提示: 确保后端服务已在运行（http://localhost:5000）
echo.

npm run dev

pause

