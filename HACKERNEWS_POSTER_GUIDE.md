# Hacker News 自动发帖系统 🚀

tbh 这个系统比评论系统更 hardcore，因为是主动发帖 lol

## 系统概述

**目标**: 在 HN 上 build in public，通过真诚的技术分享获得自然流量

**策略**:
- 每月 1 次 Show HN（产品展示）
- 每周 1 次 Ask HN（技术讨论）
- 语气轻松、真诚，多用网络用语（lol, tbh, ngl, imo）
- **关键**: 不推销产品，分享技术经验为主

**AI**: Claude (Anthropic) - 更适合技术社区

## 快速开始

### 1. 设置 API Key

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-vdOe-uCa...'
```

### 2. 登录 HN（一次性）

```bash
python3 hackernews_login_and_save_auth.py
```

### 3. 测试生成（不真实发布）

```bash
python3 hackernews_auto_poster.py --generate-only
```

这会生成当月的发帖计划到 `schedules/hackernews_posts_2025-10.json`

### 4. 启动自动发帖

```bash
python3 hackernews_auto_poster.py
```

## 核心文件

### 主要脚本
- `hackernews_auto_poster.py` - 主自动化脚本（永久运行）
- `src/hackernews_poster.py` - HN 发帖基础类
- `hackernews_login_and_save_auth.py` - 认证设置

### 数据文件
- `hackernews_auth.json` - 认证 cookies
- `schedules/hackernews_posts_{month}.json` - 每月发帖计划

## 发帖类型

### Show HN（每月1次）

**格式**:
```
标题: Show HN: Real-time AI interview coach (tbh the latency was a nightmare)
URL: https://interviewasssistant.com
正文: 2-4段技术分享
```

**Claude 生成的语气**:
- ✅ "ngl the hardest part was reducing first-byte latency"
- ✅ "tbh we tried everything before finding ChromaDB"
- ✅ "imo vector search is underrated for this use case"
- ❌ "Best interview tool ever! Try now!"

**示例内容** (Claude 会生成类似的):
```
Show HN: Real-time AI interview assistant (feedback welcome)

Been working on this for 4 months, tbh the latency was the biggest pain.

Current stack:
- Azure Speech SDK (streaming ASR)
- GPT-4o for responses
- ChromaDB for vector matching

The hardest part? Getting first-byte latency from 2.7s → 1.0s. We tried:
1. Dual-level caching (memory + disk)
2. Precomputing common answers
3. Vector similarity search (80% cache hit rate)

Still feels slow sometimes lol. Anyone hit sub-500ms with GPT-4?

Live demo: https://interviewasssistant.com

Would love feedback, esp on the UX!
```

### Ask HN（每周1次）

**格式**:
```
标题: Ask HN: How to reduce latency in real-time AI streaming?
正文: 技术问题 + 当前方案 + 具体指标 + 寻求建议
```

**示例内容** (Claude 会生成):
```
Ask HN: Best approach for real-time speaker diarization?

I'm building an interview assistant and need to distinguish between
interviewer/candidate audio in real-time.

Current approach:
- Picovoice Eagle (speaker recognition)
- 48kHz audio, 512-sample frames
- ~92% accuracy but occasional misses

Main issue: when voices overlap it gets confused lol. Tried:
- Increasing frame size → worse latency
- Lower threshold → more false positives

ngl I'm stuck. Anyone dealt with this in production? Is there a
better engine than Eagle for this use case?

Constraints:
- Real-time (< 100ms latency)
- On-device preferred (privacy)
- English + Chinese support

