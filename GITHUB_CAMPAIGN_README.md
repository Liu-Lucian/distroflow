# GitHub开发者智能营销系统

## 🎯 系统概述

由于GitHub没有私信功能，本系统采用**邮箱营销**方式联系开发者：

1. **搜索开发者** - GitHub API搜索相关开发者
2. **AI分析价值** - 分析项目方向和技术栈，判断合作潜力
3. **查找邮箱** - 从profile/commits提取 + Hunter.io查找
4. **个性化邮件** - AI生成个性化邮件内容
5. **自动发送** - SMTP自动发送
6. **多轮循环** - 持续运行，自动休息

---

## 🚀 快速开始

### Step 1: 配置GitHub Token

```bash
# 编辑 platforms_auth.json
{
  "github": {
    "access_token": "your_github_token"
  }
}
```

**获取GitHub Token**：
1. 访问 https://github.com/settings/tokens
2. 点击"Generate new token (classic)"
3. 选择权限：`read:user`, `user:email`, `repo`
4. 复制token到配置文件

---

### Step 2: 配置邮件系统

```bash
# 编辑 email_config.json
{
  "smtp": {
    "server": "smtp.gmail.com",
    "port": 587,
    "username": "your@gmail.com",
    "password": "your_app_password"
  }
}
```

**Gmail App Password**：
1. 访问 https://myaccount.google.com/apppasswords
2. 生成应用专用密码
3. 复制到配置文件

---

### Step 3: 配置Hunter.io（可选但推荐）

```bash
# 设置环境变量
export HUNTER_API_KEY='your_hunter_api_key'
```

**获取Hunter.io API Key**：
1. 注册 https://hunter.io
2. 免费计划：25 searches/月
3. 付费计划：$49/月 (500 searches)

---

### Step 4: 配置搜索策略

编辑 `run_github_campaign.py`：

```python
# 🎯 搜索配置
SEARCH_STRATEGIES = [
    # 方法1：关键词搜索
    {
        'type': 'keywords',
        'query': ['recruiter', 'hiring', 'interview', 'career'],
        'limit': 30
    },
    # 方法2：Topic搜索
    {
        'type': 'topic',
        'query': 'interview',  # 你的产品相关topic
        'limit': 30
    },
    # 方法3：仓库Contributors
    {
        'type': 'repository',
        'query': 'jwasham/coding-interview-university',  # 相关仓库
        'limit': 20
    }
]

USERS_PER_ROUND = 100  # 每轮目标用户数
MIN_FOLLOWERS = 10  # 最小粉丝数
MIN_PUBLIC_REPOS = 5  # 最小公开仓库数

# 🔄 多轮循环配置
ENABLE_LOOP = True
ROUND_DELAY_HOURS = (12, 24)  # 12-24小时间隔
MAX_ROUNDS = 5  # 最多5轮

# 📧 邮件配置
EMAIL_BATCH_SIZE = 20  # 每轮发送20封
EMAIL_DELAY = (300, 600)  # 5-10分钟延迟
```

---

### Step 5: 运行

```bash
# 单轮模式（测试）
export OPENAI_API_KEY='your_key'
export HUNTER_API_KEY='your_hunter_key'
python3 run_github_campaign.py

# 多轮循环模式（生产）
# 设置 ENABLE_LOOP = True 后运行
python3 run_github_campaign.py
```

---

## 📊 运行示例

