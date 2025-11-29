# 🚀 Facebook完整营销系统 - 使用指南

## 系统概述

**完整流程**：搜索关键词 → 找帖子 → 抓用户 → AI分析 → 发私信

参照Reddit/Twitter模式，简单清晰，功能强大！

---

## 🎯 核心功能

### 1. 搜索关键词 → 找帖子
- 输入关键词（如"job interview tips"）
- 自动在Facebook搜索相关帖子
- 找到热门讨论

### 2. 找帖子 → 抓用户
- 从帖子中抓取所有评论
- 提取用户信息（username, profile_url, comment）
- 自动去重

### 3. AI分析用户
- 使用GPT-4o-mini批量分析评论
- 识别潜在客户（intent score）
- 成本：~$0.001 per 50用户

### 4. 批量发私信
- 自动访问用户主页
- 点击Message按钮
- 发送个性化消息
- 人工延迟防检测

---

## 📝 快速开始

### Step 1: 登录Facebook并保存Cookies

```bash
python3 facebook_login_and_save_auth.py
```

**会发生什么**：
1. 浏览器自动打开Facebook
2. 你手动登录你的账号
3. 脚本自动保存cookies到 `platforms_auth.json`
4. 完成！

---

### Step 2: 配置Campaign参数

编辑 `run_facebook_campaign.py`：

```python
# 搜索关键词（修改这里）
KEYWORDS = [
    "job interview tips",
    "interview preparation",
    "career advice",
]

# 产品描述（修改这里）
PRODUCT_DESCRIPTION = """
你的产品介绍...
"""

# 消息模板（修改这里）
MESSAGE_TEMPLATE = """Hey {username}!
你的个性化消息...
"""

# 配置参数
TARGET_USERS = 50      # 目标用户数
AI_MIN_SCORE = 0.6     # AI筛选最低分
DM_BATCH_SIZE = 3      # 每次发送数量
DM_DELAY = (120, 300)  # 延迟范围（秒）
```

---

### Step 3: 运行Campaign

```bash
# 设置OpenAI API Key
export OPENAI_API_KEY='your_key'

# 运行
python3 run_facebook_campaign.py
```

**系统会自动**：
1. 搜索关键词找帖子
2. 从帖子抓取评论用户
3. AI分析用户意图
4. 显示待发送用户列表
5. 按Enter后批量发送DM
6. 保存进度到 `facebook_qualified_users.json`

---

## 📊 查看结果

```bash
# 查看所有用户
cat facebook_qualified_users.json | python3 -m json.tool

# 查看统计
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

## 🔧 系统架构

### 三个核心模块

#### 1. FacebookScraper (`src/facebook_scraper.py`)

**三个核心功能**：

```python
scraper = FacebookScraper()

# 功能1: 搜索帖子
posts = scraper.search_posts("job interview", max_posts=10)

# 功能2: 抓取评论
comments = scraper.get_post_comments(post_url, max_comments=50)

# 功能3: 完整流程（搜索→帖子→用户）
users = scraper.search_users(keywords=["career", "interview"], limit=50)
```

#### 2. FacebookDMSender (`src/facebook_dm_sender.py`)

**参照Reddit/Twitter模式**：

```python
sender = FacebookDMSender()

user = {
    'username': 'John Doe',
    'profile_url': 'https://www.facebook.com/johndoe'
}

message = "Hi John! ..."
success = sender.send_dm(user, message)
```

#### 3. Campaign Script (`run_facebook_campaign.py`)

**完整pipeline**：

```
搜索关键词
    ↓
找到帖子（5个）
    ↓
抓取评论（每个帖子30条）
    ↓
AI分析用户意图
    ↓
过滤高分用户（score >= 0.6）
    ↓
批量发送DM（3个/次，2-5分钟延迟）
    ↓
保存进度
```

---

## 💡 使用技巧

### 1. 选择精准关键词

**好的关键词**：
- ✅ "job interview preparation"
- ✅ "career change advice"
- ✅ "hiring process tips"

**不好的关键词**：
- ❌ "jobs" （太宽泛）
- ❌ "facebook" （无关）
- ❌ "memes" （不相关）

---

### 2. 调整AI筛选标准

如果AI返回0个用户：

```python
# 降低分数门槛
AI_MIN_SCORE = 0.5  # 从0.6降到0.5

# 优化产品描述
PRODUCT_DESCRIPTION = """
清楚说明：
1. 产品是什么
2. 解决什么问题
3. 谁需要这个产品
"""
```

---

### 3. 循序渐进

```bash
# 第一次：测试（1个用户）
DM_BATCH_SIZE = 1
python3 run_facebook_campaign.py

# 第二次：小规模（3个用户）
DM_BATCH_SIZE = 3
python3 run_facebook_campaign.py

