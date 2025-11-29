# TikTok 多轮循环营销系统

## 🎯 系统特点

**全自动持续运行**，无需人工干预：

✅ **每轮自动找50-100个精准用户**
✅ **完成后自动休息5-8小时**
✅ **自动开始下一轮**
✅ **循环往复，持续运行**
✅ **智能统计，进度可查**

---

## 🚀 快速开始

### Step 1: 登录TikTok（一次性）

```bash
python3 tiktok_login_and_save_auth.py
```

浏览器会自动打开，手动登录TikTok，cookies会自动保存。

---

### Step 2: 配置参数

编辑 `run_tiktok_campaign_optimized.py`：

```python
# 产品描述
PRODUCT_DESCRIPTION = """
你的产品介绍
"""

# 关键词（系统会搜索这些关键词的视频）
KEYWORDS = [
    "job interview",
    "career advice",
    "job search tips",
]

# 🎯 搜索配置
USERS_PER_ROUND = 100  # 每轮目标用户数：50-100
VIDEOS_PER_KEYWORD = 15  # 每个关键词搜索15个视频
COMMENTS_PER_VIDEO = 30  # 每个视频抓30条评论

# 🔄 多轮循环配置
ENABLE_LOOP = True  # 启用多轮循环
ROUND_DELAY_HOURS = (5, 8)  # 每轮间隔5-8小时
MAX_ROUNDS = 10  # 最多10轮（0表示无限循环）

# DM配置
DM_BATCH_SIZE = 10  # 每轮发送10条DM
DM_DELAY = (60, 180)  # 每条DM间隔1-3分钟

# 消息模板
MESSAGE_TEMPLATE = """Hey {{name}}, I saw your video about {{topic}}!

I'm building [你的产品]...

{{pain_point_mention}}

Would love your thoughts!"""
```

---

### Step 3: 运行系统

```bash
export OPENAI_API_KEY='your_openai_key'
python3 run_tiktok_campaign_optimized.py
```

---

## 📊 运行示例

### 启动界面：

```
======================================================================
🎵 TikTok Smart Campaign - Optimized
======================================================================

🔄 Multi-round loop mode ENABLED
   Target users per round: 100
   Rest between rounds: 5-8 hours
   Max rounds: 10

======================================================================
```

### Round 1：

```
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
🚀 ROUND 1 / 10
Started: 2025-10-19 14:30:00
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

🔑 Keyword: job interview
======================================================================

🔍 Searching TikTok for: 'job interview'...
   ✅ Found 15 videos

🎥 Video: https://www.tiktok.com/@user/video/123...
📝 Scraping comments from video...
   📜 Loading comments...
   🔍 Extracting comments...
   ✅ Scraped 30 comments

🧠 AI Analysis (Only GPT call)...
   Analyzing 30 comments in one batch
   Estimated cost: < $0.001
   ✅ AI identified 8 qualified users

✅ Reached target: 100 users

======================================================================
📊 Round Summary
======================================================================
New users found: 102
Total qualified users: 102
Ready for DM: 102

💬 Starting DM campaign...
[1/10] Sending to @user1...
   ✅ Sent
   ⏳ Waiting 120s...
...

✅ Round completed!
💰 AI cost this round: ~$0.1020

======================================================================
📊 Cumulative Statistics
======================================================================
Total rounds completed: 1
Total users found: 102
Total DMs sent: 10
Average users/round: 102.0
======================================================================

💤 Resting for 6.3 hours...
   Will resume at: 2025-10-19 20:48:00
   Press Ctrl+C to stop the loop
```

### Round 2 自动开始：

```
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄
🚀 ROUND 2 / 10
Started: 2025-10-19 20:48:00
🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄🔄

...
```

### 完成所有轮次：

```
======================================================================
🎉 All rounds completed!
======================================================================

Total rounds: 10
Total users found: 1,023
Total DMs sent: 100
```

---

## 💡 工作原理

### 单轮流程：

```
1. 搜索关键词视频（15个/关键词）
   ↓
2. 抓取视频评论（30条/视频）
   ↓
3. AI分析用户意图（批量，降本）
   ↓
4. 过滤高分用户（>0.6分）
   ↓
5. 发送DM（10条/轮）
   ↓
6. 保存进度
   ↓
7. 达到100用户 → 进入休息
```

### 多轮循环：

```
Round 1: 找100用户 → 发10条DM → 休息5-8小时
   ↓
Round 2: 找100用户 → 发10条DM → 休息5-8小时
   ↓
Round 3: 找100用户 → 发10条DM → 休息5-8小时
   ↓
...
   ↓
Round 10: 完成
```

---

## 📈 优势对比

### 旧版（单轮）：

- ❌ 只能找到少量用户（~20个）
- ❌ 需要手动重启
- ❌ 无法持续运行
- ❌ 无累计统计

### 新版（多轮循环）：

- ✅ 每轮自动找50-100个用户
- ✅ 自动休息，自动重启
- ✅ 持续运行，无需干预
- ✅ 智能统计，进度透明
- ✅ 可随时中断，安全恢复

---

## 🎛 配置说明

### 关键参数：

