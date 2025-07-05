# Git推送设置指南

## 🔐 GitHub身份验证问题解决

如果遇到 `Permission denied` 错误，说明需要设置GitHub身份验证。

## 🚀 解决方案

### 方案1：使用GitHub CLI（推荐）

1. **安装GitHub CLI**
   ```bash
   # macOS
   brew install gh
   
   # Windows
   winget install --id GitHub.cli
   ```

2. **登录GitHub**
   ```bash
   gh auth login
   ```
   按提示选择：
   - GitHub.com
   - HTTPS
   - Yes (authenticate Git)
   - Login with a web browser

3. **重新推送**
   ```bash
   git push -u origin main
   ```

### 方案2：使用个人访问令牌

1. **创建Personal Access Token**
   - 访问：https://github.com/settings/tokens
   - 点击 "Generate new token (classic)"
   - 选择权限：repo (完整权限)
   - 复制生成的token

2. **使用token推送**
   ```bash
   git remote set-url origin https://Terry-ten:<YOUR_TOKEN>@github.com/Terry-ten/VideoAutoProcess.git
   git push -u origin main
   ```

### 方案3：使用SSH密钥

1. **生成SSH密钥**
   ```bash
   ssh-keygen -t ed25519 -C "your-email@example.com"
   ```

2. **添加到GitHub**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   复制输出，在GitHub Settings > SSH keys 中添加

3. **修改远程仓库URL**
   ```bash
   git remote set-url origin git@github.com:Terry-ten/VideoAutoProcess.git
   git push -u origin main
   ```

## 📋 当前项目状态

✅ **已完成：**
- Git仓库已初始化
- 代码已提交到本地仓库
- 远程仓库已配置

⏳ **待完成：**
- GitHub身份验证
- 推送到远程仓库

## 🔧 手动上传方式

如果以上方法都不行，可以手动上传：

1. **创建ZIP文件**
   ```bash
   zip -r VideoAutoProcess.zip . -x "*.git*" "mongodb/data/*" "logs/*" "*.log"
   ```

2. **GitHub网页上传**
   - 访问：https://github.com/Terry-ten/VideoAutoProcess
   - 点击 "uploading an existing file"
   - 拖拽ZIP文件上传

## 💡 推荐步骤

1. 首先尝试GitHub CLI方案（最简单）
2. 如果不行，使用Personal Access Token
3. 最后考虑手动上传

---

🎯 **选择最适合您的方式完成代码上传！** 