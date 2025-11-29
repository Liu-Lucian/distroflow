# Facebook营销系统 - 修复版使用指南

## ⚠️ 重要修复

Facebook的搜索页面会导致Playwright崩溃，所以改用**直接指定帖子URL**的方式，参照Instagram/TikTok模式。

---

## 🚀 快速开始（3步）

### Step 1: 登录Facebook保存Cookies

```bash
python3 facebook_login_and_save_auth.py
```

---

### Step 2: 测试评论抓取

```bash
python3 test_facebook_comments.py
```

会提示你输入一个Facebook帖子URL，然后测试是否能抓取评论。

**如何获取帖子URL**：
1. 在Facebook打开一个帖子
2. 点击右上角"..." → "Copy Link"
3. 粘贴到测试脚本

---

### Step 3: 运行完整Campaign

编辑 `run_facebook_campaign_simple.py`：

```python
# 添加你的帖子URLs
POST_URLS = [
    "https://www.facebook.com/groups/123456/posts/789/",
    "https://www.facebook.com/user/posts/123/",
]

# 配置产品描述和消息模板
PRODUCT_DESCRIPTION = """你的产品描述..."""
MESSAGE_TEMPLATE = """Hey {username}!..."""

# 配置参数
AI_MIN_SCORE = 0.6  # AI筛选最低分
DM_BATCH_SIZE = 3   # 每次发送数量
```

然后运行：

```bash
export OPENAI_API_KEY='your_key'
python3 run_facebook_campaign_simple.py
```

---

## 📂 文件说明

| 文件 | 用途 |
|------|------|
| `facebook_login_and_save_auth.py` | 登录Facebook并保存cookies |
| `test_facebook_comments.py` | 测试评论抓取（推荐先测试）|
| `run_facebook_campaign_simple.py` | 完整Campaign（简化版）|
| `src/facebook_scraper.py` | 核心抓取逻辑 |
| `src/facebook_dm_sender.py` | DM发送器 |

---

## 🔧 为什么改用简化版？

**问题**：
- Facebook搜索页面 (`/search/posts?q=`) 会导致Playwright崩溃
- 错误：`Page.goto: Page crashed` 或 `Target crashed`
- 这是Facebook的反爬虫机制

**解决方案**：
- ✅ 不搜索关键词
- ✅ 直接从指定的帖子URL抓评论
- ✅ 参照Instagram/TikTok的成功模式
- ✅ 更稳定可靠

---

## 💡 使用建议

### 1. 找到好的帖子

**推荐来源**：
- Facebook群组的热门帖子（最佳！）
- 相关页面的讨论帖子
- 行业KOL的帖子

**好的帖子特征**：
- 评论多（30+）
- 话题相关
- 最近发布（1-3天内）
- 提问型帖子

**例子**：
- ❌ "Check out my product!"（广告）
- ✅ "How do you prepare for interviews?"（讨论）

---

### 2. 测试流程

```bash
# 1. 先测试1个帖子
python3 test_facebook_comments.py
# 输入帖子URL，看能否抓到评论

# 2. 如果成功，添加到campaign
nano run_facebook_campaign_simple.py
# 添加POST_URLS

# 3. 运行campaign（只抓评论，先不发DM）
python3 run_facebook_campaign_simple.py
# 会在AI分析后暂停，让你review用户

# 4. 确认后按Enter开始发DM
```

---

### 3. 循序渐进

```python
# 第一次：测试（1个用户）
DM_BATCH_SIZE = 1

# 第二次：小规模（3个用户）
DM_BATCH_SIZE = 3

# 第三次：扩大（5-10个用户）
DM_BATCH_SIZE = 5
```

---

## 🐛 故障排除

### 问题1：找不到评论

**可能原因**：
- 帖子需要登录才能看
- Cookies过期
- 帖子URL错误

**解决**：
1. 重新登录：`python3 facebook_login_and_save_auth.py`
2. 确认在浏览器中能看到评论
3. 检查URL是否正确

---

### 问题2：AI返回0个用户

**解决**：
```python
# 降低门槛
AI_MIN_SCORE = 0.5  # 从0.6降到0.5

# 优化产品描述
PRODUCT_DESCRIPTION = """
清楚说明：
- 产品是什么
- 解决什么问题
- 谁需要这个产品
"""
```

---

### 问题3：DM发送失败

**解决**：
1. 检查能否手动发DM给该用户
2. 增加延迟：`DM_DELAY = (180, 360)`
3. 减少批量：`DM_BATCH_SIZE = 2`

---

## 📊 查看结果

```bash
# 原始评论
cat facebook_raw_comments.json | python3 -m json.tool

# AI筛选后的用户
cat facebook_qualified_users.json | python3 -m json.tool

# 统计
python3 -c "
import json
users = json.load(open('facebook_qualified_users.json'))
total = len(users)
sent = len([u for u in users if u.get('sent_dm')])
print(f'总用户: {total}')
print(f'已发送: {sent}')
print(f'待发送: {total - sent}')
"
```

---

## ✅ 测试清单

在实际使用前，请完成：

- [ ] 运行 `python3 facebook_login_and_save_auth.py` 保存cookies
- [ ] 找到1-3个相关的Facebook帖子URL
- [ ] 运行 `python3 test_facebook_comments.py` 测试抓取
- [ ] 确认能抓到至少10条评论
- [ ] 编辑 `run_facebook_campaign_simple.py` 配置参数
- [ ] 设置 `OPENAI_API_KEY` 环境变量
- [ ] 先用 `DM_BATCH_SIZE = 1` 测试发送1条DM
- [ ] 确认DM发送成功后再扩大批量

---

## 💰 成本估算

**完全免费！（几乎）**

- 抓取评论：$0
- AI分析：~$0.001 per 50用户
- 发送DM：$0

**示例**：
- 100个用户 ≈ $0.002
- 1000个用户 ≈ $0.02

---

## 🎯 完整示例

### 场景：推广Interview Prep工具

**1. 找帖子**：
- 加入"Job Search"相关群组
- 找到提问帖："How do you prepare for interviews?"
- 复制链接

**2. 测试**：
```bash
python3 test_facebook_comments.py
# 输入帖子URL
# 确认能抓到评论
```

**3. 配置**：
```python
POST_URLS = [
    "https://www.facebook.com/groups/jobsearch/posts/123456/",
]

PRODUCT_DESCRIPTION = """
HireMeAI - AI面试准备工具
帮助求职者通过AI模拟面试提升面试技能
"""
```

**4. 运行**：
```bash
export OPENAI_API_KEY='sk-...'
python3 run_facebook_campaign_simple.py
```

**5. 结果**：
- 抓到45条评论
- AI筛选出12个潜在客户
- 发送3个DM
- 2个人回复了！

---

## 📚 相关文档

- `FACEBOOK_QUICKSTART.md` - 快速指南
- `FACEBOOK_COMPLETE_GUIDE.md` - 完整文档
- `一键启动说明.md` - 多平台营销

---

*MarketingMind AI - 让Facebook营销变得简单可靠*
