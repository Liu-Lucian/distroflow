# 发私信命令 - 所有平台

## 🚀 Reddit

```bash
# 登录
python3 reddit_login_and_save_auth.py

# 配置：编辑 run_reddit_campaign.py
# 修改 SUBREDDITS = ["startups", "entrepreneur"]

# 运行
export OPENAI_API_KEY='your_key'
python3 run_reddit_campaign.py
```

---

## 🚀 Twitter/X

```bash
# 登录
python3 twitter_login_and_save_auth.py

# 配置：编辑 run_twitter_campaign.py
# 修改 KEYWORDS = ["startup founder", "entrepreneur"]

# 运行
export OPENAI_API_KEY='your_key'
python3 run_twitter_campaign.py
```

---

## 🚀 Instagram (增强版 - 多轮循环)

```bash
# 登录
python3 instagram_login_and_save_auth.py

# 配置：编辑 run_instagram_campaign_optimized.py
# 修改 KEYWORDS = ["job interview tips", "career advice"]
# 修改 USERS_PER_ROUND = 100  # 每轮50-100个用户
# 修改 ENABLE_LOOP = True     # 启用多轮循环
# 修改 ROUND_DELAY_HOURS = (5, 8)  # 每轮休息5-8小时

# 运行（多轮循环模式）
export OPENAI_API_KEY='your_key'
python3 run_instagram_campaign_optimized.py

# 特点：
# ✅ 每轮自动找50-100个用户
# ✅ 完成后休息5-8小时
# ✅ 自动开始下一轮
# ✅ 循环往复，持续运行
# ✅ 按Ctrl+C随时停止
```

---

## 🚀 TikTok (增强版 - 多轮循环)

```bash
# 登录
python3 tiktok_login_and_save_auth.py

# 配置：编辑 run_tiktok_campaign_optimized.py
# 修改 KEYWORDS = ["startup", "entrepreneur"]
# 修改 USERS_PER_ROUND = 100  # 每轮50-100个用户
# 修改 ENABLE_LOOP = True     # 启用多轮循环
# 修改 ROUND_DELAY_HOURS = (5, 8)  # 每轮休息5-8小时

# 运行（多轮循环模式）
export OPENAI_API_KEY='your_key'
python3 run_tiktok_campaign_optimized.py

# 特点：
# ✅ 每轮自动找50-100个用户
# ✅ 完成后休息5-8小时
# ✅ 自动开始下一轮
# ✅ 循环往复，持续运行
# ✅ 按Ctrl+C随时停止
```

---

## 🚀 Facebook

```bash
# 登录
python3 facebook_login_and_save_auth.py

# 准备：在Facebook加入相关群组

# 测试群组（可选）
python3 test_facebook_url.py

# 配置：编辑 run_facebook_campaign.py
# 修改 GROUP_IDS = ["jobsearch", "careeradvice"]

# 运行
export OPENAI_API_KEY='your_key'
python3 run_facebook_campaign.py
```

---

## 🚀 LinkedIn

```bash
# 登录
python3 linkedin_login_and_save_auth.py

# 配置：编辑 run_linkedin_campaign.py
# 修改 KEYWORDS = ["startup founder", "entrepreneur"]

# 运行
export OPENAI_API_KEY='your_key'
python3 run_linkedin_campaign.py
```

---

## 🐙 GitHub (邮箱营销 - 多轮循环)

```bash
# 配置GitHub Token
# 编辑 platforms_auth.json，添加GitHub access_token

# 配置邮件系统
# 编辑 email_config.json

# 配置Hunter.io (可选但推荐)
export HUNTER_API_KEY='your_hunter_key'

# 配置：编辑 run_github_campaign.py
# 修改 SEARCH_STRATEGIES（关键词/topic/repository）
# 修改 USERS_PER_ROUND = 100
# 修改 ENABLE_LOOP = True
# 修改 EMAIL_BATCH_SIZE = 20

# 运行（多轮循环模式）
export OPENAI_API_KEY='your_key'
export HUNTER_API_KEY='your_hunter_key'
python3 run_github_campaign.py

# 特点：
# ✅ 搜索相关开发者（GitHub API）
# ✅ AI分析项目方向和价值
# ✅ 智能查找邮箱（GitHub + Hunter.io）
# ✅ AI生成个性化邮件
# ✅ 自动发送邮件（SMTP）
# ✅ 多轮循环（12-24小时间隔）
# ✅ 按Ctrl+C随时停止
```

---

## 📋 总结

| 平台 | 登录命令 | 运行命令 |
|------|----------|----------|
| Reddit | `python3 reddit_login_and_save_auth.py` | `python3 run_reddit_campaign.py` |
| Twitter | `python3 twitter_login_and_save_auth.py` | `python3 run_twitter_campaign.py` |
| Instagram | `python3 instagram_login_and_save_auth.py` | `python3 run_instagram_campaign_optimized.py` |
| TikTok | `python3 tiktok_login_and_save_auth.py` | `python3 run_tiktok_campaign_optimized.py` |
| Facebook | `python3 facebook_login_and_save_auth.py` | `python3 run_facebook_campaign.py` |
| LinkedIn | `python3 linkedin_login_and_save_auth.py` | `python3 run_linkedin_campaign.py` |

---

## ⚡ 快速开始模板

```bash
# 1. 登录（一次性）
python3 {platform}_login_and_save_auth.py

# 2. 配置（编辑对应的 run_*_campaign.py 文件）
nano run_{platform}_campaign.py

# 3. 运行
export OPENAI_API_KEY='your_key'
python3 run_{platform}_campaign.py
```

替换 `{platform}` 为：`reddit`、`twitter`、`instagram`、`tiktok`、`facebook`、`linkedin`
