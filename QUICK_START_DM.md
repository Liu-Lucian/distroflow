# 🚀 快速开始 - 私信功能

## 5分钟上手指南

### 1. 测试初始化（不发送）

```bash
python3 test_dm_senders.py
```

输出应该是：
```
✅ PASS - LinkedIn
✅ PASS - Twitter
✅ PASS - Reddit
✅ PASS - Instagram
✅ PASS - TikTok

🎯 Results: 5/5 platforms initialized successfully
```

### 2. 发送第一条测试消息

推荐从 **LinkedIn** 开始（最安全）:

```bash
python3 test_dm_real.py
```

然后：
1. 输入 `1` (选择LinkedIn)
2. 等待搜索用户
3. 查看要发送的消息
4. 输入 `yes` 确认发送
5. 观察浏览器自动操作

### 3. 常用命令

```bash
# 测试LinkedIn
python3 test_dm_real.py  # 选择 1

# 测试Twitter
python3 test_dm_real.py  # 选择 2

# 测试Reddit
python3 test_dm_real.py  # 选择 3
```

## 🎯 你的消息模板

默认模板在 `test_dm_real.py` 中：

```python
"""Hey {{name}}, I came across your work at {{company}} — really liked what you're doing with {{project}}.

I'm building something called HireMeAI, it helps teams prep for interviews with AI feedback and auto-review tools.

If you're open to it, I'd love to get your quick thoughts — always great hearing from people actually running interviews."""
```

### 自定义消息

在 `test_dm_real.py` 中修改 `TEST_MESSAGE_TEMPLATE`

支持的变量:
- `{{name}}` - 姓名
- `{{username}}` - 用户名
- `{{company}}` - 公司
- `{{project}}` - 项目
- `{{product}}` - 产品

## ⚠️ 安全建议

### 每日限制

- LinkedIn: 20-30条
- Twitter: 15-20条
- Reddit: 10-15条
- Instagram: 5-10条
- TikTok: 3-5条

### 延迟设置

连续发送时，添加延迟：

```python
import time
import random

# 每条消息后等待1-3分钟
time.sleep(random.uniform(60, 180))
```

## 🐛 常见问题

### 1. "Not logged in" 错误

**LinkedIn/Twitter:**
```bash
# 检查cookies文件
ls -la linkedin_auth.json
ls -la platforms_auth.json
```

如果文件不存在或过期，重新登录：
```bash
python3 linkedin_login_and_save_auth.py
```

**Reddit:**
在 `platforms_auth.json` 中添加：
```json
{
  "reddit": {
    "username": "your_username",
    "password": "your_password"
  }
}
```

### 2. "Could not find message button" 错误

- 用户可能未开启私信功能
- 跳过该用户，尝试下一个

### 3. 账号被限制

- 降低发送频率
- 增加延迟时间
- 暂停1-2天

## 📊 推荐策略

### 初次使用

第1天:
- ✅ LinkedIn: 5条测试
- ✅ Twitter: 3条测试
- 观察回复情况

第2-3天:
- ✅ LinkedIn: 10条
- ✅ Twitter: 5条

第4天开始:
- ✅ LinkedIn: 20-30条/天
- ✅ Twitter: 15-20条/天
- ✅ Reddit: 10条/天

### 高级策略

1. **A/B测试**
   - 测试不同消息模板
   - 追踪回复率

2. **时间优化**
   - LinkedIn: 工作日 9AM-5PM
   - Twitter: 全天，晚上更活跃
   - Reddit: 晚上7PM-11PM

3. **目标细分**
   - CEO/创始人 → LinkedIn
   - 开发者 → Twitter/Reddit
   - 年轻创业者 → Instagram/TikTok

## 🎉 完成！

现在你可以：

✅ 在5个平台上发送私信
✅ 自动化外展流程
✅ 个性化每条消息

有问题随时告诉我！