# 第三次：扩大（5-10个用户）
DM_BATCH_SIZE = 5
python3 run_facebook_campaign.py
```

---

### 4. 个性化消息

使用AI分析结果个性化：

```python
MESSAGE_TEMPLATE = """Hey {username}!

I saw your comment about {topic} - {ai_reason}

Based on your interest in {interest_area}, I think you might find HireMeAI useful!

Would love to connect!"""
```

可用变量：
- `{username}` - 用户名
- `{topic}` - AI识别的话题
- `{interest_area}` - 用户兴趣领域
- `{ai_reason}` - AI分析理由

---

## 🎯 完整示例

### 场景：推广Interview Prep工具

**Step 1: 设置关键词**
```python
KEYWORDS = [
    "job interview tips",
    "interview preparation",
    "career advice",
    "job search strategies"
]
```

**Step 2: 运行Campaign**
```bash
export OPENAI_API_KEY='your_key'
python3 run_facebook_campaign.py
```

**Step 3: 系统自动执行**
```
🔍 Searching: "job interview tips"
   Found 5 posts

📖 Post 1: https://facebook.com/...
   Found 28 comments

📖 Post 2: https://facebook.com/...
   Found 31 comments

🧠 AI Analysis: 59 users
   ✅ 23 qualified (score >= 0.6)

💬 Sending DMs to 3 users...
   [1/3] John Smith ✅ Sent
   [2/3] Jane Doe ✅ Sent
   [3/3] Bob Wilson ✅ Sent

✅ Campaign completed!
   Total: 23 users
   Sent: 3
   Pending: 20
```

---

## 🔧 故障排除

### 问题1: 找不到帖子

**原因**：
- 关键词太特殊
- Facebook搜索限制
- Cookie过期

**解决**：
1. 更换关键词
2. 重新登录：`python3 facebook_login_and_save_auth.py`
3. 尝试更通用的关键词

---

### 问题2: 找不到Message按钮

**原因**：
- 用户设置了隐私限制
- 选择器变化
- 不是朋友无法发消息

**解决**：
脚本会自动尝试备用方案：
1. 寻找多种Message按钮选择器
2. 尝试直接访问 `/messages/t/{user_id}`
3. 如果失败，跳过该用户

---

### 问题3: DM发送失败

**可能原因**：
- Cookie过期
- 发送太快被检测
- 用户屏蔽陌生人消息

**解决**：
```python
# 增加延迟
DM_DELAY = (180, 360)  # 3-6分钟

# 减少批量
DM_BATCH_SIZE = 2  # 每次只发2个

# 重新登录
python3 facebook_login_and_save_auth.py
```

---

### 问题4: AI返回0个合格用户

**原因**：
- AI_MIN_SCORE太高
- 产品描述不清晰
- 关键词不相关

**解决**：
```python
# 1. 降低门槛
AI_MIN_SCORE = 0.5  # 或更低

# 2. 优化产品描述
PRODUCT_DESCRIPTION = """
HireMeAI - AI面试准备工具

目标用户：
- 正在找工作的人
- 需要面试辅导的人
- 想提升面试技能的人

我们帮助他们通过AI模拟面试获得即时反馈。
"""

# 3. 更换关键词
KEYWORDS = ["interview tips", "job hunting"]
```

---

## 📈 最佳实践

### 1. 分散时间运行

**推荐频率**：
- 每天 1-2 次
- 间隔至少 4 小时
- 避免在短时间内大量操作

### 2. 追踪效果

手动更新JSON，添加反馈：

```json
{
  "username": "John",
  "sent_dm": true,
  "replied": true,        // 新增
  "interested": true,     // 新增
  "converted": false,     // 新增
  "notes": "Asked for more info"
}
```

### 3. A/B测试消息

测试不同消息模板：

**版本A（直接）**：
```
Hi! I'm building an interview prep tool. Interested?
```

**版本B（友好）**：
```
Hey! Saw your comment about interviews. I built something that might help. Mind if I share?
```

记录哪个版本回复率更高！

---

## 💰 成本估算

**完全免费！（几乎）**

- 搜索帖子：$0
- 抓取评论：$0
- AI分析：~$0.001 per 50用户
- 发送DM：$0

**示例**：
- 100个用户 ≈ $0.002
- 1000个用户 ≈ $0.02

基本上可以忽略不计！

---

## 🎉 现在开始！

```bash
# 1. 登录Facebook
python3 facebook_login_and_save_auth.py

# 2. 配置参数
nano run_facebook_campaign.py  # 修改KEYWORDS和产品描述

# 3. 运行Campaign
export OPENAI_API_KEY='your_key'
python3 run_facebook_campaign.py

# 4. 查看结果
cat facebook_qualified_users.json | python3 -m json.tool
```

Good luck! 🚀

---

## 📚 相关文档

- `FACEBOOK_QUICKSTART.md` - 简化版快速指南
- `一键启动说明.md` - 多平台营销指南
- `README_MARKETING_SYSTEM.md` - 系统概览

---

*MarketingMind AI - 让Facebook营销变得简单*