```
======================================================================
🐙 GitHub Smart Campaign - Email Edition
======================================================================

🔄 Multi-round loop mode ENABLED
   Target users per round: 100
   Rest between rounds: 12-24 hours
   Max rounds: 5

======================================================================

🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
🚀 ROUND 1 / 5
Started: 2025-10-19 14:30:00
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

📊 GitHub Developer Outreach Strategy:
   🔍 Search: GitHub API (free)
   🧠 AI Analysis: GPT-4o-mini (~$0.001/user)
   📧 Email Finding: Hunter.io (~$0.10/email)
   📬 Email Sending: SMTP (free)

🔍 Searching GitHub developers...

   Strategy: keywords | Query: ['recruiter', 'hiring', 'interview', 'career']
   ✅ Found 30 unique developers

   Strategy: topic | Query: interview
   ✅ Found 60 unique developers

   Strategy: repository | Query: jwasham/coding-interview-university
   ✅ Found 80 unique developers

📖 Fetching detailed profiles...
   [1/80] Fetching @john_doe...
      ✅ Added (followers: 234, repos: 45)
   [2/80] Fetching @jane_smith...
      ✅ Added (followers: 567, repos: 89)
   ...

   ✅ Got 65 qualified profiles

🧠 AI Analysis of developers...
   Analyzing 65 developers
   Estimated cost: ~$0.065
   ✅ AI identified 42 high-value developers

======================================================================
📊 Round Summary (Before Email Finding)
======================================================================
New qualified developers found: 42
Total qualified developers: 42

📧 Finding email addresses...
   [1/42] Finding email for @john_doe...
      ✅ Found from GitHub: john@example.com
   [2/42] Finding email for @jane_smith...
      ✅ Found with Hunter.io: jane@company.com
   ...

   ✅ Found emails for 35/42 users

Users with valid emails: 35
Ready for outreach: 35

📬 Starting email outreach...

📬 Sending emails to 20 developers...

[1/20] Sending to John Doe (john@example.com)...
   ✅ Sent
   ⏳ Waiting 450s...

[2/20] Sending to Jane Smith (jane@company.com)...
   ✅ Sent
   ⏳ Waiting 520s...

...

✅ Sent 20 emails

✅ Round completed!
💰 Estimated cost this round:
   AI Analysis: ~$0.042
   Email Finding: ~$3.50
   Email Sending: $0 (SMTP)

======================================================================
📊 Cumulative Statistics
======================================================================
Total rounds completed: 1
Total developers found: 42
Total emails sent: 20
Average users/round: 42.0
======================================================================

💤 Resting for 18.3 hours...
   Will resume at: 2025-10-20 08:48:00
   Press Ctrl+C to stop

...

🚀 ROUND 2 / 5
...
```

---

## 💡 工作原理

### 搜索策略（3种方式）：

#### 1. 关键词搜索
```python
{
    'type': 'keywords',
    'query': ['recruiter', 'hiring'],
    'limit': 30
}
```
- 搜索bio/README中包含关键词的用户
- 适合：找特定领域的开发者

#### 2. Topic搜索
```python
{
    'type': 'topic',
    'query': 'interview',
    'limit': 30
}
```
- 搜索特定topic的热门仓库
- 找这些仓库的contributors
- 适合：找活跃在某领域的开发者

#### 3. 仓库Contributors
```python
{
    'type': 'repository',
    'query': 'jwasham/coding-interview-university',
    'limit': 20
}
```
- 直接获取某个仓库的contributors
- 适合：找已知项目的贡献者

---

### AI分析标准：

系统会分析：
- **项目方向**：从public repos判断技术领域
- **活跃度**：followers、repos数量
- **相关性**：bio、location、company是否匹配
- **合作潜力**：intent_score > 0.7

---

### 邮箱查找策略：

```
1. GitHub Public Email
   ├─ 如果用户公开了邮箱 → 直接使用
   └─ 最准确，免费

2. GitHub Commits Email
   ├─ 从用户的commit history提取
   └─ 准确，免费

3. Hunter.io Email Finder
   ├─ 输入：domain + first name + last name
   ├─ 输出：verified email + confidence score
   └─ 付费，但准确率高（90%+）

4. 过滤无效域名
   ├─ 跳过：github.com, linkedin.com, twitter.com
   └─ 避免推断无效邮箱
```

---

### 邮件个性化：

```python
EMAIL_TEMPLATE = """Hi {{name}},

I came across your work on GitHub - really impressive projects, especially {{repo_mention}}.

I'm building HireMeAI, an AI-powered platform for interview prep.

{{personalization}}

Would love your thoughts!

Best,
[Your Name]
"""
```

**个性化变量**：
- `{{name}}` - 真实姓名（从GitHub profile）
- `{{repo_mention}}` - 提及用户的项目
- `{{personalization}}` - 根据bio/company生成

---

## 💰 成本分析

### 单轮成本（100个目标用户）：

| 项目 | 数量 | 单价 | 成本 |
|------|------|------|------|
| GitHub API | 100 calls | $0 | **$0** |
| AI分析 | 65 users | $0.001/user | **$0.07** |
| Hunter.io | 35 emails | $0.10/email | **$3.50** |
| Email发送 | 20 emails | $0 (SMTP) | **$0** |
| **总计** | - | - | **$3.57** |

### 5轮总成本：

- AI分析：~$0.35
- Hunter.io：~$17.50
- **总成本：~$18**

### Hunter.io定价：

- 免费计划：25 searches/月
- Starter：$49/月 (500 searches)
- Growth：$99/月 (1,000 searches)

**建议**：前期用免费计划测试，效果好再升级

---

## 📈 预期效果

