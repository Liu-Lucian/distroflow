# 🚀 Quick Start - 5分钟开始你的第一个营销活动

## 完整系统已实现！

✅ 自动发送介绍邮件（20% off）
✅ 24小时自动跟进（30% off）
✅ 转化追踪
✅ 测试模式（所有邮件发到 liu.lucian6@gmail.com）

---

## 快速配置（3步骤）

### 步骤1: 获取Gmail应用密码（2分钟）

1. **开启两步验证**
   - 访问: https://myaccount.google.com/security
   - 找到"两步验证"并开启

2. **生成应用密码**
   - 访问: https://myaccount.google.com/apppasswords
   - 应用: "邮件"
   - 设备: "其他" → 输入 `MarketingMind AI`
   - 点击"生成"
   - **复制16位密码**（格式：`xxxx xxxx xxxx xxxx`）

---

### 步骤2: 创建配置文件（2分钟）

```bash
# 复制示例
cp email_config.example.json email_config.json
```

**最小配置（只改这4行）：**

```json
{
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "your-email@gmail.com",        # ← 改成你的Gmail
    "password": "xxxx xxxx xxxx xxxx",         # ← 改成刚才的16位密码
    "from_name": "Your Name",                  # ← 改成你的名字
    "from_email": "your-email@gmail.com"       # ← 改成你的Gmail
  },

  "campaign": {
    "product_name": "Your Product",            # ← 改成你的产品名
    "product_url": "https://your-site.com",
    "company_name": "Your Company",
    "support_email": "support@your-company.com"
  },

  "test_mode": {
    "enabled": true,
    "test_email": "liu.lucian6@gmail.com",     # ← 测试邮箱
    "send_to_test_only": true                  # ← 测试模式开启
  }

  # ... 其他保持默认即可
}
```

---

### 步骤3: 测试运行（1分钟）

```bash
# 找10个leads并发送测试邮件
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1

# 流程：
# 1. 从Twitter抓取10个followers
# 2. 验证邮箱
# 3. 发送到 liu.lucian6@gmail.com（你会收到每封邮件）
```

**你会收到：**
```
To: liu.lucian6@gmail.com
Subject: Exclusive 20% Off Your Product for @username

（精美HTML邮件，包含优惠码 WELCOME20）
```

---

## 测试邮件效果

### 检查清单

打开 liu.lucian6@gmail.com 查看邮件：

✅ 邮件外观是否美观
✅ 产品名、公司名是否正确
✅ 优惠码 WELCOME20 是否显示
✅ "Get Started" 按钮链接是否正确
✅ 取消订阅链接是否存在

---

## 下一步

### 1. 查看数据库

```bash
# 安装SQLite浏览器
brew install --cask db-browser-for-sqlite  # macOS

# 打开数据库
open campaign_tracking.db
```

**查看内容：**
- `campaigns` 表 - 所有发送记录
- `email_log` 表 - 发送日志

### 2. 测试跟进功能

```bash
# 方式1: 手动修改数据库中的sent_at时间为25小时前
# 然后运行：
python src/email_campaign_manager.py --check-followups

# 你会收到跟进邮件（30% off, LASTCHANCE30）
```

### 3. 查看统计

```bash
python src/email_campaign_manager.py --stats

# 输出：
# 📊 Campaign Statistics:
#    Total campaigns: 10
#    Sent: 10
#    Converted: 0
#    Pending follow-up: 10
#    Conversion rate: 0.0%
```

---

## 生产环境部署

### 切换到真实发送

1. **编辑 email_config.json**

```json
"test_mode": {
  "enabled": false,        # ← 关闭测试模式
  "test_email": "liu.lucian6@gmail.com",
  "send_to_test_only": false
}
```

2. **运行真实营销活动**

```bash
# 找100个leads并发送真实邮件
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 100 5

# 确认发送
# Send emails to 75 leads? (y/n): y
```

3. **设置自动跟进**

```bash
# 编辑crontab
crontab -e

# 添加（每6小时检查一次）
0 */6 * * * cd /Users/l.u.c/my-app/MarketingMind\ AI && python3 src/email_campaign_manager.py --check-followups >> email_campaign.log 2>&1
```

---

## 系统架构

```
┌─────────────────────┐
│ Twitter Scraper     │
│ (Ultimate Finder)   │
└──────────┬──────────┘
           │ Leads with emails
           ↓
┌─────────────────────┐
│ Email Verifier      │
│ (DNS + SMTP)        │
└──────────┬──────────┘
           │ Valid emails
           ↓
┌─────────────────────┐
│ Campaign Manager    │
│ - Send initial      │
│ - Track conversion  │
│ - Auto follow-up    │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│ SQLite Database     │
│ campaign_tracking.db│
└─────────────────────┘
```

---

## 邮件流程

### 初始邮件（Day 0）

```
主题: Exclusive 20% Off Your Product for @username

Hi John!

I noticed you're following @ycombinator on Twitter...

🎁 EXCLUSIVE OFFER
Use code WELCOME20 for 20% off!
⏰ Expires in 7 days

[Get Started Now →]
```

### 跟进邮件（Day 1, if not converted）

```
主题: Don't miss out: 30% off Your Product (Last Chance)

Hi John,

I noticed you haven't taken advantage yet...

🎁 BETTER OFFER
Was: 20% off
NOW: 30% OFF!

Use code: LASTCHANCE30
⏰ Expires in 3 days!

[Claim Your 30% Discount Now →]
```

