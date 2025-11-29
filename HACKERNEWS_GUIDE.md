# Hacker News 自动回答系统

基于 Claude API (Anthropic) 的 Hacker News 技术评论自动化系统。

## 系统概述

**目标**: 在 Hacker News 上建立技术影响力，为 HireMeAI (即答侠) 带来自然流量

**策略**:
- 每天 2-3 条高质量技术评论
- 使用 Claude (Anthropic) 生成偏技术的深度内容
- 自然提及产品，不做硬广
- 遵循 HN 社区规范

**架构**: 参考 `auto_twitter_forever.py` 的调度系统

## 核心文件

### 主要脚本
- `hackernews_auto_reply.py` - 主自动化脚本（永久运行模式）
- `hackernews_login_and_save_auth.py` - 一次性登录认证
- `test_hackernews_setup.py` - 测试系统配置

### 基础设施
- `src/hackernews_commenter.py` - HN 评论基础类（Playwright）
- `hackernews_auth.json` - 保存的认证 cookies
- `schedules/hackernews_schedule_{date}.json` - 每日评论计划

## 快速开始

### 1. 安装依赖

```bash
pip install anthropic playwright
playwright install chromium
```

### 2. 设置 API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-YOUR_ANTHROPIC_API_KEY_HERE'
```

或者添加到 `~/.zshrc`:

```bash
echo "export ANTHROPIC_API_KEY='sk-ant-api03-...'" >> ~/.zshrc
source ~/.zshrc
```

### 3. 登录 Hacker News（一次性）

```bash
python3 hackernews_login_and_save_auth.py
```

步骤：
1. 脚本会打开浏览器到 HN 登录页面
2. 手动输入用户名和密码
3. 点击 login
4. 回到终端按 Enter
5. cookies 会自动保存到 `hackernews_auth.json`

### 4. 测试配置

```bash
python3 test_hackernews_setup.py
```

会验证：
- ✅ Anthropic API key 是否设置
- ✅ Claude API 是否可用
- ✅ HN 登录是否有效
- ✅ 能否获取首页帖子

### 5. 启动自动化系统

```bash
python3 hackernews_auto_reply.py
```

## 工作流程

### 每日流程

1. **09:00** - 系统启动 / 加载今日计划
2. **09:00-11:00** - 发布第1条评论（随机时间）
3. **14:00-16:00** - 发布第2条评论（随机时间）
4. **19:00-21:00** - 发布第3条评论（随机时间）
5. **00:00** - 第二天计划生成
6. **重复**

### 单次评论流程

```
获取 HN 首页帖子（30个）
    ↓
智能选择目标帖子（3个）
- 10-500 分的帖子（不太新，不太老）
- 有评论但不太多（1-200条）
- 优先技术相关帖子
    ↓
使用 Claude 生成评论
- 技术深度 + 具体数据
- 自然提及 HireMeAI（如果相关）
- 遵循 HN 规范
    ↓
模拟人类发布评论
- 真人打字速度（20-60ms/字符）
- 随机延迟 3-8 分钟
    ↓
保存状态到 JSON
```

## 文件结构

```
MarketingMind AI/
├── hackernews_auto_reply.py          # 主脚本（永久运行）
├── hackernews_login_and_save_auth.py # 登录脚本（一次性）
├── test_hackernews_setup.py          # 测试脚本
├── hackernews_auth.json              # 认证 cookies
├── src/
│   └── hackernews_commenter.py       # 评论基础类
└── schedules/
    └── hackernews_schedule_2025-10-23.json  # 每日计划
```

## 评论生成策略

### Claude Prompt 设计

**核心要求**:
1. **技术深度** - 分享具体经验、代码细节、架构决策
2. **具体性** - 包含真实数字、指标、技术细节
3. **增加价值** - 帮助其他开发者
4. **自然提及** - 仅在相关时提及 HireMeAI
5. **对话感** - 像真实工程师，不像营销人员

**示例好评论**:
```
We hit this exact issue when building real-time feedback for interviews.
The key was switching from REST polling (200ms latency) to WebSockets
with delta updates. Reduced bandwidth by 80% and made the UX feel instant.

The tricky part was handling reconnections gracefully - we ended up using
a sliding window buffer. Have you considered QUIC for the transport layer?
```

**示例坏评论**（不会生成）:
```
❌ "Great post! Check out HireMeAI if you need interview help!"
❌ "Thanks for sharing! Very relevant."
```

## 帖子选择算法

### 过滤条件

```python
# 跳过的帖子
- 没有评论的帖子（0 comments）
- 评论太多的帖子（> 200 comments）
- 分数太低的帖子（< 10 points）
- 分数太高的超热帖（> 500 points）

