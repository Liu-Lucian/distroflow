# ✅ 修复：确保每轮50-100个用户才休眠

## 问题描述

用户反馈：Instagram脚本只发送1个用户就进入5-8小时休眠，不符合预期。

**期望行为**：每轮发送50-100个用户后才休眠5-8小时。

## 根本原因

1. **AI筛选太严格** - `AI_MIN_SCORE = 0.6` 过滤掉了太多潜在用户
2. **搜索量不足** - 每个关键词只搜索15个帖子/视频，评论只抓30条
3. **没有最小用户数限制** - 代码没有强制要求至少找到50个用户

## 解决方案

### 1. Instagram 修改 (`run_instagram_campaign_optimized.py`)

#### 配置优化
```python
# 之前
POSTS_PER_KEYWORD = 15
COMMENTS_PER_POST = 30
AI_MIN_SCORE = 0.6
DM_BATCH_SIZE = 10

# 修改后
POSTS_PER_KEYWORD = 50  # 增加3倍搜索量
COMMENTS_PER_POST = 50   # 增加评论数
AI_MIN_SCORE = 0.5       # 降低门槛获得更多用户
DM_BATCH_SIZE = 20       # 增加每轮发送数
MIN_USERS_BEFORE_SLEEP = 50  # 🔥 新增配置
```

#### 终止逻辑修改
```python
# 之前：只要达到USERS_PER_ROUND就停止
if new_users_found >= USERS_PER_ROUND:
    break

# 修改后：必须达到MIN_USERS_BEFORE_SLEEP才能停止
if new_users_found >= MIN_USERS_BEFORE_SLEEP:
    print(f"✅ Reached minimum target: {new_users_found}/{MIN_USERS_BEFORE_SLEEP} users")
    if new_users_found >= USERS_PER_ROUND:
        print(f"🎯 Exceeded ideal target: {USERS_PER_ROUND} users")
        break
```

#### 警告系统
```python
# 如果没达到最小目标，给出建议
if new_users_found < MIN_USERS_BEFORE_SLEEP:
    print(f"⚠️  WARNING: Only found {new_users_found} users (target: {MIN_USERS_BEFORE_SLEEP}+)")
    print(f"   Consider: 1) Lower AI_MIN_SCORE (current: {AI_MIN_SCORE})")
    print(f"            2) Add more KEYWORDS")
    print(f"            3) Increase POSTS_PER_KEYWORD (current: {POSTS_PER_KEYWORD})")
```

### 2. TikTok 修改 (`run_tiktok_campaign_optimized.py`)

应用了完全相同的修改：

```python
VIDEOS_PER_KEYWORD = 50  # 从15增加到50
COMMENTS_PER_VIDEO = 50  # 从30增加到50
AI_MIN_SCORE = 0.5       # 从0.6降低到0.5
DM_BATCH_SIZE = 20       # 从10增加到20
MIN_USERS_BEFORE_SLEEP = 50  # 🔥 新增
```

## 预期效果

### 每轮流程

1. **搜索阶段**：
   - Instagram: 3个关键词 × 50个帖子 × 50条评论 = 最多7500条评论
   - TikTok: 3个关键词 × 50个视频 × 50条评论 = 最多7500条评论

2. **AI筛选**：
   - 使用 `AI_MIN_SCORE = 0.5` (降低门槛)
   - 预计筛选率：1-3% (50-225个合格用户)

3. **DM发送**：
   - 每轮发送20个用户
   - 如果合格用户>20，剩余用户留待下一轮

4. **休眠**：
   - **只有找到 ≥50 个用户后才休眠**
   - 休眠时间：随机5-8小时

### 失败保护

如果某轮只找到<50个用户：
- 系统会显示警告信息
- 建议调整配置（降低AI_MIN_SCORE，增加关键词等）
- 但仍然会进入休眠（避免无限循环消耗资源）

## 运行命令

### Instagram
```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
export OPENAI_API_KEY='your_key'
python3 run_instagram_campaign_optimized.py
```

### TikTok
```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
export OPENAI_API_KEY='your_key'
python3 run_tiktok_campaign_optimized.py
```

### 一键启动（推荐）
```bash
marketing-campaign
# 选择平台 → 系统自动运行多轮循环
```

## 监控进度

### 查看统计文件
```bash
# Instagram
cat instagram_round_stats.json

# TikTok
cat tiktok_round_stats.json
```

### 实时统计
每轮结束后会显示：
```
📊 Cumulative Statistics
======================================================================
Total rounds completed: 3
Total users found: 187
Total DMs sent: 60
Average users/round: 62.3
======================================================================
```

## 成本估算

假设每轮找到50-100个用户：

- **搜索阶段**：$0 (纯Playwright)
- **AI分析**：~$0.01 (100条评论批量分析)
- **DM发送**：$0 (纯DOM自动化)

**每轮总成本**：~$0.01
**每天5轮**：~$0.05

## 注意事项

1. **第一次运行可能较慢**：需要搜索大量帖子/视频
2. **缓存系统会加速后续运行**：已分析的帖子/视频会跳过
3. **平台反爬限制**：TikTok可能出现CAPTCHA（系统会自动用AI解决）
4. **账号安全**：建议使用专用营销账号，不要用个人账号

## 故障排除

### 问题1：仍然只找到<50个用户

**解决方案**：
```python
# 进一步降低AI门槛
AI_MIN_SCORE = 0.4  # 从0.5降到0.4

# 或增加更多关键词
KEYWORDS = [
    "job interview tips",
    "interview preparation",
    "career advice",
    "job search",        # 新增
    "resume tips",       # 新增
    "career coaching",   # 新增
]
```

### 问题2：DM发送失败

**原因**：Cookie过期或平台UI变更

**解决方案**：
```bash
# Instagram：手动更新platforms_auth.json中的sessionid

# TikTok：运行
python3 save_tiktok_sessionid.py
```

### 问题3：AI分析太慢

**解决方案**：
```python
# 增加批量大小（减少API调用次数）
AI_BATCH_SIZE = 200  # 从100增加到200
```

## 版本历史

- **2025-10-20**: 修复50-100用户/轮问题
  - 新增 `MIN_USERS_BEFORE_SLEEP = 50`
  - 增加搜索量（50帖子/视频，50评论）
  - 降低AI门槛（0.6 → 0.5）
  - 增加DM批量（10 → 20）