| 参数 | 作用 | 推荐值 | 说明 |
|------|------|--------|------|
| `USERS_PER_ROUND` | 每轮目标用户数 | 50-100 | 太少效率低，太多易被检测 |
| `VIDEOS_PER_KEYWORD` | 每个关键词搜索视频数 | 10-20 | 视频越多，用户越多 |
| `COMMENTS_PER_VIDEO` | 每个视频抓评论数 | 20-30 | 评论越多，分析越准 |
| `ENABLE_LOOP` | 是否启用循环 | `True` | 开启自动循环 |
| `ROUND_DELAY_HOURS` | 轮次间隔（小时）| (5, 8) | 模拟真人，避免检测 |
| `MAX_ROUNDS` | 最大轮数 | 10 | 0=无限循环 |
| `DM_BATCH_SIZE` | 每轮发DM数 | 10 | 避免一次发太多被封 |

### 安全建议：

1. **首次运行**：设置 `USERS_PER_ROUND = 20`, `DM_BATCH_SIZE = 3`，小规模测试
2. **观察效果**：如果成功，逐步增加到 `50-100`
3. **账号安全**：不要设置太短的间隔（最少5小时）
4. **随时中断**：按 `Ctrl+C` 可随时停止，下次继续

---

## 📊 统计追踪

系统会自动保存统计到 `tiktok_round_stats.json`：

```json
{
  "rounds_completed": 5,
  "total_users_found": 487,
  "total_dms_sent": 50,
  "last_run": "2025-10-19T20:30:00",
  "start_time": "2025-10-19T10:00:00"
}
```

**查看统计**：

```bash
cat tiktok_round_stats.json
```

---

## 💰 成本预估

### AI分析成本（GPT-4o-mini）：

- 每批30条评论 ≈ $0.001
- 每轮100个用户 ≈ $0.10
- 10轮 ≈ $1.00

### 其他成本：

- 爬虫：$0（纯Playwright）
- DM发送：$0（纯选择器）
- 服务器：如需24/7运行，AWS EC2约$10/月

**总成本（10轮）**：~$1-2

---

## 🔧 故障排查

### 问题1：找不到视频

**原因**：关键词太冷门，或TikTok反爬

**解决**：
1. 更换关键词
2. 降低 `VIDEOS_PER_KEYWORD`
3. 增加延迟

### 问题2：找不到评论

**原因**：视频太新，还没评论

**解决**：
1. 增加 `VIDEOS_PER_KEYWORD`（搜更多视频）
2. 更换关键词

### 问题3：AI分析失败

**原因**：OpenAI API key无效

**解决**：
```bash
export OPENAI_API_KEY='your_valid_key'
```

### 问题4：DM发送失败

**原因**：TikTok检测到异常行为

**解决**：
1. 增加 `DM_DELAY`（延迟更长）
2. 减少 `DM_BATCH_SIZE`（每轮发更少）
3. 增加 `ROUND_DELAY_HOURS`（间隔更长）

### 问题5：系统中断后如何恢复？

**解决**：直接重新运行，系统会：
- 加载之前的用户列表
- 跳过已发DM的用户
- 继续下一轮

---

## 🎯 最佳实践

### 1. 选择热门关键词：

```python
# ✅ 好的关键词（搜索量大）
KEYWORDS = [
    "job interview tips",      # 100万+视频
    "career advice",           # 50万+视频
    "remote work life"         # 30万+视频
]

# ❌ 差的关键词（太冷门）
KEYWORDS = [
    "enterprise saas marketing",  # 只有几百个视频
]
```

### 2. 逐步扩大规模：

```
Day 1: USERS_PER_ROUND = 20, MAX_ROUNDS = 2
   ↓ 观察效果
Day 2: USERS_PER_ROUND = 50, MAX_ROUNDS = 5
   ↓ 如果正常
Day 3: USERS_PER_ROUND = 100, MAX_ROUNDS = 10
```

### 3. 定期检查：

```bash
# 查看统计
cat tiktok_round_stats.json

# 查看用户列表
cat tiktok_qualified_users.json | grep "sent_dm"
```

### 4. 优化消息模板：

```python
# 个性化提及用户痛点
MESSAGE_TEMPLATE = """Hey {{name}}!

Saw your content about {{topic}} - really insightful!

{{pain_point_mention}}  # AI自动填充用户痛点

[Your pitch]

Curious to hear your thoughts!"""
```

---

## 🚨 安全提示

### ⚠️ 避免被封：

1. **不要贪快**：间隔至少5小时
2. **不要群发**：每轮最多10-20条DM
3. **不要重复**：系统会自动去重
4. **不要垃圾内容**：消息要个性化

### ✅ 推荐设置：

```python
# 安全的配置
USERS_PER_ROUND = 50          # 适中
ROUND_DELAY_HOURS = (6, 10)   # 充足间隔
DM_BATCH_SIZE = 5             # 保守发送
DM_DELAY = (120, 300)         # 2-5分钟延迟
```

---

## 📚 相关文档

- `TIKTOK_README.md` - TikTok基础使用
- `COMMANDS.md` - 所有平台命令
- `PLATFORMS_OVERVIEW.md` - 平台总览

---

## 🎉 现在开始吧！

```bash
# 1. 登录
python3 tiktok_login_and_save_auth.py

# 2. 配置
nano run_tiktok_campaign_optimized.py
# 修改 KEYWORDS, USERS_PER_ROUND, ENABLE_LOOP 等

# 3. 运行
export OPENAI_API_KEY='your_key'
python3 run_tiktok_campaign_optimized.py

# 4. 观察输出，系统会自动循环运行
# 按Ctrl+C可随时停止
```

**祝你营销成功！** 🚀
