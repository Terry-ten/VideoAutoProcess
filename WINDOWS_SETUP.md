# Windows用户安装指南

## 📋 系统要求

- Windows 10/11
- Python 3.9+
- Git（可选）

## 🚀 安装步骤

### 1. 安装Python
1. 访问 https://www.python.org/downloads/
2. 下载并安装Python 3.9或更高版本
3. 安装时勾选"Add Python to PATH"

### 2. 安装MongoDB
1. 访问 https://www.mongodb.com/try/download/community
2. 下载MongoDB Community Server
3. 安装后启动MongoDB服务

### 3. 下载项目
```bash
# 使用Git克隆
git clone <your-repo-url>
cd VideoURLGet

# 或者直接下载ZIP文件并解压
```

### 4. 安装依赖
```bash
pip install -r requirements.txt
```

### 5. 配置MongoDB
```bash
# 创建MongoDB数据目录
mkdir mongodb\data\db

# 启动MongoDB（如果没有作为服务运行）
mongod --dbpath mongodb\data\db
```

## 🎯 启动系统

### 方法1：手动启动（推荐新手）
```bash
# 启动Web服务
python web_ui.py
```
然后访问 http://localhost:8080

### 方法2：使用启动脚本
创建 `start.bat` 文件：
```batch
@echo off
echo 启动YouTube RSS监控系统
echo ========================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：Python未安装或未添加到PATH
    pause
    exit /b 1
)

REM 启动Web服务
echo 启动Web服务...
python web_ui.py
pause
```

### 方法3：作为Windows服务运行
1. 安装NSSM（Non-Sucking Service Manager）
2. 使用NSSM将Python脚本注册为Windows服务

## 🔄 自动监控使用

### 启动自动监控
1. **Web界面启动**（推荐）
   - 访问 http://localhost:8080
   - 点击"启动"按钮
   - 设置监控间隔（小时）

2. **命令行启动**
   ```bash
   # 前台运行
   python auto_monitor.py --hours 1
   
   # 后台运行（需要额外工具）
   start /B python auto_monitor.py --hours 1
   ```

### 关闭自动监控
1. **Web界面关闭**
   - 访问 http://localhost:8080
   - 点击"停止"按钮

2. **命令行关闭**
   ```bash
   # 查找并终止进程
   taskkill /F /IM python.exe
   
   # 或者使用任务管理器手动结束进程
   ```

## 📁 Windows文件结构

```
VideoURLGet/
├── web_ui.py              # Web服务主程序
├── auto_monitor.py        # 自动监控程序
├── main_rss.py           # RSS监控核心逻辑
├── youtube_rss.py        # YouTube RSS解析器
├── database_mongodb.py   # MongoDB数据库操作
├── config.py             # 配置文件
├── requirements.txt      # Python依赖包
├── start.bat             # Windows启动脚本
├── templates/            # Web界面模板
├── mongodb/              # MongoDB数据库文件
└── logs/                 # 系统日志文件
```

## 🛠️ 常见问题

### Q: MongoDB连接失败
A: 确保MongoDB服务正在运行
```bash
# 检查MongoDB服务状态
sc query MongoDB

# 启动MongoDB服务
net start MongoDB
```

### Q: 端口8080被占用
A: 修改 `web_ui.py` 中的端口号
```python
app.run(host='127.0.0.1', port=8081, debug=False, threaded=True)
```

### Q: 自动监控无法启动
A: 检查Python进程和权限
```bash
# 查看Python进程
tasklist /FI "IMAGENAME eq python.exe"

# 以管理员权限运行命令提示符
```

## 🔧 Windows服务安装（高级用户）

### 使用NSSM安装服务
1. 下载NSSM：https://nssm.cc/download
2. 解压到系统PATH目录
3. 安装服务：
```bash
nssm install YouTubeMonitor
# 在GUI中设置：
# Path: C:\Python39\python.exe
# Arguments: C:\path\to\VideoURLGet\web_ui.py
# Startup directory: C:\path\to\VideoURLGet
```

### 服务管理
```bash
# 启动服务
nssm start YouTubeMonitor

# 停止服务
nssm stop YouTubeMonitor

# 删除服务
nssm remove YouTubeMonitor
```

## 💡 使用建议

1. **开发环境**：使用手动启动方式
2. **生产环境**：安装为Windows服务
3. **临时使用**：直接运行 `python web_ui.py`
4. **长期使用**：配置开机自启动

## 📞 技术支持

如果遇到问题：
1. 检查Python和MongoDB是否正确安装
2. 查看 `logs/` 目录中的错误日志
3. 确认防火墙没有阻止端口8080
4. 检查依赖包是否完整安装

---

🎬 **YouTube RSS监控系统 - Windows版本使用指南** 