---

## 关键功能

### 1. 测试模式

**作用：** 所有邮件发到你的测试邮箱

```json
"test_mode": {
  "enabled": true,
  "test_email": "liu.lucian6@gmail.com",
  "send_to_test_only": true
}
```

**好处：**
- 先看邮件效果
- 测试链接和优惠码
- 确认格式无误
- 避免发错

### 2. 转化追踪

**URL追踪：**
```
https://your-product.com?promo=WELCOME20&email=user@example.com
```

**手动标记：**
```bash
python -c "
from src.email_campaign_manager import EmailCampaignManager
manager = EmailCampaignManager()
manager.mark_conversion('WELCOME20', 'customer@example.com')
"
```

### 3. 自动跟进

**逻辑：**
1. 每6小时检查数据库
2. 找到24小时前发送、未转化的leads
3. 发送跟进邮件（更大优惠）
4. 最多跟进2次

**设置：**
```bash
# 手动触发
python src/email_campaign_manager.py --check-followups

# 或设置cron自动触发
0 */6 * * * python3 src/email_campaign_manager.py --check-followups
```

---

## 常见问题

### Q: 测试邮件发不出去？

**A:** 检查：
1. Gmail两步验证是否开启
2. 应用密码是否正确（16位，带或不带空格都行）
3. `email_config.json` 中username和password是否正确

### Q: 如何修改邮件模板？

**A:** 编辑 `src/email_campaign_manager.py`，找到：
- `create_initial_email()` - 初始邮件模板
- `create_followup_email()` - 跟进邮件模板

修改 `html_content` 变量即可。

### Q: 如何添加更多优惠码？

**A:** 编辑 `email_config.json`:

```json
"promo_codes": {
  "initial": {
    "code": "WELCOME20",
    "discount": "20%",
    "valid_days": 7
  },
  "followup": {
    "code": "LASTCHANCE30",
    "discount": "30%",
    "valid_days": 3
  }
}
```

### Q: 一天能发多少邮件？

**A:**
- Gmail个人版: 500封/天
- Google Workspace: 2000封/天
- 专业SMTP（SendGrid等）: 无限制

---

## 完整命令参考

```bash
# ===== 配置 =====
cp email_config.example.json email_config.json
# 编辑 email_config.json

# ===== 测试 =====
# 10个leads，测试模式
python src/ultimate_email_finder_with_campaign.py product.md 10 1

# ===== 生产 =====
# 100个leads，真实发送
python src/ultimate_email_finder_with_campaign.py product.md 100 5

# ===== 跟进 =====
# 检查并发送跟进邮件
python src/email_campaign_manager.py --check-followups

# ===== 统计 =====
# 查看营销统计
python src/email_campaign_manager.py --stats

# ===== 转化 =====
# 标记转化
python -c "from src.email_campaign_manager import EmailCampaignManager; EmailCampaignManager().mark_conversion('WELCOME20', 'user@example.com')"

# ===== 数据库 =====
# 查看数据库
sqlite3 campaign_tracking.db "SELECT * FROM campaigns LIMIT 5"
open campaign_tracking.db  # macOS GUI查看
```

---

## 预期效果

### 小规模测试（10-20 leads）

```
输入: 10 followers from 1 seed account
↓
邮箱验证: 6-8 valid emails (60-80%)
↓
发送邮件: 6-8 emails sent
↓
测试邮箱: 收到6-8封邮件
↓
24小时后跟进: 自动发送跟进邮件
```

### 生产规模（100+ leads）

```
输入: 100 followers from 5 seed accounts
↓
邮箱验证: 70-80 valid emails (70-80%)
↓
发送邮件: 70-80 emails sent
↓
转化率: 10-20% (7-16 conversions)
↓
ROI: 根据产品价格计算
```

---

## 支持的邮件服务

### Gmail（已配置）

```json
"smtp": {
  "host": "smtp.gmail.com",
  "port": 587
}
```

### SendGrid（推荐生产）

```json
"smtp": {
  "host": "smtp.sendgrid.net",
  "port": 587,
  "username": "apikey",
  "password": "YOUR_SENDGRID_API_KEY"
}
```

### Amazon SES

```json
"smtp": {
  "host": "email-smtp.us-east-1.amazonaws.com",
  "port": 587,
  "username": "YOUR_AWS_SMTP_USERNAME",
  "password": "YOUR_AWS_SMTP_PASSWORD"
}
```

---

## 总结

### 已实现功能

✅ Twitter leads抓取
✅ 邮箱验证（DNS + SMTP）
✅ 自动发送介绍邮件
✅ 优惠码系统（20% → 30%）
✅ 转化追踪（SQLite数据库）
✅ 24小时自动跟进
✅ 测试模式（发到 liu.lucian6@gmail.com）
✅ 精美HTML邮件模板
✅ 统计报表

### 立即开始

```bash
# 1. 配置
cp email_config.example.json email_config.json
# 编辑email_config.json（改4行配置）

# 2. 测试
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1

# 3. 检查邮箱
# 打开 liu.lucian6@gmail.com 查看效果

# 4. 生产部署
# 修改test_mode.enabled = false
# 运行真实营销活动
```

---

**🎉 开始你的第一个自动化营销活动！**

测试邮件将发送到: **liu.lucian6@gmail.com**