# 优先的帖子
- 包含技术关键词（api, framework, ai, ml, startup, interview 等）
- 10-500 分之间（已有热度但还在增长）
- 1-200 条评论（有讨论但不太拥挤）
```

### 排序策略

```python
# 排序公式: comments / (points + 10)
# 目标：找到"讨论热度相对较高"的帖子
# 这些帖子更可能给评论带来可见性
```

## 调度系统

### 时间段设计

| 时间段 | 用途 | 说明 |
|--------|------|------|
| 09:00-11:00 | 早间评论 | 美国西海岸夜间，欧洲下午 |
| 14:00-16:00 | 下午评论 | 美国东海岸早晨，欧洲晚上 |
| 19:00-21:00 | 晚间评论 | 美国东海岸下午，欧洲深夜 |

### 随机化策略

```python
# 每个时间段内随机选择具体时间
# 例如: 09:00-11:00 → 09:37 (随机)

random_hour = random.randint(start_hour, end_hour - 1)
random_minute = random.randint(0, 59)

# 评论之间随机延迟 3-8 分钟
delay = random.randint(180, 480)
```

## 数据持久化

### 每日计划文件

```json
{
  "generated_at": "2025-10-23T09:00:00",
  "date": "2025-10-23",
  "schedule": [
    {
      "time_slot": "09:00-11:00",
      "scheduled_time": "09:37",
      "story": {
        "id": "42048392",
        "title": "Show HN: AI Interview Assistant...",
        "url": "https://news.ycombinator.com/item?id=42048392",
        "points": 127,
        "comments": 43
      },
      "comment": "We faced similar challenges...",
      "posted": true
    }
  ]
}
```

## 安全性和反检测

### 人类行为模拟

```python
# 真人打字速度
for char in comment_text:
    self.page.keyboard.type(char, delay=random.randint(20, 60))  # 20-60ms

# 段落间换行
self.page.keyboard.press('Enter')
self.page.keyboard.press('Enter')

# 随机延迟
time.sleep(random.randint(3*60, 8*60))  # 3-8 分钟
```

### 账号安全

- 使用 cookie-based 认证（不暴露密码）
- 每天仅 2-3 条评论（避免垃圾邮件检测）
- 高质量内容（真实技术讨论）
- 随机时间分布（不规律模式）

## 监控和维护

### 检查日志

```bash
# 查看实时日志
python3 hackernews_auto_reply.py

# 输出示例
2025-10-23 09:37:15 - INFO - ⏰ 时间到: 09:37
2025-10-23 09:37:15 - INFO - 📝 准备评论: Show HN: AI Interview Assistant...
2025-10-23 09:37:45 - INFO -    ✅ 评论发布成功!
2025-10-23 09:37:45 - INFO -    ⏳ 等待 5 分钟后继续...
```

### 查看每日计划

```bash
cat schedules/hackernews_schedule_2025-10-23.json | python3 -m json.tool
```

### 检查发布状态

```bash
# 查看今日计划中的发布状态
python3 -c "
import json
with open('schedules/hackernews_schedule_2025-10-23.json') as f:
    data = json.load(f)

total = len(data['schedule'])
posted = sum(1 for item in data['schedule'] if item['posted'])
print(f'进度: {posted}/{total} 条评论已发布')
"
```

## 故障排查

### 问题1: API key 无效

```bash
# 症状
❌ 错误: 未设置 ANTHROPIC_API_KEY

# 解决
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

### 问题2: HN 登录失效

```bash
# 症状
❌ HN 登录验证失败

# 解决
python3 hackernews_login_and_save_auth.py  # 重新登录
```

### 问题3: 找不到评论输入框

```bash
# 症状
❌ 找不到评论输入框

# 可能原因
1. HN 页面结构变化
2. 需要登录才能评论
3. 帖子已关闭评论

# 调试
# 修改 hackernews_commenter.py 中的 setup_browser()
self.commenter.setup_browser(headless=False)  # 改为可见模式
```

### 问题4: Claude API 超时

```bash
# 症状
❌ Claude API 调用失败: timeout

# 解决
1. 检查网络连接
2. 增加 timeout 参数
3. 重试机制（自动处理）
```

## 最佳实践

### 1. 评论质量控制

**遵循 HN 规范**:
- ✅ 技术深度和具体性
- ✅ 提供真实价值
- ✅ 参与真实讨论
- ❌ 营销语言
- ❌ 自我推广
- ❌ 通用赞美

