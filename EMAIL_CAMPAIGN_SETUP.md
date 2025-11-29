# 📧 Email Campaign System - 配置指南

## 系统概述

我已经实现了完整的自动化邮件营销系统！

### 功能特点

✅ **自动发送介绍邮件** - 找到leads后自动发送产品介绍
✅ **优惠码系统** - 初始20% off，跟进30% off
✅ **转化追踪** - SQLite数据库记录所有活动
✅ **自动跟进** - 24小时未转化自动发送更大优惠
✅ **测试模式** - 所有邮件先发到你的测试邮箱
✅ **精美HTML模板** - 专业的邮件设计

---

## 快速开始（5分钟配置）

### 步骤1: 配置Gmail SMTP

#### 1.1 开启Gmail的两步验证

1. 访问 https://myaccount.google.com/security
2. 找到"两步验证"并开启

#### 1.2 生成应用专用密码

1. 访问 https://myaccount.google.com/apppasswords
2. 选择"应用" → "邮件"
3. 选择"设备" → "其他（自定义名称）"
4. 输入名称：`MarketingMind AI`
5. 点击"生成"
6. **复制生成的16位密码**（格式：`xxxx xxxx xxxx xxxx`）

---

### 步骤2: 创建配置文件

```bash
# 复制示例配置
cp email_config.example.json email_config.json
```

编辑 `email_config.json`:

```json
{
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "your-email@gmail.com",        # 你的Gmail地址
    "password": "your-16-digit-app-password",  # 刚才生成的密码
    "from_name": "Your Name",                  # 发件人名字
    "from_email": "your-email@gmail.com"       # 你的Gmail地址
  },

  "campaign": {
    "product_name": "TaskFlow AI",             # 你的产品名
    "product_url": "https://your-product.com", # 产品网址
    "company_name": "Your Company",            # 公司名
    "support_email": "support@your-company.com"
  },

  "promo_codes": {
    "initial": {
      "code": "WELCOME20",   # 初始优惠码
      "discount": "20%",     # 优惠力度
      "valid_days": 7        # 有效天数
    },
    "followup": {
      "code": "LASTCHANCE30", # 跟进优惠码
      "discount": "30%",      # 更大优惠
      "valid_days": 3
    }
  },

  "timing": {
    "initial_delay_minutes": 5,   # 发送延迟
    "followup_delay_hours": 24,   # 跟进延迟（24小时）
    "max_followups": 2            # 最多跟进次数
  },

  "test_mode": {
    "enabled": true,                    # 开启测试模式
    "test_email": "liu.lucian6@gmail.com",  # 测试邮箱（你的）
    "send_to_test_only": true           # 所有邮件只发到测试邮箱
  }
}
```

---

### 步骤3: 测试发送

```bash
# 运行完整流程（测试模式）
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1

# 流程：
# 1. 抓取10个followers
# 2. 验证邮箱
# 3. 发送到 liu.lucian6@gmail.com（测试邮箱）
```

**测试邮件示例：**
```
To: liu.lucian6@gmail.com
Subject: Exclusive 20% Off TaskFlow AI for @username

（你会收到精美的HTML邮件，包含优惠码）
```

---

## 完整工作流程

### 流程图

```
Twitter抓取
    ↓
邮箱验证（过滤无效邮箱）
    ↓
发送初始邮件（20% off，优惠码：WELCOME20）
    ↓
记录到数据库（campaign_tracking.db）
    ↓
等待24小时
    ↓
检查转化状态
    ↓
未转化？ → 发送跟进邮件（30% off，优惠码：LASTCHANCE30）
    ↓
再等24小时
    ↓
第二次跟进（可选）
```

---

## 使用方法

### 方法1: 测试模式（推荐首次使用）

```bash
# 配置文件中设置：
# "test_mode": {
#   "enabled": true,
#   "test_email": "liu.lucian6@gmail.com",
#   "send_to_test_only": true
# }

# 运行
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 20 2

# 效果：
# - 找到20个leads
# - 所有邮件都发到 liu.lucian6@gmail.com
# - 可以查看邮件效果
```