Any advice appreciated!
```

## 调度系统

### 月度计划

```json
{
  "month": "2025-10",
  "posts": [
    {
      "type": "Show HN",
      "scheduled_date": "2025-10-03",
      "scheduled_time": "10:27",
      "post_data": {
        "title": "Show HN: ...",
        "url": "https://interviewasssistant.com",
        "text": "..."
      },
      "posted": false
    },
    {
      "type": "Ask HN",
      "scheduled_date": "2025-10-08",
      "scheduled_time": "14:15",
      "post_data": {
        "title": "Ask HN: ...",
        "text": "..."
      },
      "posted": false
    }
  ]
}
```

### 时间分布

| 帖子类型 | 频率 | 时间选择 |
|---------|------|---------|
| Show HN | 每月1次 | 月初第1-7天，上午9-11点 |
| Ask HN | 每周1次 | 周二或周三，上午9点-下午4点 |

## HN 规范遵循

### ✅ 推荐做法

1. **真诚分享技术挑战**
   - "ngl the hardest part was..."
   - "tbh we tried everything..."
   - Share actual numbers/metrics

2. **轻松语气但有深度**
   - Use lol, tbh, ngl, imo naturally
   - But provide real technical value
   - Ask genuine questions

3. **产品提及自然**
   - Mention only when contextually relevant
   - Focus on technical challenges, not features
   - Link at end, not in title

### ❌ 禁忌行为

1. **营销语言**
   - ❌ "Best", "Revolutionary", "Game-changing"
   - ❌ "Try now", "Sign up", "Limited offer"
   - ❌ Feature list without context

2. **伪装讨论**
   - ❌ Ask HN 但实际是产品广告
   - ❌ 不分享具体技术细节
   - ❌ 不回应评论中的技术问题

3. **频率过高**
   - ❌ 每周多个 Show HN
   - ❌ 同一主题反复发帖
   - ❌ 不参与评论讨论

## Claude Prompt 策略

### Show HN Prompt 特点

```python
# 关键指令
"Sound like a technical founder sharing, not a marketer pitching"
"Use casual tech founder language (lol, tbh, ngl, imo)"
"Share 1-2 technical challenges with specific metrics"
"Ask for feedback genuinely"
```

### Ask HN Prompt 特点

```python
# 关键指令
"REAL technical question, not disguised marketing"
"Share specific numbers/metrics"
"Be humble and curious"
"DON'T pitch your product"
```

## 成本估算

```
Claude Sonnet 3.5 API:
- Show HN: ~800 tokens output → $0.012
- Ask HN: ~800 tokens output → $0.012

每月成本:
- 1 Show HN: $0.012
- 4 Ask HN: $0.048
Total: ~$0.06/月
```

超级便宜 lol

## 监控和维护

### 查看当月计划

```bash
cat schedules/hackernews_posts_2025-10.json | python3 -m json.tool
```

### 检查发布状态

```python
python3 -c "
import json
with open('schedules/hackernews_posts_2025-10.json') as f:
    data = json.load(f)

total = len(data['posts'])
posted = sum(1 for p in data['posts'] if p['posted'])
print(f'Progress: {posted}/{total} posts published')

for p in data['posts']:
    status = '✅' if p['posted'] else '⏳'
    print(f'{status} [{p[\"type\"]}] {p[\"scheduled_date\"]} - {p[\"post_data\"][\"title\"][:50]}...')
"
```

### 手动发布单个帖子

```python
python3 -c "
import sys
sys.path.insert(0, 'src')
from hackernews_poster import HackerNewsPoster

poster = HackerNewsPoster()
poster.setup_browser(headless=False)
poster.verify_login()

post_data = {
    'title': 'Ask HN: Your question here',
    'text': 'Your content here...'
}

poster.submit_post(post_data)
input('Press Enter to close...')
poster.close_browser()
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

### 问题3: 帖子被 flagged

**可能原因**:
1. 标题太推销化
2. 正文缺少技术细节
3. 没有参与评论讨论
4. 频率太高

**解决**:
- Review Claude 生成的内容
- 确保技术深度足够
- 积极回复评论
- 降低发帖频率

## 最佳实践

### 1. 发帖后必做

**立即**:
- 关注帖子评论（前30分钟最关键）
- 认真回复技术问题
- 分享更多细节和代码

**不要**:
- 发完就走
- 无视评论
- 只回复赞美，不回复质疑

### 2. 内容质量控制

**检查清单**:
- [ ] 标题有网络用语但不夸张
- [ ] 正文有具体数字/指标
- [ ] 分享了真实技术挑战
- [ ] 没有营销语言
- [ ] 真诚请教或分享

