# 📧 Email Campaign System - README

**完整的自动化邮件营销系统** - 集成到 MarketingMind AI

---

## ✨ 新功能

✅ **自动化邮件营销** - 找到leads后自动发送介绍邮件
✅ **智能跟进** - 24小时后自动发送更大优惠
✅ **优惠码系统** - 20% → 30%递进式优惠
✅ **转化追踪** - SQLite数据库实时追踪
✅ **测试模式** - 发送到测试邮箱验证效果
✅ **HTML邮件模板** - 专业设计的邮件

---

## 🚀 快速开始（3步骤）

### 步骤1: 运行配置向导 ⚙️

```bash
python setup_wizard.py
```

向导会帮你配置：
- Gmail SMTP设置
- 产品信息
- 优惠码
- 测试模式

### 步骤2: 测试配置 🧪

```bash
python test_email_system.py
```

### 步骤3: 运行测试营销活动 📧

```bash
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1
```

---

## 📋 完整文档

- **QUICK_START_CAMPAIGN.md** - 5分钟快速开始（详细步骤）
- **EMAIL_CAMPAIGN_SETUP.md** - 完整配置指南（Gmail设置等）
- **SYSTEM_STATUS.md** - 系统状态和架构文档
- **EMAIL_VERIFICATION_GUIDE.md** - 邮箱验证使用指南

---

## 🎯 系统流程

```
1. Twitter抓取 (ultimate_email_finder.py)
   ↓
2. 邮箱验证 (email_verifier_v2.py)
   ↓
3. 发送初始邮件 (email_campaign_manager.py)
   - 优惠码: WELCOME20 (20% off)
   ↓
4. 追踪转化 (campaign_tracking.db)
   ↓
5. 24小时后自动跟进
   - 优惠码: LASTCHANCE30 (30% off)
```

---

## 🛠️ 主要文件

### 新增文件
- `src/email_campaign_manager.py` - 邮件营销核心引擎
- `src/ultimate_email_finder_with_campaign.py` - 集成系统
- `email_config.json` - 配置文件
- `setup_wizard.py` - 配置向导
- `test_email_system.py` - 测试脚本
- `campaign_tracking.db` - SQLite数据库（自动创建）

### 配置文件
```json
{
  "smtp": {
    "host": "smtp.gmail.com",
    "username": "your-email@gmail.com",
    "password": "your-app-password"
  },
  "campaign": {
    "product_name": "Your Product",
    "product_url": "https://your-site.com"
  },
  "test_mode": {
    "enabled": true,
    "test_email": "liu.lucian6@gmail.com"
  }
}
```

---

## 📧 邮件示例

### 初始邮件（Day 0）
```
主题: Exclusive 20% Off [Your Product] for @username

Hi John!

I noticed you're interested in [topic]...

🎁 EXCLUSIVE OFFER
Use code WELCOME20 for 20% off!
⏰ Expires in 7 days

[Get Started Now →]
```

### 跟进邮件（Day 1）
```
主题: Don't miss out: 30% off [Your Product]

Hi John,

You haven't claimed your discount yet...

🎁 BETTER OFFER
Was: 20% off
NOW: 30% OFF!

Use code: LASTCHANCE30
⏰ Expires in 3 days!

[Claim Your 30% Discount Now →]
```

---

## 📊 命令参考

### 配置
```bash
# 交互式配置
python setup_wizard.py

# 测试配置
python test_email_system.py
```

### 运行营销活动
```bash
# 测试模式（10个leads）
python src/ultimate_email_finder_with_campaign.py product.md 10 1

# 生产模式（100个leads）
python src/ultimate_email_finder_with_campaign.py product.md 100 5
```

### 管理
```bash
# 查看统计
python src/email_campaign_manager.py --stats

# 检查跟进
python src/email_campaign_manager.py --check-followups
```

---

## 🎯 测试模式

默认情况下，所有邮件发送到测试邮箱（liu.lucian6@gmail.com）

**优点：**
- ✅ 验证邮件外观
- ✅ 测试链接和优惠码
- ✅ 不会打扰真实用户

**切换到生产模式：**
编辑 `email_config.json`:
```json
"test_mode": {
  "enabled": false
}
```

---

## 📈 预期效果

### 测试（10 leads）
```
输入: 10 followers
邮箱验证: 6-8 valid (60-80%)
发送: 6-8 emails
测试邮箱: 收到6-8封
```

### 生产（100 leads）
```
输入: 100 followers
邮箱验证: 70-80 valid (70-80%)
发送: 70-80 emails
转化率: 10-20% (7-16 conversions)
```

---

## 🔧 自动化设置

### Cron Job（自动跟进）
```bash
crontab -e

# 每6小时检查一次
0 */6 * * * cd /Users/l.u.c/my-app/MarketingMind\ AI && python3 src/email_campaign_manager.py --check-followups >> email_campaign.log 2>&1
```

---

## 🆘 常见问题

### Q: Gmail应用密码在哪里？
**A:** https://myaccount.google.com/apppasswords
（需先开启两步验证）

### Q: 测试邮件发不出去？
**A:** 检查：
1. Gmail两步验证是否开启
2. 应用密码是否正确
3. `email_config.json` 配置是否正确

### Q: 如何修改邮件模板？
**A:** 编辑 `src/email_campaign_manager.py`:
- `create_initial_email()` - 初始邮件
- `create_followup_email()` - 跟进邮件

---

## 📚 更多文档

完整详细的文档请查看：
- `QUICK_START_CAMPAIGN.md` - 最详细的快速开始指南
- `EMAIL_CAMPAIGN_SETUP.md` - Gmail配置、SMTP设置
- `SYSTEM_STATUS.md` - 完整系统架构和状态
- `EMAIL_VERIFICATION_GUIDE.md` - 邮箱验证使用

---

## 🎉 开始使用

```bash
# 1. 配置
python setup_wizard.py

# 2. 测试
python test_email_system.py

# 3. 运行
python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1
```

**🚀 准备好开始自动化邮件营销了吗？**