### 方法2: 生产模式（真实发送）

```bash
# 1. 修改配置文件
# "test_mode": {
#   "enabled": false,  # 关闭测试模式
# }

# 2. 运行
python src/ultimate_email_finder_with_campaign.py product.md 100 5

# 3. 确认发送
# Send emails to 75 leads? (y/n): y

# 效果：
# - 找到75个有效邮箱的leads
# - 发送75封介绍邮件
# - 24小时后自动跟进
```

---

## 自动跟进设置

### 方法1: 手动触发（测试用）

```bash
# 24小时后手动运行
python src/email_campaign_manager.py --check-followups

# 系统会：
# 1. 查找24小时前发送、未转化的leads
# 2. 发送跟进邮件（30% off）
# 3. 更新数据库
```

### 方法2: Cron自动化（生产用）

#### macOS/Linux:

```bash
# 1. 编辑crontab
crontab -e

# 2. 添加定时任务（每6小时检查一次）
0 */6 * * * cd /Users/l.u.c/my-app/MarketingMind\ AI && /usr/bin/python3 src/email_campaign_manager.py --check-followups >> email_campaign.log 2>&1

# 3. 保存并退出
```

#### 解释：
- `0 */6 * * *` - 每天00:00, 06:00, 12:00, 18:00运行
- `cd /path/to/project` - 切换到项目目录
- `python3 src/...` - 运行跟进检查
- `>> email_campaign.log` - 记录日志

---

## 转化追踪

### 手动标记转化

```python
from src.email_campaign_manager import EmailCampaignManager

manager = EmailCampaignManager()

# 方式1: 通过邮箱和优惠码
manager.mark_conversion('WELCOME20', 'customer@example.com')

# 方式2: 只通过优惠码
manager.mark_conversion('LASTCHANCE30')
```

### 查看统计

```bash
python src/email_campaign_manager.py --stats

# 输出：
# 📊 Campaign Statistics:
#    Total campaigns: 75
#    Sent: 75
#    Converted: 12
#    Pending follow-up: 45
#    Conversion rate: 16.0%
```

### 数据库查看

```bash
# 安装SQLite浏览器
brew install --cask db-browser-for-sqlite  # macOS

# 打开数据库
open campaign_tracking.db  # 或用DB Browser打开
```

**数据库表：**

1. **campaigns** - 所有营销活动
   - email, name, username
   - promo_code, status
   - sent_at, converted_at
   - followup_count

2. **email_log** - 邮件发送日志
   - campaign_id
   - email_type (initial/followup_1/followup_2)
   - sent_at, success

3. **promo_usage** - 优惠码使用记录
   - campaign_id
   - promo_code
   - used_at

---

## 邮件模板预览

### 初始邮件（20% off）

**主题：** Exclusive 20% Off TaskFlow AI for @username

**内容：**
```
━━━━━━━━━━━━━━━━━━━━━━
  TaskFlow AI
  Exclusive Offer for @username
━━━━━━━━━━━━━━━━━━━━━━

Hi John!

I noticed you're following @ycombinator on Twitter,
and I thought TaskFlow AI would be perfect for you!

Why TaskFlow AI?
✓ Boost productivity with AI-powered task management
✓ Automate workflow bottlenecks
✓ Predict and prevent project delays

🎁 EXCLUSIVE OFFER FOR YOU
Use code WELCOME20
Get 20% off your first month!
⏰ Expires in 7 days

[Get Started Now →]

Have questions? Just reply to this email!
```

### 跟进邮件（30% off）

**主题：** Don't miss out: 30% off TaskFlow AI (Last Chance)

**内容：**
```
━━━━━━━━━━━━━━━━━━━━━━
  ⚡ UPGRADED OFFER ⚡
  Don't Miss Your Last Chance
━━━━━━━━━━━━━━━━━━━━━━

Hi John,

I noticed you haven't taken advantage of your
exclusive offer yet, so I've UPGRADED it for you!

🎁 BETTER OFFER - JUST FOR YOU
Was: 20% off
NOW: 30% OFF!

Use code: LASTCHANCE30

⏰ This offer expires in just 3 days!

[Claim Your 30% Discount Now →]

P.S. This is our BEST offer and the last time
we'll be able to offer this discount. Don't miss out!
```

