@echo off
chcp 65001 >nul
echo 🚀 启动YouTube RSS监控系统
echo ========================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：Python未安装或未添加到PATH
    echo 请安装Python 3.9+并添加到系统PATH
    pause
    exit /b 1
)

REM 检查依赖包
echo 📦 检查依赖包...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 📦 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        pause
        exit /b 1
    )
)

REM 检查MongoDB是否运行
echo 🗄️ 检查MongoDB服务...
sc query MongoDB | find "RUNNING" >nul 2>&1
if errorlevel 1 (
    echo ⚠️ MongoDB服务未运行，尝试启动...
    net start MongoDB >nul 2>&1
    if errorlevel 1 (
        echo ❌ 无法启动MongoDB服务
        echo 请手动安装并启动MongoDB
        pause
        exit /b 1
    )
)

REM 创建日志目录
if not exist "logs" mkdir logs

REM 启动Web服务
echo 🌐 启动Web服务...
echo 📍 访问地址: http://localhost:8080
echo 💡 按 Ctrl+C 停止服务
echo ========================
python web_ui.py
pause 