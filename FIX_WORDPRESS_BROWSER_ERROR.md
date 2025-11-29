# 🔧 修复 WordPress "浏览器不安全" 错误

## 问题

当你运行 `marketingmind hub connect wordpress` 时，浏览器显示：

```
无法登录
此浏览器或应用可能不安全。
```

## ✅ 快速解决方案

使用我创建的 Python 脚本：

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 wordpress-oauth-manual.py
```

## 📋 步骤说明

### 1. 运行脚本

```bash
python3 wordpress-oauth-manual.py
```

脚本会显示：

```
============================================================
WordPress OAuth Manual Flow
============================================================

📋 Step 1: Getting authorization URL...
✓ Auth URL obtained
✓ State: abc123...

🌐 Step 2: Opening browser for authorization...

URL: https://public-api.wordpress.com/oauth2/authorize?...

✓ Browser opened

============================================================
INSTRUCTIONS:
============================================================
1. A browser window should have opened with WordPress.com
2. If not, copy the URL above and paste it in your browser
3. Login to WordPress.com
4. Click 'Authorize' to grant access
5. You will be redirected to a URL like:
   http://localhost:3000/api/platforms/wordpress/callback?code=...
6. Copy the ENTIRE redirect URL and paste it below
============================================================
```

### 2. 在浏览器中授权

- 脚本会自动打开你的默认浏览器
- 如果没有自动打开，复制显示的 URL 到浏览器
- **使用 Chrome 或 Safari（不要用无痕模式）**
- 登录 WordPress.com
- 点击 "Authorize" 按钮

### 3. 复制 Redirect URL

授权后，浏览器会重定向到类似这样的 URL：

```
http://localhost:3000/api/platforms/wordpress/callback?code=abc123xyz...&state=def456...
```

**复制整个 URL**（从 `http` 到最后）

### 4. 粘贴到脚本

回到终端，在提示符处粘贴 URL：

```
📝 Step 3: After authorization, paste the redirect URL:
Redirect URL: http://localhost:3000/api/platforms/wordpress/callback?code=...

✓ Authorization code: abc123...
✓ State: def456...

🔐 Step 4: Completing OAuth flow...

✅ OAuth completed successfully!

✓ Step 5: Verifying connection...

✅ WordPress connected!
   Username: liulucian6
   Display name: Lucian Liu

============================================================
✅ Done! You can now use:
   marketingmind hub connections
   marketingmind blog-quick "topic" --now
============================================================
```

## ✅ 验证成功

```bash
# 检查连接
marketingmind hub connections

# 应该显示：
# Platform Connections:
#
# WORDPRESS
#   Connected: [今天日期]
#   Username: [你的用户名]
#   Sites: [数量]
```

## 🎯 现在可以发布了！

```bash
# 测试快速发布
marketingmind blog-quick "测试 WordPress 发布" --now

# 查看队列
marketingmind hub queue

# 查看历史
marketingmind hub history
```

## 🆘 如果脚本失败

### 错误 1: "No module named 'requests'"

```bash
pip3 install requests
```

### 错误 2: "Failed to get authorization URL"

检查 Hub 是否运行：

```bash
./start-hub.sh
curl http://localhost:3000/health
```

### 错误 3: "No authorization code found in URL"

确保复制了**完整的 URL**，包括：
- `http://localhost:3000`
- `/api/platforms/wordpress/callback`
- `?code=...&state=...`

### 错误 4: 浏览器没有自动打开

手动复制脚本显示的 URL 到浏览器中打开。

## 💡 为什么这个方法有效？

1. **使用真实浏览器**: 脚本打开你的默认浏览器（Chrome/Safari），不是自动化浏览器
2. **手动授权**: 你亲自在浏览器中完成授权，Google 不会标记为不安全
3. **安全的回调**: 脚本使用正确的 OAuth 流程完成认证

## 📚 完整文档

详细说明请查看：`WORDPRESS_LOGIN_FIX.md`

## 🎉 成功后

你的 WordPress 账号已经连接到 MarketingMind AI！

现在你可以：

```bash
# 自动生成并发布博客
marketingmind blog-auto

# 或指定话题
marketingmind blog-quick "独立开发者营销指南" --now

# 查看发布状态
marketingmind hub queue
marketingmind hub history
```

---

**一键发布博客，就像发 Twitter 一样简单！** 🚀