---

## 常见问题

### Q1: 如何测试邮件效果？

**A**: 开启测试模式：

```json
"test_mode": {
  "enabled": true,
  "test_email": "liu.lucian6@gmail.com",
  "send_to_test_only": true
}
```

所有邮件都会发到你的测试邮箱，你可以：
- 查看邮件外观
- 测试链接
- 检查优惠码

### Q2: Gmail显示"发送失败"？

**A**: 常见原因：

1. **未开启两步验证** → 开启并生成应用密码
2. **密码错误** → 确认16位应用密码（带空格或不带空格都行）
3. **安全设置** → 访问 https://myaccount.google.com/lesssecureapps (可能需要)

### Q3: 如何修改邮件模板？

**A**: 编辑 `src/email_campaign_manager.py`:

```python
# 找到 create_initial_email() 函数
# 修改 html_content 变量

html_content = f"""
<!DOCTYPE html>
<html>
...
你的自定义HTML
...
</html>
"""
```

### Q4: 如何追踪转化？

**A**: 三种方法：

1. **URL参数追踪**
   - 邮件中的链接包含 `?promo=WELCOME20&email=user@example.com`
   - 在你的网站记录这些参数

2. **优惠码使用**
   - 用户使用优惠码时，调用API标记转化

3. **手动标记**
   ```bash
   python -c "
   from src.email_campaign_manager import EmailCampaignManager
   manager = EmailCampaignManager()
   manager.mark_conversion('WELCOME20', 'customer@example.com')
   "
   ```

### Q5: 每天能发多少邮件？

**A**: Gmail限制：

- **个人Gmail**: 500封/天
- **Google Workspace**: 2000封/天

**建议：**
- 小规模测试: 50-100封/天
- 生产使用: 考虑专业SMTP服务（SendGrid, Mailgun）

### Q6: 如何避免进垃圾箱？

**A**: 最佳实践：

✅ **使用测试模式确认邮件质量**
✅ **添加取消订阅链接**（已包含在模板中）
✅ **不要发送垃圾内容**
✅ **控制发送速度**（系统已设置2秒延迟）
✅ **使用真实的from地址**
✅ **避免spam关键词**（FREE, CLICK NOW等）

### Q7: 如何切换到SendGrid？

**A**: 修改配置：

```json
"smtp": {
  "host": "smtp.sendgrid.net",
  "port": 587,
  "username": "apikey",
  "password": "YOUR_SENDGRID_API_KEY",
  "from_name": "Your Name",
  "from_email": "verified@your-domain.com"
}
```

---

## 高级配置

### 自定义跟进时间

```json
"timing": {
  "initial_delay_minutes": 5,
  "followup_delay_hours": 24,  # 改为48小时后跟进
  "max_followups": 3           # 最多跟进3次
}
```

### 多阶段优惠码

```json
"promo_codes": {
  "initial": {
    "code": "WELCOME15",
    "discount": "15%",
    "valid_days": 7
  },
  "followup": {
    "code": "COMEBACK25",
    "discount": "25%",
    "valid_days": 5
  }
}
```

### 自定义邮件主题

编辑 `email_campaign_manager.py`:

```python
# 在 create_initial_email() 中
msg['Subject'] = f"🚀 {lead['name']}, meet {campaign_config['product_name']}"

# 在 create_followup_email() 中
subject_lines = [
    f"⚡ {lead['name']}, your {promo_config['discount']} discount is waiting",
    f"Last chance: {promo_config['discount']} off ends tomorrow",
]
```

---

## 监控和分析

### 实时监控

```bash
# 查看最近发送的邮件
sqlite3 campaign_tracking.db "
SELECT email, status, sent_at, followup_count
FROM campaigns
ORDER BY sent_at DESC
LIMIT 10
"
```

### 转化漏斗分析

