#!/bin/bash

echo "🗑️  卸载YouTube RSS监控系统服务"
echo "=================================="

# 停止服务
echo "🛑 停止服务..."
launchctl stop com.youtube.monitor 2>/dev/null || true

# 卸载服务
echo "📤 卸载服务..."
launchctl unload ~/Library/LaunchAgents/com.youtube.monitor.plist 2>/dev/null || true

# 删除配置文件
echo "🗑️  删除配置文件..."
rm -f ~/Library/LaunchAgents/com.youtube.monitor.plist
rm -f com.youtube.monitor.plist

# 停止相关进程
echo "🔚 停止相关进程..."
pkill -f "python.*web_ui.py" 2>/dev/null || true
pkill -f "python.*auto_monitor.py" 2>/dev/null || true

# 检查是否卸载成功
if launchctl list | grep -q com.youtube.monitor; then
    echo "⚠️  服务可能仍在运行，请手动检查"
else
    echo "✅ 服务已成功卸载！"
fi

echo ""
echo "💡 注意：日志文件和数据库文件保留在项目目录中"
echo "如需完全清理，请手动删除 logs/ 目录和 MongoDB 数据" 