基于100个开发者outreach：

### 漏斗分析：

```
100 搜索到的用户
 ↓ 过滤（followers < 10, repos < 5）
65 符合基础标准
 ↓ AI分析（intent_score > 0.7）
42 高价值开发者
 ↓ 邮箱查找（GitHub + Hunter.io）
35 找到有效邮箱
 ↓ 邮件发送（每轮20封）
20 收到邮件
 ↓ 响应率（5-10%）
1-2 回复
 ↓ 转化率（50%）
1 个付费用户
```

### ROI计算：

- 成本：$3.57/轮
- 转化：1个用户（假设LTV = $50）
- **ROI：14x**

---

## 🎯 优化建议

### 1. 提高邮箱发现率

**当前**：35/42 (83%)

**优化**：
- 使用多个邮箱查找工具（Clearbit, Voila Norbert）
- 爬取用户的个人网站（Playwright）
- 检查用户的social links

### 2. 提高邮件响应率

**当前**：5-10%

**优化**：
- 更个性化的subject line
- 提及用户的具体项目/commit
- 提供立即价值（免费试用、早期访问）
- A/B测试不同模板

### 3. 降低Hunter.io成本

**方法**：
- 优先使用GitHub public email
- 缓存已查找的邮箱
- 只对高分用户使用Hunter.io
- 使用更便宜的替代品（Apollo.io, Snov.io）

### 4. 扩大搜索范围

**增加搜索策略**：
```python
# 方法4：语言过滤
{
    'type': 'keywords',
    'query': ['interview', 'language:python'],
    'limit': 50
}

# 方法5：地理位置
{
    'type': 'keywords',
    'query': ['recruiter', 'location:san-francisco'],
    'limit': 50
}

# 方法6：公司搜索
{
    'type': 'keywords',
    'query': ['company:google', 'hiring'],
    'limit': 30
}
```

---

## 🔧 故障排查

### 问题1：GitHub API限速

**错误**：`API rate limit exceeded`

**解决**：
```python
# 检查rate limit
curl -H "Authorization: token YOUR_TOKEN" \
     https://api.github.com/rate_limit

# 增加延迟
time.sleep(1)  # 每次API调用后等待1秒
```

### 问题2：Hunter.io credits不足

**错误**：`Hunter.io API: No credits remaining`

**解决**：
- 升级Hunter.io计划
- 使用免费的GitHub email
- 减少`EMAIL_BATCH_SIZE`

### 问题3：邮件进垃圾箱

**原因**：
- 发送频率太高
- 邮件内容像垃圾邮件
- SPF/DKIM设置不正确

**解决**：
```python
# 增加延迟
EMAIL_DELAY = (600, 1200)  # 10-20分钟

# 配置SPF/DKIM
# 在Gmail中启用"Less secure app access"
# 或使用SendGrid/Mailgun

# 优化邮件内容
# - 避免过多链接
# - 使用纯文本而非HTML
# - 个性化每封邮件
```

### 问题4：邮箱验证失败

**错误**：`Invalid email address`

**解决**：
```python
# 启用邮箱验证
from email_verifier import EmailVerifier

verifier = EmailVerifier()
if verifier.verify(email):
    # 发送邮件
else:
    # 跳过无效邮箱
```

---

## 📚 相关文档

- `run_github_campaign.py` - 主程序
- `src/github_scraper.py` - GitHub爬虫
- `src/smart_email_finder.py` - 智能邮箱查找
- `src/email_campaign_manager.py` - 邮件发送
- `COMMANDS.md` - 所有平台命令
- `SMART_EMAIL_FINDER.md` - 邮箱查找策略

---

## 🎉 开始使用！

```bash
# 1. 配置GitHub Token
nano platforms_auth.json

# 2. 配置邮件
nano email_config.json

# 3. 配置Hunter.io (可选)
export HUNTER_API_KEY='your_key'

# 4. 运行
export OPENAI_API_KEY='your_key'
python3 run_github_campaign.py
```

**Good luck with your GitHub developer outreach!** 🚀

---

## 💡 Pro Tips

1. **先小规模测试**：`EMAIL_BATCH_SIZE = 3`, `MAX_ROUNDS = 1`
2. **监控响应率**：如果<3%，优化邮件内容
3. **避免被标记垃圾邮件**：每天最多50封
4. **使用专业邮箱**：避免Gmail免费账号
5. **A/B测试主题行**：测试不同的subject lines
6. **跟进策略**：7天后发送follow-up邮件

---

*Happy Developer Outreach!* 🐙✨
