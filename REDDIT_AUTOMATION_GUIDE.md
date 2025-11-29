# Reddit Build in Public Automation System

## 🎯 System Overview

Automated Reddit posting system for HireMeAI (https://interviewasssistant.com) using "Build in Public" strategy.

**Key Features**:
- ✅ Smart account aging strategy (prevents bans)
- ✅ AI-generated authentic content (5 types: progress, technical, story, learning, milestone)
- ✅ Forever-running automation with intelligent scheduling
- ✅ Cookie-based authentication (no Reddit API needed)
- ✅ Automatic content generation with URL inclusion

## 📋 System Components

### 1. `reddit_login_and_save_auth.py`
**Purpose**: Save Reddit login cookies for automated posting

**What it does**:
- Opens Reddit login page in browser
- Waits for you to login manually
- Automatically extracts and saves cookies to `reddit_auth.json`

### 2. `src/reddit_poster.py`
**Purpose**: Core Playwright automation for posting to Reddit

**Features**:
- Multiple selector fallbacks (robust against UI changes)
- Natural typing simulation (random delays)
- Success verification (checks URL contains `/comments/`)

### 3. `reddit_account_manager.py`
**Purpose**: Smart account aging and posting limit enforcement

**Account Phases**:
| Phase | Age | Daily Limit | Min Interval | Strategy |
|-------|-----|-------------|--------------|----------|
| **Cold Start** | 0-5 days | 1 post/day | 24 hours | Conservative start |
| **Growing** | 5-14 days | 1 post/day | 12 hours | Build reputation |
| **Stable** | 15-30 days | 2-3 posts/day | 4 hours | Increase activity |
| **Mature** | 30+ days | 4 posts/day | 2 hours | Full capacity |

### 4. `auto_reddit_scheduler.py`
**Purpose**: Main automation loop - runs forever

**What it does**:
- Checks if posting is allowed (based on account age rules)
- Generates random Build in Public content
- Posts to Reddit
- Records success/failure
- Waits randomly (30-60 min if success, 1hr if can't post)

### 5. `src/generate_reddit_build_in_public.py`
**Purpose**: AI content generation (GPT-4o-mini)

**Post Types**:
- **Progress**: Weekly updates with metrics
- **Technical**: Problem-solving stories
- **Story**: Founder journey and insights
- **Learning**: Mistakes and lessons learned
- **Milestone**: Achievements with data

## 🚀 Quick Start Guide

### Step 1: Set Up Reddit Authentication

```bash
# Run the login helper
python3 reddit_login_and_save_auth.py
```

**What will happen**:
1. Browser opens to Reddit login page
2. **You manually login** (username + password)
3. Press Enter when login is complete
4. Script automatically saves cookies to `reddit_auth.json`

**Expected Output**:
```
🔐 Reddit 登录并保存认证
...
✅ 认证信息已保存到 reddit_auth.json
   共保存 XX 个cookies
```

### Step 2: Check Account Status (Optional)

```bash
# View current account phase and posting limits
python3 reddit_account_manager.py
```

**Expected Output**:
```
📊 Reddit账号状态
账号年龄: 0天
当前阶段: cold_start
总发帖数: 0
今日已发: 0
每日上限: 1
最小间隔: 24小时

当前状态: ✅ 可以发帖
原因: 首次发帖
```

### Step 3: Start Automated Posting

```bash
# Run the forever-running scheduler
python3 auto_reddit_scheduler.py
```

**What will happen**:
1. System checks account status and posting limits
2. If can post: generates Build in Public content → posts to Reddit → waits 30-60 min
3. If can't post: waits 1 hour → checks again
4. Runs forever (press Ctrl+C to stop)

**Expected Output**:
```
🚀 Reddit Build in Public自动发帖系统 - 永久运行模式

📊 账号状态:
   账号年龄: 0天
   当前阶段: cold_start
   总发帖数: 0
   今日已发: 0/1
   最小间隔: 24小时

⏰ 开始监控，智能发帖...

✅ 满足发帖条件，开始发帖流程

📝 生成Build in Public内容...
   ✅ 内容生成完成 (类型: progress)
   标题: Week 3 of building HireMeAI: 150+ users...
   板块: r/Startups

📤 准备发布到 r/Startups...
   访问 https://www.reddit.com/r/Startups
   填写标题...
   填写正文...
   发布帖子...

✅ 帖子发布成功！
   URL: https://www.reddit.com/r/Startups/comments/xxx/...

✅ 发帖成功！
   今日已发: 1/1

⏳ 随机等待 45 分钟...
```

## 🎯 Target Subreddits

The system automatically posts to these communities:
- **r/Startups** - Startup journey and milestones
- **r/ArtificialIntelligence** - AI/tech discussions
- **r/EntrepreneurRideAlong** - Build in public community
- **r/SaaS** - SaaS product updates

## 📊 Account Aging Strategy Explained

### Why This Matters
Reddit's anti-spam system is **very aggressive**. New accounts posting too frequently get:
- Shadow banned (posts invisible to others)
- Permanently banned (account lost)

### Our Strategy
**Progressive ramping** - Start slow, build reputation, increase activity:

**Days 0-5 (Cold Start)**:
- **What**: Only 1 post per day, 24hr gaps
- **Why**: New accounts are heavily monitored
- **Goal**: Establish account legitimacy

**Days 5-14 (Growing)**:
- **What**: 1 post per day, 12hr gaps
- **Why**: Building karma and post history
- **Goal**: Gain subreddit trust

**Days 15-30 (Stable)**:
- **What**: 2-3 posts per day, 4hr gaps
- **Why**: Account has proven legitimacy
- **Goal**: Increase reach while staying safe

**Days 30+ (Mature)**:
- **What**: Up to 4 posts per day, 2hr gaps
- **Why**: Established account with history
- **Goal**: Maximum marketing impact

### Automatic Enforcement
The `reddit_account_manager.py` **automatically enforces** these limits. You can't accidentally over-post.

## 🔧 Customization

### Change Posting Limits

Edit `reddit_account_manager.py`:

```python
def get_daily_post_limit(self):
    limits = {
        "cold_start": 1,    # Change these numbers
        "growing": 1,
        "stable": 3,
        "mature": 4
    }
```

### Change Minimum Intervals

Edit `reddit_account_manager.py`:

```python
def get_minimum_interval_hours(self):
    intervals = {
        "cold_start": 24,   # Change these hours
        "growing": 12,
        "stable": 4,
        "mature": 2
    }
```

### Change Random Wait Time

Edit `auto_reddit_scheduler.py` line 79:

```python
wait_time = random.randint(1800, 3600)  # 30-60 minutes
# Change to:
wait_time = random.randint(900, 1800)   # 15-30 minutes (more aggressive)
# Or:
wait_time = random.randint(3600, 7200)  # 1-2 hours (safer)
```

### Change Product Description

Edit `src/generate_reddit_build_in_public.py` lines 15-25:

```python
PRODUCT_DESCRIPTION = """
HireMeAI (https://interviewasssistant.com) is an AI-powered interview assistant...
[Customize your product description here]
"""
```

## 📁 Data Files

### `reddit_auth.json`
**Created by**: `reddit_login_and_save_auth.py`

**Contains**: Reddit login cookies for automated posting

**Format**:
```json
{
  "cookies": [...],
  "saved_at": "2025-10-22 18:00:00"
}
```

**When to update**: If login expires (usually every 30 days)

### `reddit_account_state.json`
**Created by**: `reddit_account_manager.py` (automatically on first run)

**Contains**: Account history and posting records

**Format**:
```json
{
  "account_created_at": "2025-10-22T18:00:00",
  "total_posts": 5,
  "posts_history": [
    {
      "timestamp": "2025-10-22T18:30:00",
      "subreddit": "r/Startups",
      "title": "Week 3 of building HireMeAI...",
      "success": true
    }
  ],
  "current_phase": "cold_start",
  "last_post_at": "2025-10-22T18:30:00"
}
```

**DO NOT manually edit** - automatically managed by system

## 🚨 Troubleshooting

### Problem: "❌ 找不到认证文件: reddit_auth.json"

**Solution**: Run authentication setup first
```bash
python3 reddit_login_and_save_auth.py
```

### Problem: "❌ 未登录"

**Solution**: Cookies expired, re-run authentication
```bash
python3 reddit_login_and_save_auth.py
```

### Problem: "⏸️ 暂不满足发帖条件: 今日已达发帖上限"

**Solution**: This is NORMAL. Account aging system is protecting you from ban. Wait until tomorrow.

### Problem: "⏸️ 暂不满足发帖条件: 距离上次发帖不足X小时"

**Solution**: This is NORMAL. Wait for the minimum interval to pass.

### Problem: "❌ 找不到Create Post按钮"

**Solution**: Reddit UI changed. Update selectors in `src/reddit_poster.py` line 104-108:
```python
create_selectors = [
    'a[href*="submit"]',
    'button:has-text("Create")',
    'a:has-text("Create Post")',
    # Add new selectors here
]
```

### Problem: Posts are being shadow banned

**Solution**: You're posting too aggressively. Account aging system should prevent this, but if it happens:
1. Stop posting for 3-5 days
2. Manually comment on other posts (build karma)
3. Increase wait times in `auto_reddit_scheduler.py`
4. Lower daily limits in `reddit_account_manager.py`

## 🎯 Content Quality Tips

The system generates authentic Build in Public content, but you can improve results:

### 1. Update Product Description
Edit `src/generate_reddit_build_in_public.py` with:
- Specific features (not generic "AI-powered")
- Real user numbers (if you have them)
- Unique value proposition

### 2. Monitor Generated Content
First few posts: Run with `headless=False` in `auto_reddit_scheduler.py` line 110:
```python
self.poster.setup_browser(headless=False)  # See what's being posted
```

### 3. Manually Review
Before going fully automated:
1. Run scheduler for 1 day
2. Check Reddit to see actual posts
3. Verify they look authentic
4. Adjust prompts if needed

## 🔄 Running Both Twitter + Reddit Systems

### Terminal 1: Twitter Automation
```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'
python3 auto_twitter_forever.py
```

### Terminal 2: Reddit Automation
```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'
python3 auto_reddit_scheduler.py
```

Both will run forever in parallel. Press Ctrl+C in each terminal to stop.

## 📈 Expected Results

### Week 1 (Cold Start)
- **Posts**: 1 per day = 7 total posts
- **Subreddits**: Rotating through r/Startups, r/ArtificialIntelligence, etc.
- **Engagement**: Expect low engagement initially (building trust)

### Week 2 (Growing)
- **Posts**: 1 per day = 7 total posts (14 cumulative)
- **Account Age**: 7-14 days (still "growing" phase)
- **Engagement**: Should start seeing upvotes and comments

### Week 3+ (Stable → Mature)
- **Posts**: 2-3 per day = 14-21 posts/week
- **Account Age**: 15+ days
- **Engagement**: Established presence, consistent visibility

### Month 2+ (Mature)
- **Posts**: Up to 4 per day = 28 posts/week
- **Account Age**: 30+ days
- **Engagement**: Strong reputation, may get featured/upvoted

## ⚠️ Important Warnings

### DO NOT:
- ❌ Manually increase posting limits (will get banned)
- ❌ Delete `reddit_account_state.json` (resets account age to 0)
- ❌ Post manually while automation is running (confuses tracking)
- ❌ Run multiple instances of scheduler (will exceed limits)

### DO:
- ✅ Let the system run autonomously
- ✅ Monitor first few posts to ensure quality
- ✅ Engage with comments on your posts (builds karma)
- ✅ Keep OpenAI API key valid (content generation requires it)

## 🎯 Success Metrics

Track your Reddit automation success:

```bash
# View total posts
python3 -c "import json; s=json.load(open('reddit_account_state.json')); print(f'Total posts: {s[\"total_posts\"]}')"

# View today's posts
python3 reddit_account_manager.py

# View all post history
python3 -c "import json; s=json.load(open('reddit_account_state.json')); [print(f'{p[\"timestamp\"]}: {p[\"title\"][:50]}... ({'✅' if p[\"success\"] else '❌'})') for p in s['posts_history']]"
```

## 🚀 Next Steps

1. ✅ Run authentication: `python3 reddit_login_and_save_auth.py`
2. ✅ Check account status: `python3 reddit_account_manager.py`
3. ✅ Start automation: `python3 auto_reddit_scheduler.py`
4. 📊 Monitor results on Reddit
5. 🎯 Engage with comments (build karma)
6. 📈 Watch your HireMeAI brand grow!

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the error messages (usually self-explanatory)
3. Try re-running authentication if login fails
4. Increase wait times if getting rate limited

---

**Built with**: Playwright + GPT-4o-mini + Smart Account Aging
**For**: HireMeAI (https://interviewasssistant.com)
**Strategy**: Build in Public on Reddit
