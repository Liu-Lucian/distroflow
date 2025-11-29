# 📊 邮件营销跟踪指南

## 当前状态
✅ 已发送38封营销邮件
✅ 目标客户包括：Salesforce、ProductHunt、Ceridian等
✅ 邮件包含跟踪参数

## 邮件中的跟踪链接

每封邮件的链接格式：
```
https://interviewasssistant.com?promo=VIP888&email={email}&ref=@{username}
```

例如：
```
https://interviewasssistant.com?promo=VIP888&email=marc@salesforce.com&ref=@Benioff
```

## 需要在网站后端实现的跟踪

### 1. 记录点击事件
当用户点击邮件链接访问网站时：

```javascript
// 在你的网站首页添加
const urlParams = new URLSearchParams(window.location.search);
const promoCode = urlParams.get('promo');
const email = urlParams.get('email');
const ref = urlParams.get('ref');

if (promoCode && email) {
    // 发送跟踪事件到后端
    fetch('/api/track-email-click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            promo_code: promoCode,
            email: email,
            ref: ref,
            timestamp: new Date().toISOString()
        })
    });
}
```

### 2. 后端API记录点击

```python
# Flask 示例
@app.route('/api/track-email-click', methods=['POST'])
def track_email_click():
    data = request.json

    # 更新 MarketingMind AI 的数据库
    conn = sqlite3.connect('/Users/l.u.c/my-app/MarketingMind AI/campaign_tracking.db')
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE campaigns
        SET opened_at = ?
        WHERE email = ? AND promo_code = ? AND opened_at IS NULL
    ''', (datetime.now(), data['email'], data['promo_code']))

    conn.commit()
    conn.close()

    return {'status': 'success'}
```

### 3. 记录转化（用户注册/购买）

当用户使用优惠码注册或购买时：

```python
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    promo_code = data.get('promo_code')
    email = data.get('email')

    # 你的正常注册逻辑...

    # 记录转化
    if promo_code:
        conn = sqlite3.connect('/Users/l.u.c/my-app/MarketingMind AI/campaign_tracking.db')
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE campaigns
            SET status = 'converted', converted_at = ?
            WHERE email = ? AND promo_code = ?
        ''', (datetime.now(), email, promo_code))

        conn.commit()
        conn.close()

    return {'status': 'success'}
```

## 查看转化数据

### 查看点击率
```bash
cd /Users/l.u.c/my-app/MarketingMind\ AI
sqlite3 campaign_tracking.db "
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
    ROUND(100.0 * SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as open_rate
FROM campaigns
"
```

### 查看转化率
```bash
sqlite3 campaign_tracking.db "
SELECT
    COUNT(*) as total,
    SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) as converted,
    ROUND(100.0 * SUM(CASE WHEN status = 'converted' THEN 1 ELSE 0 END) / COUNT(*), 2) as conversion_rate
FROM campaigns
"
```

### 查看最有价值的客户
```bash
sqlite3 campaign_tracking.db "
SELECT email, name, opened_at, converted_at
FROM campaigns
WHERE status = 'converted'
ORDER BY converted_at DESC
"
```

## 24小时后自动跟进

系统已经设置了cron job，会在24小时后自动：
1. 检查哪些客户还没转化
2. 发送更大优惠的跟进邮件（30% OFF，优惠码VIP999）
3. 最多跟进2次

### 手动触发跟进（不用等24小时）
```bash
cd /Users/l.u.c/my-app/MarketingMind\ AI
python3 src/email_campaign_manager.py --check-followups
```

## Gmail退信监控

### 查看退信邮件
1. 打开 liu.lucian6@gmail.com
2. 搜索："Delivery Status Notification"
3. 找出所有退信的邮箱地址

### 标记无效邮箱（可选）
```bash
sqlite3 campaign_tracking.db "
UPDATE campaigns
SET status = 'bounced', notes = 'Email bounced - address not found'
WHERE email IN (
    'datacenter@pobox.com',
    'other_bounced@email.com'
)
"
```

## 优化建议

### 提高邮件送达率
1. ✅ 已实现：随机延迟30-90秒
2. ✅ 已实现：个性化内容
3. 建议添加：SPF/DKIM记录到你的域名
4. 建议添加：使用自定义域名发送（而不是@gmail.com）

### 提高转化率
1. A/B测试不同主题行
2. 在24小时跟进邮件中突出新优惠
3. 添加紧迫感（"仅剩XX个名额"）
4. 展示社会证明（"2000+用户"）

## 当前营销漏斗

```
38封邮件发送 (100%)
    ↓
? 封邮件打开 (目标: 20-30%)
    ↓
? 次链接点击 (目标: 5-10%)
    ↓
? 个注册转化 (目标: 1-3%)
```

实施网站跟踪后，你就能看到完整的转化漏斗数据！
