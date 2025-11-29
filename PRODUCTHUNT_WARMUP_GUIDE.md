# Product Hunt 账号养号指南（7天计划）

## 🎯 为什么要养号？

### Product Hunt 新账号限制

- ⏰ **新账号需等待 1 周**才能发布产品
- 💬 **期间应该积极互动**（评论、点赞、探索）
- 🚀 **订阅 newsletter 可立即发布**（快速通道）
- 👤 **必须是个人账号**（不能是公司账号）

### 养号的好处

✅ **建立社区信誉** - 让社区认识你，不是冷启动
✅ **熟悉平台文化** - 了解什么样的评论受欢迎
✅ **积累人脉** - 评论互动可能带来回访
✅ **算法友好** - 活跃账号发布的产品可能获得更好的曝光

---

## 📅 7天养号计划

### 每日互动目标

| 天数 | 目标互动 | 策略 | 重点 |
|------|---------|------|------|
| **Day 1-2** | 2次/天 | 探索期 | 熟悉平台，选择相关类别 |
| **Day 3-5** | 3次/天 | 活跃期 | 增加互动，建立存在感 |
| **Day 6-7** | 4次/天 | 冲刺期 | 最大化曝光，准备发布 |

**总计**：21 次互动（点赞 + 评论）

---

## 🚀 快速开始

### 第1步：设置 API Key

```bash
export OPENAI_API_KEY='sk-proj-...'
```

### 第2步：确保已登录 Product Hunt

```bash
# 如果还没登录：
python3 producthunt_login_and_save_auth.py
```

### 第3步：配置今日目标产品

编辑 `producthunt_account_warmup.py`，找到 `get_todays_target_products()` 函数（约第 110 行），添加今天的产品：

```python
example_products = [
    {
        'url': 'https://www.producthunt.com/posts/产品名',
        'name': '产品名',
        'tagline': '产品标语',
        'category': 'AI Tools, Productivity',
        'description': '产品描述'
    },
    # 每天添加 3-5 个相关产品
]
```

