# HN 自动化大师使用指南

一个命令搞定 Hacker News 的所有自动化：发帖 + 评论。

## 快速开始

### 1. 初次设置（一次性）

```bash
# 1.1 设置 API Key
export ANTHROPIC_API_KEY='sk-ant-YOUR_ANTHROPIC_API_KEY_HERE'

# 1.2 登录 HN 并保存 cookies（一次性）
python3 hackernews_login_and_save_auth.py
```

### 2. 运行自动化

```bash
# 单次运行（推荐先测试）
python3 hackernews_master.py --once

# 永久运行（后台持续运行）
python3 hackernews_master.py --forever

# 查看当前状态
python3 hackernews_master.py --status
```

## 工作原理

### 自动发帖（Posting）

**频率：** 每月 5 篇
- 1 篇 Show HN（产品展示）
- 4 篇 Ask HN（技术讨论）

**时间窗口：** 工作日 09:00-12:00, 14:00-17:00

**策略：**
1. 每月初自动生成本月发帖计划
2. 按计划在指定日期发布
3. 内容由 Claude API 生成，确保：
   - 语气自然、技术化（lol, tbh, ngl 等网络用语）
   - 分享真实的技术挑战，不是营销
   - 符合 HN 社区规范

### 自动评论（Commenting）

**频率：** 每天 2-3 条

**时间窗口：**
- 上午 09:00-11:00
- 下午 14:00-16:00
- 晚上 19:00-21:00

**策略：**
1. 从 HN 首页获取 30 个热门帖子
2. 智能选择值得评论的帖子：
   - 技术相关（AI, API, 架构, 性能等）
   - 有一定讨论但不太热（10-200 评论）
   - 分数适中（50-500 分）
3. 使用 Claude 生成高质量技术评论：
   - 分享真实经验和具体数字
   - 提供有价值的建议
   - 自然提及产品（仅在相关时）

### 频率控制

系统会智能控制频率，避免被 HN 检测为机器人：

- ✅ 随机时间偏移（±30分钟）
- ✅ 随机决策（不是每次检查都执行）
- ✅ 严格的每日/每月限额
- ✅ 只在合适的时间窗口内活动

## 使用场景

### 场景 1: 单次测试

```bash
# 运行一次，看看会做什么
python3 hackernews_master.py --once
```

**输出示例：**
```
🤖 HN 自动化大师 - 单次运行
================================================================================
时间: 2025-10-23 14:30:00
模式: 发帖+评论
================================================================================

📊 当前状态:
   本月发帖: 1 / 5
   今日评论: 2 / 3
   总发帖数: 12
   总评论数: 85

⏸️  当前时间 (14:00) 在评论窗口内
✅ 决定现在评论

================================================================================
💬 执行评论任务
================================================================================
📰 获取 HN 首页帖子...
   ✅ 获取到 30 个帖子
📊 从 30 个帖子中选择 1 个...
   ✅ 已选择 1 个帖子:
      1. Ask HN: Best practices for real-time WebSockets? (👍 127, 💬 45)

🤖 使用 Claude 生成评论...
   ✅ 生成成功 (142 字符)
   预览: We hit this exact issue when building real-time feedback for interviews...

💬 发布评论...
   ✅ 评论成功！

✅ 本次运行完成，执行了: 评论
```

### 场景 2: 永久后台运行

```bash
# 启动后台任务（推荐使用 screen 或 tmux）
screen -S hackernews
python3 hackernews_master.py --forever

# 分离会话: Ctrl+A, D
# 重新连接: screen -r hackernews
```

### 场景 3: 仅发帖（不评论）

```bash
# 适合只想偶尔发帖的场景
python3 hackernews_master.py --once --post-only
```

### 场景 4: 仅评论（不发帖）

```bash
# 适合只想增加社区参与度
python3 hackernews_master.py --once --comment-only
```

## 文件结构