### 2. 频率控制

```python
# 建议配置
COMMENTS_PER_DAY = 2-3  # 每天2-3条
MIN_DELAY_MINUTES = 180  # 评论间隔至少3分钟
MAX_DELAY_MINUTES = 480  # 最多8分钟

# 避免
COMMENTS_PER_DAY = 10+  # 太多，会被标记为垃圾
MIN_DELAY_MINUTES = 0   # 太快，不自然
```

### 3. 内容多样性

**自动生成的评论应该包含**:
- 技术细节和数据
- 真实经验分享
- 问题和讨论
- 偶尔的产品提及（仅在相关时）

**避免**:
- 每条评论都提到产品
- 使用相同的句式
- 重复的技术细节

### 4. 账号维护

```bash
# 定期检查账号状态
# 访问: https://news.ycombinator.com/user?id=你的用户名

# 检查项目
- Karma 分数是否正常增长
- 是否有被 downvote 的评论
- 是否收到社区警告
```

## HN 算法优化

### 冷启动期（最重要）

```
前 30-60 分钟决定帖子能否上首页
    ↓
策略: 在帖子发布后 5-15 分钟内评论
    ↓
选择: 刚发布的 Show HN / Ask HN
```

### 评论可见性

```python
# 评论排序算法（简化版）
comment_score = upvotes - downvotes - age_penalty

# 策略
1. 早期评论（age_penalty 小）
2. 高质量内容（upvotes 高）
3. 避免争议（downvotes 少）
```

## 成本估算

### API 成本

```
Claude Sonnet 3.5:
- Input: $3 / 1M tokens
- Output: $15 / 1M tokens

每条评论估算:
- Input: ~500 tokens (prompt + context)
- Output: ~150 tokens (评论内容)

成本: ~$0.003 / 评论

每日成本: $0.003 × 3 = ~$0.01
每月成本: ~$0.30
```

**对比 OpenAI GPT-4**:
- GPT-4: ~$0.06 / 评论 → $5.40 / 月
- Claude: ~$0.003 / 评论 → $0.30 / 月
- **节省 94%**

## 进阶配置

### 修改评论频率

编辑 `hackernews_auto_reply.py`:

```python
# 改为每天4条评论
selected_stories = self.select_stories_to_comment(stories, count=4)

# 增加时间段
time_slots = [
    ("09:00-11:00", 9, 11),
    ("12:00-14:00", 12, 14),  # 新增
    ("15:00-17:00", 15, 17),
    ("19:00-21:00", 19, 21),
]
```

### 修改选择策略

```python
# 更激进（选择更热门的帖子）
if points > 100 and comments < 300:
    filtered.append(story)

# 更保守（选择更冷门的帖子）
if 5 < points < 100 and comments < 50:
    filtered.append(story)
```

### 自定义 Prompt

编辑 `hackernews_auto_reply.py` 中的 `generate_technical_comment()`:

```python
prompt = f"""You are the technical founder of HireMeAI...

[修改这里的 prompt 来调整生成风格]

例如:
- 更技术: "Focus on low-level implementation details"
- 更产品: "Mention product context more naturally"
- 更学术: "Reference papers and research"
"""
```

## 与其他系统集成

### 配合 Twitter 系统

```bash
# 同时运行多个 Build in Public 系统
tmux new-session -d -s hn 'python3 hackernews_auto_reply.py'
tmux new-session -d -s twitter 'python3 auto_twitter_forever.py'
tmux new-session -d -s reddit 'python3 reddit_karma_farmer.py'

# 查看会话
tmux ls

# 进入会话
tmux attach -t hn
```

### 数据同步

```python
# 可以让 HN 评论和 Twitter 推文主题保持一致
# 例如: 如果今天 Twitter 发了关于 WebSocket 的内容
# 可以在 HN 上也寻找相关帖子评论
```

## 总结

**系统特点**:
- ✅ 完全自动化（永久运行）
- ✅ 使用 Claude (更适合技术社区)
- ✅ 低成本（~$0.30/月）
- ✅ 高质量评论（技术深度）
- ✅ 遵循 HN 规范

**使用场景**:
- Build in Public 营销
- 技术品牌建设
- 自然流量获取
- 社区影响力积累

**关键指标**:
- Karma 分数增长
- 评论 upvote 数量
- 网站流量增加
- 用户提及次数

**下一步**:
1. 运行测试验证配置
2. 启动系统观察一周
3. 根据社区反馈调整策略
4. 监控 Karma 和流量
