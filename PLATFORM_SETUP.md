# 平台配置指南

## 📝 需要配置的平台

下面列出了每个新增平台需要的配置信息。

---

### ✅ Reddit（可选配置）

**无需配置即可使用** - Reddit的公开API不需要认证

**可选：增强功能需要API credentials**

1. 访问 https://www.reddit.com/prefs/apps
2. 创建应用（选择"script"类型）
3. 获取 `client_id` 和 `client_secret`

配置格式：
```json
{
  "reddit": {
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "user_agent": "MarketingMindAI/1.0"
  }
}
```

---

### ⚠️ YouTube（需要API Key）

**需要配置** - YouTube Data API需要API key

1. 访问 https://console.cloud.google.com/
2. 创建项目
3. 启用 "YouTube Data API v3"
4. 创建API密钥（Credentials → Create Credentials → API Key）

配置格式：
```json
{
  "youtube": {
    "api_key": "AIzaSy..."
  }
}
```

**费用**: 免费（每天10,000配额，足够使用）

---

### ⚠️ Instagram（需要Cookie或API）

**需要配置** - Instagram需要认证

**方法1: 使用Cookie（推荐）**
1. 登录Instagram
2. 打开浏览器开发者工具 (F12)
3. 转到Application/Storage → Cookies
4. 复制 `sessionid` cookie

配置格式：
```json
{
  "instagram": {
    "sessionid": "your_sessionid_cookie"
  }
}
```

**方法2: 使用Instagram Basic Display API**
- 更复杂，需要Facebook开发者账号
- 限制更多

---

### ⚠️ Facebook（需要Access Token）

**需要配置** - Facebook Graph API需要access token

1. 访问 https://developers.facebook.com/
2. 创建应用
3. 获取Access Token

配置格式：
```json
{
  "facebook": {
    "access_token": "your_access_token",
    "app_id": "your_app_id",
    "app_secret": "your_app_secret"
  }
}
```

**注意**: Facebook的API限制较多，可能不如其他平台有效

---

### ⚠️ TikTok（需要Cookie）

**需要配置** - TikTok需要认证

1. 登录TikTok网页版
2. 打开浏览器开发者工具 (F12)
3. 转到Application/Storage → Cookies
4. 复制 `sessionid` 和 `msToken`

配置格式：
```json
{
  "tiktok": {
    "sessionid": "your_sessionid",
    "msToken": "your_ms_token"
  }
}
```

---

### ✅ Medium（无需配置）

**无需配置** - 使用公开API和RSS

可直接使用。

---

### ✅ Indie Hackers（无需配置）

**无需配置** - 使用公开数据

可直接使用，但功能有限。

---

## 🚀 快速配置

### 推荐的最小配置

如果你想快速开始，建议配置这些：

1. **Reddit** - ✅ 可选（公开API即可）
2. **YouTube** - ⚠️ 需要（获取API key很简单）
3. **Medium** - ✅ 无需配置
4. **Indie Hackers** - ✅ 无需配置

其他平台（Instagram, Facebook, TikTok）的配置较复杂，可以等测试后再决定是否添加。

---

## 📋 配置文件示例

完整的 `platforms_auth.json` 示例：

```json
{
  "github": {
    "access_token": "ghp_..."
  },
  "producthunt": {
    "api_key": "...",
    "api_secret": "...",
    "redirect_uri": "..."
  },
  "reddit": {
    "client_id": "optional_client_id",
    "client_secret": "optional_client_secret",
    "user_agent": "MarketingMindAI/1.0"
  },
  "youtube": {
    "api_key": "AIzaSy..."
  },
  "instagram": {
    "sessionid": "optional_if_needed"
  },
  "facebook": {
    "access_token": "optional_if_needed"
  },
  "tiktok": {
    "sessionid": "optional_if_needed",
    "msToken": "optional_if_needed"
  }
}
```

---

## ✅ 当前已配置的平台

- [x] Twitter/X - 已配置
- [x] GitHub - 已配置
- [x] Hacker News - 无需配置
- [x] Product Hunt - 已配置
- [ ] LinkedIn - 账号受限
- [x] Reddit - 可用（无配置）
- [ ] YouTube - **需要你提供API key**
- [ ] Instagram - **需要你提供cookie**
- [ ] Facebook - **需要你提供token**
- [ ] TikTok - **需要你提供cookie**
- [x] Medium - 可用（无配置）
- [x] Indie Hackers - 可用（无配置）

---

## 📊 优先级建议

### 高优先级（推荐先配置）:
1. ✅ **Reddit** - 免费，无需配置
2. ⚠️ **YouTube** - 免费，简单配置
3. ✅ **Medium** - 免费，无需配置

### 中优先级（按需配置）:
4. ⚠️ **Instagram** - 需要cookie
5. ⚠️ **TikTok** - 需要cookie

### 低优先级（可选）:
6. ⚠️ **Facebook** - API限制多
7. ✅ **Indie Hackers** - 数据有限

---

## 🎯 下一步

1. 告诉我你想配置哪些平台
2. 我会帮你测试已经可用的平台（Reddit, Medium, Indie Hackers）
3. 对于需要配置的平台，按照上面的指南获取credentials
4. 更新 `platforms_auth.json` 文件
5. 运行测试验证所有平台

哪些平台你想先配置？我可以先测试那些不需要配置的。
