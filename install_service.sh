#!/bin/bash

echo "🚀 安装YouTube RSS监控系统为macOS系统服务"
echo "=================================================="

# 检查当前目录
if [ ! -f "web_ui.py" ]; then
    echo "❌ 错误：请在项目根目录运行此脚本"
    exit 1
fi

# 停止现有进程
echo "🛑 停止现有进程..."
pkill -f "python.*web_ui.py" 2>/dev/null || true
pkill -f "python.*auto_monitor.py" 2>/dev/null || true

# 创建日志目录
echo "📁 创建日志目录..."
mkdir -p logs

# 获取当前目录的绝对路径
PROJECT_DIR=$(pwd)
echo "📍 项目目录: $PROJECT_DIR"

# 创建修正的plist文件
echo "📝 创建LaunchAgent配置文件..."
cat > com.youtube.monitor.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.youtube.monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$PROJECT_DIR/web_ui.py</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/youtube_monitor.log</string>
    
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/youtube_monitor_error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# 复制到LaunchAgents目录
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
echo "📋 复制配置文件到 $LAUNCH_AGENTS_DIR"
mkdir -p "$LAUNCH_AGENTS_DIR"
cp com.youtube.monitor.plist "$LAUNCH_AGENTS_DIR/"

# 加载服务
echo "🔄 加载系统服务..."
launchctl unload "$LAUNCH_AGENTS_DIR/com.youtube.monitor.plist" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS_DIR/com.youtube.monitor.plist"

# 启动服务
echo "▶️  启动服务..."
launchctl start com.youtube.monitor

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查服务状态
echo "🔍 检查服务状态..."
if launchctl list | grep -q com.youtube.monitor; then
    echo "✅ 服务已成功启动！"
    echo ""
    echo "📊 服务信息："
    launchctl list | grep com.youtube.monitor
    echo ""
    echo "🌐 访问地址: http://localhost:8080"
    echo "📝 日志文件: $PROJECT_DIR/logs/youtube_monitor.log"
    echo "❌ 错误日志: $PROJECT_DIR/logs/youtube_monitor_error.log"
    echo ""
    echo "🎉 安装完成！系统将在开机时自动启动YouTube RSS监控服务"
    echo ""
    echo "📋 常用命令："
    echo "  启动服务: launchctl start com.youtube.monitor"
    echo "  停止服务: launchctl stop com.youtube.monitor"
    echo "  重启服务: launchctl stop com.youtube.monitor && launchctl start com.youtube.monitor"
    echo "  卸载服务: launchctl unload ~/Library/LaunchAgents/com.youtube.monitor.plist"
    echo "  查看日志: tail -f $PROJECT_DIR/logs/youtube_monitor.log"
else
    echo "❌ 服务启动失败，请检查日志文件"
    echo "错误日志: $PROJECT_DIR/logs/youtube_monitor_error.log"
fi 