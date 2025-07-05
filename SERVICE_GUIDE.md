# YouTube RSS监控系统 - 服务管理指南

## 🎯 系统服务概述

YouTube RSS监控系统现已安装为macOS系统服务，具有以下特点：

- ✅ **开机自启动** - 系统启动时自动运行
- ✅ **后台运行** - 无需终端窗口，完全后台运行
- ✅ **自动重启** - 服务异常时自动重启
- ✅ **日志记录** - 完整的运行日志记录

## 🌐 访问地址

- **Web界面**: http://localhost:8080
- **系统状态**: 随时可以打开浏览器访问

## 📋 服务管理命令

### 基本操作
```bash
# 启动服务
launchctl start com.youtube.monitor

# 停止服务
launchctl stop com.youtube.monitor

# 重启服务
launchctl stop com.youtube.monitor && launchctl start com.youtube.monitor

# 查看服务状态
launchctl list | grep com.youtube.monitor
```

### 服务安装/卸载
```bash
# 安装服务（已完成）
./install_service.sh

# 卸载服务
./uninstall_service.sh
```

## 📝 日志管理

### 日志文件位置
- **运行日志**: `logs/youtube_monitor.log`
- **错误日志**: `logs/youtube_monitor_error.log`

### 查看日志
```bash
# 查看最新日志
tail -f logs/youtube_monitor.log

# 查看错误日志
tail -f logs/youtube_monitor_error.log

# 查看最后50行日志
tail -50 logs/youtube_monitor.log
```

## 🔧 故障排除

### 服务无法启动
1. 检查错误日志：`cat logs/youtube_monitor_error.log`
2. 检查MongoDB是否运行：`ps aux | grep mongod`
3. 检查端口是否被占用：`lsof -i :8080`

### 重置服务
```bash
# 完全重置服务
launchctl stop com.youtube.monitor
launchctl unload ~/Library/LaunchAgents/com.youtube.monitor.plist
launchctl load ~/Library/LaunchAgents/com.youtube.monitor.plist
launchctl start com.youtube.monitor
```

### 查看服务详细信息
```bash
# 查看服务详细状态
launchctl list com.youtube.monitor

# 查看服务配置
cat ~/Library/LaunchAgents/com.youtube.monitor.plist
```

## 🎉 使用方式

### 日常使用
1. **无需任何操作** - 服务自动运行
2. **查看监控** - 打开 http://localhost:8080
3. **管理频道** - 通过Web界面添加/删除频道
4. **启动自动监控** - 在Web界面点击"启动"按钮

### 系统重启后
- 服务会自动启动，无需手动操作
- 直接访问 http://localhost:8080 即可

## 🛡️ 数据安全

- **本地存储** - 所有数据存储在本地MongoDB
- **自动备份** - 建议定期备份 `mongodb/data/` 目录
- **日志轮转** - 日志文件会自动管理，无需手动清理

## 📞 技术支持

如果遇到问题，请：
1. 查看错误日志文件
2. 检查服务运行状态
3. 重启服务尝试解决

---

🎬 **YouTube RSS监控系统现已成为您Mac上的常驻服务！** 