```
MarketingMind AI/
├── hackernews_master.py              # 🎯 主控制器（新）
├── hackernews_auto_poster.py         # 发帖子系统
├── hackernews_auto_reply.py          # 评论系统
├── hackernews_master_state.json      # 运行状态（自动生成）
│
├── src/
│   ├── hackernews_poster.py          # 发帖基础设施
│   └── hackernews_commenter.py       # 评论基础设施
│
├── schedules/                         # 计划存储
│   ├── hackernews_posts_2025-10.json    # 本月发帖计划
│   └── hackernews_schedule_2025-10-23.json  # 今日评论计划
│
└── hackernews_auth.json              # 登录凭证（一次性设置）
```

## 配置调整

如果想调整频率，编辑 `hackernews_master.py` 中的 `SCHEDULE_CONFIG`:

```python
SCHEDULE_CONFIG = {
    # 发帖频率
    'posts_per_month': {
        'show_hn': 1,   # 每月1次 Show HN
        'ask_hn': 4     # 每月4次 Ask HN
    },

    # 评论频率
    'comments_per_day': {
        'min': 2,       # 每天至少2条
        'max': 3        # 每天最多3条
    },

    # 检查间隔（小时）
    'check_interval_hours': 2  # 每2小时检查一次
}
```

## 监控与日志

### 查看状态

```bash
python3 hackernews_master.py --status
```

### 查看日志

```bash
# 实时查看日志
tail -f hackernews_master.log

# 查看最近50行
tail -50 hackernews_master.log
```

### 查看计划

```bash
# 查看本月发帖计划
cat schedules/hackernews_posts_2025-10.json | python3 -m json.tool

# 查看今日评论计划
cat schedules/hackernews_schedule_2025-10-23.json | python3 -m json.tool
```

## 常见问题

### Q: 登录 Cookie 过期了怎么办？

```bash
# 重新登录
python3 hackernews_login_and_save_auth.py
```

### Q: 如何暂停自动化？

```bash
# 如果是 --forever 模式，直接 Ctrl+C 中断
# 如果是 cron job，注释掉 crontab 条目
```

### Q: 评论/发帖太频繁会被封吗？

不会。系统已内置严格的频率控制：
- 每天最多 3 条评论
- 每月最多 5 篇帖子
- 随机时间偏移
- 只在合理的时间窗口内活动

这个频率远低于 HN 的限制。

### Q: 生成的内容质量如何？

内容由 Claude API 生成，经过精心设计的提示词：
- ✅ 技术深度高，分享真实经验
- ✅ 语气自然，使用网络用语（lol, tbh）
- ✅ 符合 HN 社区规范
- ✅ 避免营销语言

可以先用 `--once` 模式测试，查看生成的内容。

### Q: 成本是多少？

极低：
- **发帖**：每月 5 次 × $0.002 = $0.01/月
- **评论**：每天 3 次 × 30 天 × $0.001 = $0.09/月
- **总计**：~$0.10/月

基本可以忽略不计。

## 最佳实践

1. **先测试后运行**
   ```bash
   # 先单次运行几天，观察效果
   python3 hackernews_master.py --once
   ```

2. **使用 screen/tmux 后台运行**
   ```bash
   screen -S hn
   python3 hackernews_master.py --forever
   ```

3. **定期检查日志**
   ```bash
   tail -f hackernews_master.log
   ```

4. **手动审核重要帖子**
   - Show HN 帖子建议先生成，手动审核后再发布
   - Ask HN 和评论可以自动化

5. **保持 Cookie 新鲜**
   - 每月至少手动登录一次 HN
   - 如果发现登录失效，重新运行 `hackernews_login_and_save_auth.py`

## 下一步

1. ✅ **测试单次运行**：`python3 hackernews_master.py --once`
2. ✅ **查看生成的内容**：检查 `schedules/` 目录
3. ✅ **设置后台运行**：使用 screen 或 cron job
4. ✅ **监控效果**：定期查看日志和 HN 个人主页

**享受自动化带来的轻松！** 🚀
