# 🔧 GitHub 推送认证 - 快速修复

## 问题

```
致命错误：could not read Username for 'https://github.com': Device not configured
```

这是因为 GitHub 需要认证才能推送代码。

---

## 🚀 快速解决（3 步）

### 方法 1: SSH 密钥（推荐 - 最安全）

```bash
# 1. 运行认证设置脚本
./setup_github_auth.sh
# 选择 "1. SSH 密钥"

# 2. 按照提示操作（自动生成密钥并指导你添加到 GitHub）

# 3. 测试推送
cd interview_assistant
git push -u origin main
```

### 方法 2: Personal Access Token（最简单）

```bash
# 1. 创建 Token
# 访问: https://github.com/settings/tokens
# 点击: Generate new token (classic)
# 权限: 勾选 "repo"
# 复制 token

# 2. 配置 Git
cd interview_assistant
git remote set-url origin https://<YOUR_TOKEN>@github.com/q1q1-spefic/interview_assistant.git

# 3. 推送
git push -u origin main
```

### 方法 3: 使用设置脚本（自动化）

```bash
# 直接运行，选择你喜欢的方式
./setup_github_auth.sh
```

---

## ✅ 验证成功

推送成功后会看到：

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 1.23 KiB | 1.23 MiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/q1q1-spefic/interview_assistant.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## 🔄 之后怎么办？

认证设置好后，只需重新启动发布系统：

```bash
# 继续永久运行
python3 github_gradual_publisher.py --forever

# 或单次测试
python3 github_gradual_publisher.py --once
```

系统会自动继续之前的进度！✨

---

## 💡 推荐方式

**SSH 密钥**最安全，一次设置终身使用：
- ✅ 不需要保存密码/token
- ✅ 更安全
- ✅ 所有仓库通用

**Personal Access Token** 最快速：
- ✅ 5 分钟搞定
- ❌ 需要妥善保存 token
- ❌ Token 可能过期

---

## 🆘 还是不行？

检查：
1. GitHub 仓库是否存在：https://github.com/q1q1-spefic/interview_assistant
2. 你是否有仓库的写权限
3. Token 权限是否包含 "repo"

需要帮助？查看日志：
```bash
tail -f github_publisher.log
```