### 3. 社区互动

**每周**:
- 在其他 HN 帖子下评论 2-3 次
- 分享相关技术经验
- 建立社区存在感

## 进阶配置

### 修改发帖频率

编辑 `hackernews_auto_poster.py`:

```python
# 改为每月 2 个 Show HN
for month_week in [0, 2]:  # 第1周和第3周
    show_hn = self.generate_show_hn_post()
    # ...

# 改为每周 2 个 Ask HN
for week in range(4):
    for _ in range(2):  # 每周2次
        ask_hn = self.generate_ask_hn_post()
        # ...
```

### 自定义 Prompt 风格

```python
# 更轻松的语气
"Use VERY casual language (lots of lol, tbh, ngl)"

# 更专业的语气
"Professional but approachable tone"

# 更技术的深度
"Include code snippets and architecture diagrams"
```

## 与其他系统集成

### 配合评论系统

```bash
# 同时运行发帖和评论
tmux new-session -d -s hn-poster 'python3 hackernews_auto_poster.py'
tmux new-session -d -s hn-commenter 'python3 hackernews_auto_reply.py'

tmux ls
```

### 数据同步

```python
# 可以让发帖主题和评论主题保持一致
# 例如: Show HN 后的一周，Ask HN 围绕同一技术点
```

## 典型发帖案例

### Show HN - 产品展示

**好的例子**:
```
Show HN: Real-time AI interview coach (latency was a nightmare lol)

URL: https://interviewasssistant.com

Been hacking on this for 4mo, ngl the biggest challenge was latency.

Tech stack:
- Azure Speech SDK (streaming ASR, 48kHz)
- GPT-4o (response generation)
- ChromaDB (vector similarity search)
- SSE (client streaming)

Key optimization:
First-byte latency: 2.7s → 1.0s (60% improvement)
- Dual-level caching (memory + disk)
- Precompute common answers (80% hit rate)
- Vector matching instead of full GPT calls

Still feels slow tbh. Anyone hit sub-500ms with GPT-4?

Would love feedback on the UX! Demo linked above.
```

**为什么好**:
- ✅ 轻松语气（lol, ngl, tbh）
- ✅ 具体技术栈和指标
- ✅ 分享真实挑战
- ✅ 请教问题
- ✅ 产品链接自然放置

### Ask HN - 技术讨论

**好的例子**:
```
Ask HN: Best practices for real-time speaker diarization?

I'm building an interview assistant that needs to tell apart
interviewer/candidate voices in real-time.

Current setup:
- Picovoice Eagle (speaker recognition engine)
- 48kHz audio, 512-sample frames
- ~92% accuracy under ideal conditions

Main issue: overlapping speech. When both people talk at once,
accuracy drops to ~60%.

Tried:
- Bigger frames → worse latency (unacceptable)
- Lower threshold → too many false positives
- Noise gate → cuts off soft speakers

ngl I'm hitting a wall here. Is this just a fundamental limit
of real-time diarization? Or am I missing something?

Anyone dealt with this in production? Alternative engines?

Constraints:
- Real-time (<100ms latency)
- Privacy (on-device preferred)
- Bilingual (English + Chinese)

Any advice would be amazing!
```

**为什么好**:
- ✅ 真实技术问题
- ✅ 详细当前方案
- ✅ 具体指标和约束
- ✅ 分享尝试过的方法
- ✅ 真诚求助（ngl）
- ✅ 没有推销产品

## 总结

**系统特点**:
- ✅ 全自动生成和发布
- ✅ 使用 Claude (适合技术社区)
- ✅ 真诚语气，多网络用语
- ✅ 遵循 HN 规范
- ✅ 低成本（~$0.06/月）

**适用场景**:
- Build in Public 营销
- 技术品牌建设
- 吸引技术人才
- 获得技术反馈

**关键指标**:
- HN Karma 增长
- 帖子 upvote 数量
- 网站流量增加
- 评论互动质量

**下一步**:
1. 生成测试计划查看内容
2. 手动发布1-2个帖子测试反馈
3. 根据社区反应调整策略
4. 启动自动化系统

glhf! 🎉
