# YouTube RSS监控系统

一个基于RSS的YouTube频道监控系统，自动获取频道最新视频并提供Web界面管理。

## 🚀 快速开始

### 📦 下载项目
```bash
git clone https://github.com/Terry-ten/VideoAutoProcess.git
cd VideoAutoProcess
```

### 🔧 系统要求
- Python 3.9+
- MongoDB 4.0+
- 网络连接

### ⚡ 一键启动

#### Windows用户
```batch
# 双击运行或命令行执行
start.bat
```

#### macOS用户
```bash
# 安装依赖
pip3 install -r requirements.txt

# 启动MongoDB
./mongodb/bin/mongod --dbpath ./mongodb/data/db --bind_ip 127.0.0.1 --port 27017 --fork --logpath ./mongodb/mongodb.log

# 启动Web服务
python3 web_ui.py
```

#### Linux用户
```bash
# 安装依赖
pip3 install -r requirements.txt

# 启动MongoDB（如果未安装）
sudo apt-get install mongodb
sudo systemctl start mongod

# 启动Web服务
python3 web_ui.py
```

### 🌐 访问系统
启动成功后，在浏览器中访问：
**http://localhost:8080**

### 📖 详细安装指南
- **Windows用户**: [WINDOWS_SETUP.md](WINDOWS_SETUP.md)
- **macOS系统服务**: [SERVICE_GUIDE.md](SERVICE_GUIDE.md)
- **自动监控使用**: [AUTO_MONITOR_GUIDE.md](AUTO_MONITOR_GUIDE.md)

## 📁 项目结构

### 核心运行文件
- `web_ui.py` - Web服务主程序
- `auto_monitor.py` - 自动监控程序
- `main_rss.py` - RSS监控核心逻辑
- `youtube_rss.py` - YouTube RSS解析器
- `database_mongodb.py` - MongoDB数据库操作
- `config.py` - 配置文件

### 服务管理
- `install_service.sh` - 安装macOS系统服务
- `uninstall_service.sh` - 卸载macOS系统服务
- `start.bat` - Windows启动脚本
- `SERVICE_GUIDE.md` - macOS详细使用说明
- `WINDOWS_SETUP.md` - Windows安装指南

### 其他文件
- `requirements.txt` - Python依赖包
- `templates/` - Web界面模板
- `mongodb/` - MongoDB数据库文件
- `logs/` - 系统日志文件

## 🎯 功能特点

- ✅ **自动监控** - 定时检查频道更新
- ✅ **Web界面** - 现代化管理界面
- ✅ **图片下载** - 视频缩略图下载
- ✅ **批量操作** - 视频状态批量管理
- ✅ **系统服务** - 开机自启动，后台运行

## 📋 使用流程

### 1️⃣ 添加YouTube频道
1. 在Web界面左侧"添加频道"区域
2. 输入YouTube频道URL（支持多种格式）
3. 点击"添加"按钮

### 2️⃣ 启动自动监控
1. 在"系统控制"区域找到"自动监控"
2. 点击"启动"按钮
3. 设置监控间隔（建议1-3小时）

### 3️⃣ 查看监控结果
- **最近视频**: 右侧显示最新发现的视频
- **频道详情**: 点击"查看所有视频"查看频道完整视频列表
- **统计信息**: 查看频道数量、视频总数等统计数据

### 4️⃣ 管理视频
- **下载缩略图**: 点击视频封面上的绿色下载按钮
- **标记状态**: 批量选择视频并标记为"已读"
- **频道管理**: 更新单个频道或删除不需要的频道

## 📋 服务管理

```bash
# 启动服务
launchctl start com.youtube.monitor

# 停止服务
launchctl stop com.youtube.monitor

# 查看日志
tail -f logs/youtube_monitor.log
```

详细说明请参考 [SERVICE_GUIDE.md](SERVICE_GUIDE.md)

## 🔧 开发者指南

### Git仓库管理
如需推送代码到GitHub，请参考 [GIT_SETUP.md](GIT_SETUP.md)

### 项目贡献
1. Fork本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

### 问题反馈
如遇到问题，请在GitHub Issues中提交详细描述。

---

🎬 **YouTube RSS监控系统 - 让您轻松跟踪喜爱的YouTube频道！** 