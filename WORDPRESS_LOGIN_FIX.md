# WordPress OAuth "浏览器不安全" 错误解决方案

## 问题

访问 WordPress OAuth 授权页面时显示：
```
无法登录
此浏览器或应用可能不安全。
```

## 原因

WordPress.com 使用 Google OAuth，Google 会检测并阻止：
- 自动化浏览器（如 Selenium、Puppeteer）
- 不受信任的浏览器
- 某些嵌入式 webview

## 解决方案

### 方案 1: 使用手动 Python 脚本（推荐）✅

这个脚本会在你的默认浏览器中打开 OAuth 页面，然后你手动完成授权。

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 wordpress-oauth-manual.py
```

**步骤：**
1. 脚本打开浏览器到 WordPress 授权页面
2. 在浏览器中登录 WordPress.com（使用你常用的浏览器，如 Chrome/Safari）
3. 点击"授权"按钮
4. 浏览器会重定向到 `http://localhost:3000/api/platforms/wordpress/callback?code=...`
5. 复制完整的重定向 URL
6. 粘贴到脚本提示符
7. 脚本自动完成 OAuth 流程

### 方案 2: 手动复制授权 URL 到浏览器

```bash
# 1. 获取授权 URL
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NCwiZW1haWwiOiJsaXUubHVjaWFuQGljbG91ZC5jb20iLCJuYW1lIjpudWxsLCJpYXQiOjE3NjA0OTkyMDksImV4cCI6MTc2MzA5MTIwOX0.dK8n-8nq22ZpEuwCPMAcTGc0PCOIxgQvloXE-CeS_Q0"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:3000/api/platforms/wordpress/auth-url

# 输出类似：
# {
#   "authUrl": "https://public-api.wordpress.com/oauth2/authorize?...",
#   "state": "abc123..."
# }
```

**步骤：**
1. 复制 `authUrl` 的值
2. 在 Chrome/Safari 中打开这个 URL（不要用无痕模式）
3. 登录 WordPress.com
4. 点击"授权"
5. 浏览器重定向到 `http://localhost:3000/api/platforms/wordpress/callback?code=xxx&state=xxx`
6. OAuth 自动完成！

### 方案 3: 使用 Chrome（不是无痕模式）

```bash
# 1. 运行 CLI 命令
marketingmind hub connect wordpress

# 2. 当浏览器打开时：
#    - 确保使用的是 Chrome（不是无痕窗口）
#    - 确保已经登录过 Google 账号
#    - 如果看到"浏览器不安全"，点击"了解详情"
#    - 选择"继续使用此浏览器"
```

### 方案 4: 使用 Safari

Safari 通常不会被 Google OAuth 标记为不安全：

```bash
# 1. 设置 Safari 为默认浏览器（临时）
# 2. 运行命令
marketingmind hub connect wordpress

# 3. Safari 会打开授权页面
# 4. 完成授权
```

### 方案 5: 手动构建 OAuth URL（开发者方式）

如果所有方法都失败，可以手动完成 OAuth：

```bash
# 1. 构建授权 URL（已经帮你生成好了）
open "https://public-api.wordpress.com/oauth2/authorize?client_id=126390&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fapi%2Fplatforms%2Fwordpress%2Fcallback&response_type=code&scope=global&state=YOUR_STATE_HERE"

# 注意：YOUR_STATE_HERE 需要从数据库获取
# 或者使用 wordpress-oauth-manual.py 脚本
```

## 推荐使用：wordpress-oauth-manual.py 脚本

这是最可靠的方法！

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
python3 wordpress-oauth-manual.py
```

**为什么推荐：**
- ✅ 使用你的默认浏览器（不会被标记为不安全）
- ✅ 自动处理所有 OAuth 步骤
- ✅ 清晰的指示和错误处理
- ✅ 验证连接是否成功

## 完成后验证

```bash
# 检查连接状态
marketingmind hub connections

# 应该显示：
# Platform Connections:
#
# WORDPRESS
#   Connected: [日期]
#   Username: [用户名]
#   Sites: [数量]
```

## 常见问题

### Q1: 为什么 `open` 命令打开的浏览器被标记为不安全？

**A:** `open` 命令可能会打开一个新的浏览器实例，Google 会检测到这不是用户的主浏览器。

**解决:** 手动复制 URL 并在已经打开的浏览器标签页中打开。

### Q2: 我可以跳过 OAuth 直接使用 API Key 吗？

**A:** WordPress.com 不支持 API Key，必须使用 OAuth。但你可以考虑：
- 使用 Ghost（支持 API Key）
- 使用 Dev.to（支持 API Key）

```bash
# 连接 Ghost（不需要 OAuth）
marketingmind hub connect ghost

# 连接 Dev.to（不需要 OAuth）
marketingmind hub connect devto
```

### Q3: OAuth 连接后会过期吗？

**A:** 是的，OAuth token 可能会过期。到期后重新运行：

```bash
python3 wordpress-oauth-manual.py
# 或
marketingmind hub connect wordpress
```

### Q4: 可以在生产环境使用吗？

**A:** 可以，但需要：
1. 更新 `.env` 中的 `WORDPRESS_REDIRECT_URI`
2. 在 WordPress Developer Console 添加生产环境的 redirect URL
3. 使用生产环境的域名（不是 localhost）

## 技术细节

### OAuth Flow

1. **获取授权 URL**: `/api/platforms/wordpress/auth-url`
   - 生成 state
   - 保存 state → user_id 映射到数据库
   - 返回授权 URL

2. **用户授权**: `https://public-api.wordpress.com/oauth2/authorize`
   - 用户在 WordPress.com 登录
   - 点击授权
   - WordPress 重定向回 callback URL

3. **回调处理**: `/api/platforms/wordpress/callback`
   - 从 state 检索 user_id
   - 用 code 交换 access token
   - 保存 token 和用户信息

### 为什么需要 state？

- **安全性**: 防止 CSRF 攻击
- **用户映射**: 在无认证的 callback 中识别用户
- **一次性使用**: 使用后立即删除

### 数据库中的记录

```sql
-- oauth_states 表
SELECT * FROM oauth_states WHERE platform = 'wordpress';
-- state, user_id, expires_at

-- platform_connections 表
SELECT * FROM platform_connections WHERE platform = 'wordpress';
-- user_id (本地 ID), access_token, metadata (包含 WordPress 用户信息)
```

## 故障排查

### 1. "Invalid or expired OAuth state"

**原因**: State 过期（10 分钟）或已使用

**解决**: 重新开始 OAuth 流程

### 2. "Cannot connect to Publishing Hub"

**原因**: Hub 服务器未运行

**解决**:
```bash
./start-hub.sh
curl http://localhost:3000/health
```

### 3. 授权后没有反应

**检查日志**:
```bash
tail -f hub-server.log
```

查找：
- "WordPress OAuth callback error"
- "Database query error"
- HTTP 状态码（应该是 302 或 200）

### 4. "此浏览器或应用可能不安全"

**这就是本文档要解决的问题！** 使用上面的方案 1 或方案 2。

## 总结

**最简单的方法：**

```bash
python3 wordpress-oauth-manual.py
```

按照屏幕提示操作，在你的常用浏览器中完成授权，然后复制 redirect URL 回来。

**完成后：**

```bash
# 验证连接
marketingmind hub connections

# 测试发布
marketingmind blog-quick "测试 WordPress 发布" --now

# 查看队列
marketingmind hub queue
```

---

**如果还有问题，请查看 hub-server.log 日志文件并告诉我具体的错误信息。**