**如何找产品**：
1. 访问 [Product Hunt](https://www.producthunt.com)
2. 点击 "Today" 查看今日发布
3. 筛选 AI Tools / Productivity / Career 类别
4. 选择 3-5 个看起来有趣的产品

### 第4步：查看养号进度

```bash
python3 producthunt_account_warmup.py
# 选择 "1. 查看养号进度"
```

### 第5步：执行今日任务

```bash
python3 producthunt_account_warmup.py
# 选择 "2. 执行今日养号任务"
```

---

## 💬 评论策略

### ✅ 好的养号评论

#### 示例 1：热情支持型
```
Yooo this looks fire 🔥 I've been looking for something exactly like this ngl.
Quick Q - does it work with Google Calendar? That'd be perfect fr
```

**特点**：
- 热情（Yooo, fire）
- 网络用语（ngl, fr）
- 提出实际问题
- 专注对方产品

---

#### 示例 2：问题导向型
```
Love the concept! Curious about the tech stack - did you go with serverless
for this? Debating that approach myself for a side project lol
```

**特点**：
- 技术好奇
- 自然分享背景（side project）
- 不提具体产品名
- 轻松语气（lol）

---

#### 示例 3：痛点共鸣型
```
This solves a real problem tbh. I've tried like 5 tools for this and they
all fell short. How'd you tackle [specific challenge]?
```

**特点**：
- 真实经历
- 网络用语（tbh）
- 具体问题
- 鼓励分享经验

---

### ❌ 避免的评论

#### 错误 1：硬推销
```
❌ "Great product! You should check out HireMeAI too at..."
```

#### 错误 2：太正式
```
❌ "Congratulations on your successful product launch. I believe this will
be very beneficial for users seeking productivity solutions."
```

#### 错误 3：太泛泛
```
❌ "Great work!"
❌ "Nice product"
❌ "Love it"
```

---

## 📊 进度追踪

### 自动记录

脚本会自动记录：
- ✅ 每日完成情况
- ✅ 总互动次数
- ✅ 已互动产品（避免重复）
- ✅ 距离发布日期剩余天数

**进度文件**：`producthunt_warmup_progress.json`

### 查看进度

```bash
python3 producthunt_account_warmup.py
# 选择 "1. 查看养号进度"
```

**输出示例**：
```
📊 Product Hunt 账号养号进度

⏰ 时间线:
   开始日期: 2025-10-23
   目标发布: 2025-10-30
   当前进度: 第 3/7 天
   剩余时间: 4 天

📈 互动统计:
   总互动次数: 7
   总点赞数: 7
   总评论数: 7

📅 每日计划:
   Day 1: ✅ 2/2 次互动
   Day 2: ✅ 2/2 次互动
   Day 3: 🔄 3/3 次互动
   Day 4: ⏳ 0/3 次互动
   Day 5: ⏳ 0/3 次互动
   Day 6: ⏳ 0/4 次互动
   Day 7: ⏳ 0/4 次互动

🎯 今日任务: 还需完成 0 次互动
```

---

## 🎯 每日执行清单

### 早上（选择产品）

```bash
# 1. 访问 Product Hunt
open https://www.producthunt.com

# 2. 浏览 "Today" 页面

# 3. 记录 3-5 个相关产品信息

# 4. 更新 producthunt_account_warmup.py
```

### 中午（执行任务）

```bash
# 1. 运行养号脚本
python3 producthunt_account_warmup.py

# 2. 选择 "2. 执行今日养号任务"

# 3. 等待自动完成（约 20-30 分钟）
```

### 晚上（检查进度）

```bash
# 1. 查看进度
python3 producthunt_account_warmup.py

# 2. 选择 "1. 查看养号进度"

# 3. 手动访问 Product Hunt 检查评论是否发布
```

---

## ⚡ 快速通道：订阅 Newsletter

如果不想等 7 天，可以订阅 Product Hunt Newsletter 立即获得发布权限：

1. 访问 [Product Hunt](https://www.producthunt.com)
2. 找到 Newsletter 订阅入口
3. 订阅后即可立即发布

**但仍建议先养号 2-3 天**，建立基础信誉后再发布效果更好。

---

## 🔧 高级配置

### 调整每日互动次数

编辑 `producthunt_account_warmup.py`，找到 `_load_progress()` 函数（约第 30 行）：

```python
"daily_plan": [
    {"day": 1, "target_interactions": 3, ...},  # 改为 3
    {"day": 2, "target_interactions": 3, ...},  # 改为 3
    # ...
]
```

### 自定义评论风格

编辑 `generate_warmup_comment()` 函数的 prompt（约第 80 行），调整：
- 网络用语使用频率
- emoji 数量
- 评论长度
- 提问风格

---

## 📈 成功指标

### 7天结束时应达到：

- ✅ **21+ 次互动**（点赞 + 评论）
- ✅ **7+ 个产品互动**（分散到不同产品）
- ✅ **0 次 spam 投诉**（质量 > 数量）
- ✅ **熟悉 Product Hunt 文化**

### 衡量标准：

| 指标 | 目标 | 说明 |
|------|------|------|
| **互动次数** | 21+ | 每天 2-4 次 |
| **评论质量** | 高质量 | 真诚、有价值、无 spam |
| **产品相关性** | 100% | 只与 AI/Productivity/Career 相关 |
| **社区反馈** | 正向 | 有人回复你的评论 |

---

## 🎉 养号完成后

### Day 8：准备发布

```bash
# 1. 检查账号是否可以发布
# 访问 Product Hunt，点击右上角 "Submit"

# 2. 如果可以发布，准备素材
# - 封面图（512x512）
# - Gallery（3-5张）
# - Demo 视频

# 3. 运行发布脚本
python3 producthunt_launcher.py
```

---

## ⚠️ 注意事项

### 避免被判为 Spam

- ❌ 不要在短时间内大量评论
- ❌ 不要使用相同的评论模板
- ❌ 不要只点赞不评论
- ❌ 不要推销自己的产品

### 保持真实性

- ✅ 每条评论都要真诚
- ✅ 只评论你真正感兴趣的产品
- ✅ 提出真实的问题
- ✅ 如果有人回复，继续对话

---

## 🐛 常见问题

### Q1: 评论发布后看不到？

**A**: 可能需要刷新页面，或者 Product Hunt 有审核机制。等待 5-10 分钟。

### Q2: 是否需要每天都运行？

**A**: 建议每天执行，但可以灵活调整。重要的是总互动次数达标。

### Q3: 可以跳过某几天吗？

**A**: 可以，但建议保持连续性。如果某天错过了，可以在后续几天补上。

### Q4: 养号期间可以发布产品吗？

**A**:
- 新账号：不行，必须等 7 天
- 订阅 newsletter：可以立即发布
- 建议：即使订阅了，也先养号 2-3 天

---

## 📞 技术支持

**问题反馈**: liu.lucian6@gmail.com

**产品官网**: https://interviewasssistant.com

---

## 📚 相关文档

- `producthunt_account_warmup.py` - 养号脚本
- `PRODUCTHUNT_LAUNCH_GUIDE.md` - 完整发布指南
- `PRODUCTHUNT_QUICKSTART.md` - 快速开始

---

**Good luck with your warmup! 🚀**

养号期间多探索，多学习，多互动 —— 这不仅是为了满足平台要求，更是为了真正融入 Product Hunt 社区！
