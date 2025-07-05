# 自动监控功能使用指南

## 🎯 功能概述

自动监控功能可以定时检查所有YouTube频道的更新，自动发现新视频并添加到数据库中。

## 🔄 启动方法

### 方法1：Web界面启动（推荐）
1. 访问 http://localhost:8080
2. 在"系统控制"区域找到"自动监控"
3. 点击"启动"按钮
4. 输入监控间隔小时数（建议1-6小时）
5. 确认启动

### 方法2：命令行启动

#### macOS/Linux
```bash
# 前台运行（会占用终端）
python3 auto_monitor.py --hours 1

# 后台运行
nohup python3 auto_monitor.py --hours 1 > logs/auto_monitor.log 2>&1 &

# 测试运行（只执行一次检查）
python3 auto_monitor.py --test

# 查看状态
python3 auto_monitor.py --status
```

#### Windows
```batch
# 前台运行
python auto_monitor.py --hours 1

# 后台运行
start /B python auto_monitor.py --hours 1

# 测试运行
python auto_monitor.py --test
```

### 方法3：系统服务启动（仅macOS）
```bash
# 启动系统服务（包含Web服务和自动监控功能）
launchctl start com.youtube.monitor

# 然后通过Web界面启动自动监控
```

## 🛑 关闭方法

### 方法1：Web界面关闭（推荐）
1. 访问 http://localhost:8080
2. 在"系统控制"区域找到"自动监控"
3. 点击"停止"按钮
4. 确认关闭

### 方法2：命令行关闭

#### macOS/Linux
```bash
# 查找进程
ps aux | grep auto_monitor

# 终止进程
pkill -f "python.*auto_monitor"

# 或者使用PID
kill <PID>
```

#### Windows
```batch
# 查找进程
tasklist /FI "IMAGENAME eq python.exe"

# 终止所有Python进程（注意：会关闭所有Python程序）
taskkill /F /IM python.exe

# 或者使用任务管理器手动结束
```

## 📊 监控状态查看

### Web界面查看
- 访问 http://localhost:8080
- "自动监控"状态显示：
  - 🟢 "运行中" - 正在监控
  - 🔴 "已停止" - 未运行
  - 显示启动时间

### 命令行查看
```bash
# macOS/Linux
ps aux | grep auto_monitor
lsof -i :8080

# Windows
tasklist /FI "IMAGENAME eq python.exe"
netstat -an | find "8080"
```

### 日志查看
```bash
# 查看监控日志
tail -f logs/auto_monitor.log

# 查看Web服务日志
tail -f logs/youtube_monitor.log

# 查看最近的监控活动
python3 auto_monitor.py --status
```

## ⚙️ 监控配置

### 监控间隔设置
- **1小时**：适合重要频道，及时获取更新
- **3小时**：适合一般频道，平衡及时性和资源消耗
- **6小时**：适合更新不频繁的频道
- **12小时**：适合偶尔更新的频道

### 自定义配置
修改 `config.py` 文件：
```python
# 默认检查间隔（秒）
CHECK_INTERVAL = 3600  # 1小时

# 每次检查的最大视频数
MAX_VIDEOS_PER_CHECK = 50

# 数据保留天数
RETENTION_DAYS = 365
```

## 🔧 故障排除

### 自动监控无法启动
1. **检查Python环境**
   ```bash
   python3 --version
   pip3 list | grep -E "(requests|schedule|pymongo)"
   ```

2. **检查MongoDB连接**
   ```bash
   python3 -c "from database_mongodb import DatabaseMongoDB; db = DatabaseMongoDB(); print(db.test_connection())"
   ```

3. **检查网络连接**
   ```bash
   curl -I https://www.youtube.com/feeds/videos.xml?channel_id=UCBJycsmduvYEL83R_U4JriQ
   ```

### 监控进程异常退出
1. **查看错误日志**
   ```bash
   cat logs/auto_monitor.log
   cat logs/youtube_monitor_error.log
   ```

2. **重启服务**
   ```bash
   # Web界面重启
   点击"停止" → 等待2秒 → 点击"启动"
   
   # 命令行重启
   pkill -f auto_monitor
   python3 auto_monitor.py --hours 1
   ```

### 监控频率异常
1. **检查系统时间**
   ```bash
   date
   ```

2. **检查进程状态**
   ```bash
   ps aux | grep auto_monitor
   ```

3. **重新设置监控间隔**
   - 通过Web界面停止并重新启动
   - 设置新的监控间隔

## 💡 最佳实践

### 推荐设置
- **监控间隔**：1-3小时
- **运行方式**：Web界面启动
- **监控时间**：24小时持续运行

### 性能优化
- 定期清理日志文件
- 监控频道数量控制在50个以内
- 定期备份MongoDB数据

### 安全建议
- 仅在本地网络访问
- 定期更新依赖包
- 监控系统资源使用情况

## 📈 监控效果

### 成功指标
- ✅ 新视频及时发现并添加
- ✅ 监控日志正常记录
- ✅ 系统资源占用合理
- ✅ 错误率低于5%

### 监控数据
- 检查频道数量
- 发现新视频数量
- 检查耗时
- 错误次数

---

🎬 **自动监控让您永不错过喜爱频道的最新内容！** 