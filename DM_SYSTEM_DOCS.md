# DM系统文档

## 系统概述

多平台私信自动化系统，使用Playwright浏览器自动化发送DM。

## 已实现平台

| 平台 | 状态 | 认证文件 | 测试结果 |
|------|------|----------|----------|
| Reddit | ✅ 可用 | `reddit_auth.json` | 发送成功 |
| Twitter/X | ✅ 可用 | `platforms_auth.json` (twitter) | 登录成功 |
| Instagram | ✅ 已修复 | `platforms_auth.json` (instagram.sessionid) | 正确流程：搜索→点帖子→点"消息"按钮（在帖子弹窗中） |
| TikTok | 🟡 未测试 | `platforms_auth.json` (tiktok.sessionid+msToken) | - |
| LinkedIn | ⏸️ 跳过 | `linkedin_auth.json` | 用户报告失败 |

## 核心文件

### DM发送器
- `src/dm_sender_base.py` - 基类（消息模板、人性化行为）
- `src/reddit_dm_sender.py` - Reddit实现（✅ 已测试）
- `src/twitter_dm_sender.py` - Twitter实现（✅ 已测试）
- `src/instagram_dm_sender.py` - Instagram实现
- `src/tiktok_dm_sender.py` - TikTok实现
- `src/linkedin_dm_sender.py` - LinkedIn实现

### 认证工具
- `reddit_save_cookies.py` - Reddit登录保存（手动按Enter）
- `twitter_save_cookies.py` - Twitter登录保存（手动按Enter）

### 测试脚本
- `test_reddit_send_now.py` - Reddit发送测试（✅ 成功）
- `test_twitter_auto.py` - Twitter发送测试（✅ 登录成功）
- `instagram_debug_auto.py` - Instagram调试脚本（自动扫描元素60秒）

## 消息模板

```
Hey {{name}}, I came across your posts about {{project}} — really insightful stuff.

I'm building HireMeAI (https://interviewasssistant.com), it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews.
```

变量：`{{name}}`, `{{company}}`, `{{project}}`, `{{product}}`, `{{username}}`

## 快速使用

### Reddit
```python
from src.reddit_dm_sender import RedditDMSender

sender = RedditDMSender()  # 自动加载reddit_auth.json
success = sender.send_dm(
    {'username': 'target_user', 'name': 'Name'},
    'Your message here'
)
sender.cleanup()
```

### Twitter
```python
from src.twitter_dm_sender import TwitterDMSender

sender = TwitterDMSender()  # 自动加载platforms_auth.json中的twitter
success = sender.send_dm(
    {'username': 'target_user', 'name': 'Name'},
    'Your message here'
)
sender.cleanup()
```

## 认证配置

### platforms_auth.json结构
```json
{
  "reddit": {
    "cookies": {...},
    "storage_state_file": "reddit_auth.json"
  },
  "twitter": {
    "cookies": [
      {"name": "auth_token", "value": "...", "domain": ".x.com", ...},
      {"name": "ct0", "value": "...", ...}
    ]
  },
  "instagram": {
    "sessionid": "..."
  },
  "tiktok": {
    "sessionid": "...",
    "msToken": "..."
  }
}
```

## 关键实现细节

### Reddit特殊处理
- 字段名：`message-recipient-input`, `message-title`, `message-content`
- 需填写所有3个字段才能启用发送按钮
- 使用`wait_for_element_state('enabled')`等待按钮可用

### Twitter特殊处理
- cookies格式：数组，包含`auth_token`, `ct0`, `twid`
- 检测`sendDMFromProfile`按钮判断用户是否开启DM
- 很多用户（尤其名人）关闭了DM功能

### 人性化行为（所有平台）
- `_random_delay(min, max)` - 随机延迟
- `_type_like_human(element, text)` - 逐字输入，每字符0.05-0.15秒

## Instagram关键修复

**问题**: 之前无法找到Message按钮
**根本原因**: 错误的流程和选择器

**修复方案**:
1. **正确流程**: 搜索关键词 → 访问用户profile → 滚动加载帖子 → 点击第一个帖子 → **在帖子弹窗中**找Message按钮
2. **关键选择器**:
   - 帖子: `a[href*="/p/"]`, `a[href*="/reel/"]` (不要用`article a`)
   - Message按钮: `div[role="button"]:has-text("消息")` (不是`button:has-text()`)
   - 备选: `a:has-text("消息")`
3. **重要细节**:
   - 需要滚动页面确保帖子加载: `page.evaluate("window.scrollTo(0, 500)")`
   - 使用JavaScript点击避免overlay: `page.evaluate('(element) => element.click()', element)`
   - 等待时间: 点击帖子后等待3-4秒让弹窗加载
   - 支持中英文UI: "消息" (Chinese) 和 "Message" (English)

**调试脚本**: `debug_instagram_profile.py` - 测试各种选择器，自动点击帖子，查找Message按钮

## 已知问题

1. **LinkedIn** - 用户报告失败，原因未知，暂时跳过
2. **Twitter DM限制** - 需要用户开启DM或已关注
3. **TikTok** - 未测试，有严格反自动化检测

## 测试过的场景

✅ Reddit: 成功发送DM给`u/Gari_305`
✅ Twitter: 成功登录，访问`@paulg`（DM未开启，符合预期）

## 每日限制建议

| 平台 | 建议上限 | 风险 |
|------|---------|------|
| Reddit | 10-15条/天 | 🟡 中 |
| Twitter | 15-20条/天 | 🟢 低 |
| Instagram | 5-10条/天 | 🔴 高 |
| TikTok | 3-5条/天 | 🔴 高 |
| LinkedIn | 20-30条/天 | 🟢 低 |

发送间隔：1-3分钟随机延迟

## 故障排查

### Reddit
- ❌ "Could not find message input box" → 运行`python3 reddit_save_cookies.py`重新登录
- ❌ "Send button not enabled" → 检查是否填写了subject和message

### Twitter
- ❌ "Not logged in" → cookies过期，运行`python3 twitter_save_cookies.py`
- ⚠️ "DMs may not be enabled" → 正常，选择其他用户

### 通用
- 浏览器关闭异常 → 调用`sender.cleanup()`
- Playwright超时 → 增加`timeout`参数或检查网络