```bash
# 查看转化漏斗
python -c "
import sqlite3
conn = sqlite3.connect('campaign_tracking.db')
cursor = conn.cursor()

# 发送数
cursor.execute('SELECT COUNT(*) FROM campaigns WHERE status=\"sent\"')
sent = cursor.fetchone()[0]

# 跟进数
cursor.execute('SELECT COUNT(*) FROM campaigns WHERE followup_count > 0')
followups = cursor.fetchone()[0]

# 转化数
cursor.execute('SELECT COUNT(*) FROM campaigns WHERE status=\"converted\"')
converted = cursor.fetchone()[0]

print(f'发送: {sent}')
print(f'跟进: {followups} ({followups/sent*100:.1f}%)')
print(f'转化: {converted} ({converted/sent*100:.1f}%)')
"
```

### 导出报表

```bash
# 导出CSV
sqlite3 -header -csv campaign_tracking.db "
SELECT
  email,
  name,
  promo_code,
  status,
  sent_at,
  converted_at,
  followup_count
FROM campaigns
" > campaign_report.csv
```

---

## 最佳实践

### 1. 先小规模测试

```bash
# 测试流程：
# 1. 测试模式 → 10 leads
python src/ultimate_email_finder_with_campaign.py product.md 10 1

# 2. 检查测试邮箱
# 3. 确认邮件质量
# 4. 扩大规模 → 50 leads
# 5. 再扩大 → 100+ leads
```

### 2. 优化邮件内容

- **个性化** - 使用{name}, {username}
- **简洁** - 3-5段，突出价值
- **明确CTA** - 一个主要按钮
- **紧迫感** - 限时优惠
- **社交证明** - 提及从哪里发现他们的

### 3. A/B测试

```python
# 创建两个版本
# Version A: 20% off
# Version B: $20 off

# 发送一半leads到A，一半到B
# 对比转化率
```

### 4. 跟进策略

```
Day 0: 初始邮件（20% off）
Day 1: 等待
Day 2: 第一次跟进（25% off）
Day 3: 等待
Day 4: 最后跟进（30% off + 紧迫感）
```

---

## 故障排除

### 问题1: SMTP连接失败

```
错误: SMTPAuthenticationError: Username and Password not accepted
```

**解决:**
1. 确认开启了Gmail两步验证
2. 使用应用专用密码（不是Gmail密码）
3. 检查配置文件中的用户名和密码

### 问题2: 邮件进垃圾箱

**解决:**
1. 添加SPF/DKIM记录到域名DNS
2. 使用自定义域名（而非gmail.com）
3. 减少发送速度
4. 改进邮件内容（避免spam关键词）

### 问题3: 数据库锁定

```
错误: database is locked
```

**解决:**
```bash
# 关闭所有SQLite连接
lsof | grep campaign_tracking.db

# 或重启系统
```

---

## 总结

### 完整命令速查

```bash
# 1. 配置
cp email_config.example.json email_config.json
# 编辑email_config.json

# 2. 测试运行
python src/ultimate_email_finder_with_campaign.py product.md 10 1

# 3. 生产运行
python src/ultimate_email_finder_with_campaign.py product.md 100 5

# 4. 检查跟进（24小时后）
python src/email_campaign_manager.py --check-followups

# 5. 查看统计
python src/email_campaign_manager.py --stats

# 6. 标记转化
python -c "from src.email_campaign_manager import EmailCampaignManager; EmailCampaignManager().mark_conversion('WELCOME20', 'user@example.com')"
```

### 文件结构

```
MarketingMind AI/
├── email_config.json              # 你的配置（需创建）
├── email_config.example.json      # 配置模板
├── campaign_tracking.db           # 自动创建的数据库
├── src/
│   ├── email_campaign_manager.py          # 营销系统核心
│   ├── ultimate_email_finder_with_campaign.py  # 集成版
│   └── ...
└── EMAIL_CAMPAIGN_SETUP.md        # 本文档
```

---

**🚀 开始你的第一个营销活动！**

```bash
# 立即测试
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1
```

**邮件会发送到: liu.lucian6@gmail.com（测试模式）**
