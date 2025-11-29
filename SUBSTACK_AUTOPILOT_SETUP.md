# Substack Autopilot - 永久运行设置指南

## 系统概览

**Substack Autopilot** 整合了发布系统和养号系统，实现完全自动化的Substack增长。

### 两大系统协同工作

1. **发布系统** (`schedule_substack_posts.py`)
   - 生成AI文章
   - 设置定时发布（每隔几天自动发布）
   - 一次性设置，自动执行

2. **养号系统** (`substack_comment_farmer.py`)
   - 自动发现相关文章
   - AI生成有价值的评论
   - 建立账号信誉度

3. **自动驾驶** (`substack_autopilot.py`)
   - 协调两个系统
   - 每天自动运行养号系统
   - 监控每日限额
   - 持续不断运行

## 快速开始

### 方法1: 手动运行（测试用）

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'

# 运行一次
python3 substack_autopilot.py

# 持续运行（需要保持终端开启）
python3 substack_autopilot.py --continuous
```

### 方法2: 使用cron（简单后台运行）

每天自动运行3次（早上9点、下午2点、晚上8点）：

```bash
# 编辑crontab
crontab -e

# 添加以下行（全部复制）
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY_HERE

# 早上9点
0 9 * * * cd "/Users/l.u.c/my-app/MarketingMind AI" && /usr/local/bin/python3 substack_autopilot.py >> /tmp/substack_autopilot.log 2>&1

# 下午2点
0 14 * * * cd "/Users/l.u.c/my-app/MarketingMind AI" && /usr/local/bin/python3 substack_autopilot.py >> /tmp/substack_autopilot.log 2>&1

# 晚上8点
0 20 * * * cd "/Users/l.u.c/my-app/MarketingMind AI" && /usr/local/bin/python3 substack_autopilot.py >> /tmp/substack_autopilot.log 2>&1
```

**查看日志：**
```bash
tail -f /tmp/substack_autopilot.log
```

### 方法3: 使用launchd（macOS推荐，永久后台运行）

最稳定的方式，即使重启也会自动运行。

#### 步骤1: 创建launchd配置文件

```bash
nano ~/Library/LaunchAgents/com.substack.autopilot.plist
```

粘贴以下内容（**注意修改你的API key**）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.substack.autopilot</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/l.u.c/my-app/MarketingMind AI/substack_autopilot.py</string>
        <string>--once</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/l.u.c/my-app/MarketingMind AI</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>OPENAI_API_KEY</key>
        <string>sk-proj-YOUR_OPENAI_API_KEY_HERE</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>9</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>14</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
        <dict>
            <key>Hour</key>
            <integer>20</integer>
            <key>Minute</key>
            <integer>0</integer>
        </dict>
    </array>

    <key>StandardOutPath</key>
    <string>/tmp/substack_autopilot.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/substack_autopilot_error.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

#### 步骤2: 加载并启动服务

```bash
# 加载服务
launchctl load ~/Library/LaunchAgents/com.substack.autopilot.plist

# 验证服务已加载
launchctl list | grep substack

# 立即测试运行一次（可选）
launchctl start com.substack.autopilot
```

#### 步骤3: 管理服务

```bash
# 查看日志
tail -f /tmp/substack_autopilot.log
tail -f /tmp/substack_autopilot_error.log

# 停止服务
launchctl stop com.substack.autopilot

# 卸载服务
launchctl unload ~/Library/LaunchAgents/com.substack.autopilot.plist

# 重新加载（修改配置后）
launchctl unload ~/Library/LaunchAgents/com.substack.autopilot.plist
launchctl load ~/Library/LaunchAgents/com.substack.autopilot.plist
```

## 完整工作流程

### 初始设置（一次性）

1. **设置定时发布文章**（一次性，会自动发布）
   ```bash
   python3 schedule_substack_posts.py
   ```
   这会安排4篇文章在未来几天自动发布。

2. **启动自动驾驶系统**（永久运行）
   - 使用上面的launchd或cron方法
   - 系统会每天自动评论3次

### 日常运行

**完全自动化！** 不需要任何手动操作。

- **发布系统**: 已设置的文章会在指定时间自动发布
- **养号系统**: 每天早中晚自动评论
- **监控**: 查看日志文件了解运行状态

### 定期维护（每周一次）

```bash
# 1. 查看本周统计
python3 -c "import json; h=json.load(open('substack_commented_posts.json')); print(f'Total comments: {len(h)}')"

# 2. 安排下周的文章发布
python3 schedule_substack_posts.py

# 3. 查看日志确保一切正常
tail -100 /tmp/substack_autopilot.log
```

## 配置调整

### 调整评论频率

编辑 `substack_autopilot.py`:

```python
CONFIG = {
    "comment_runs_per_day": 3,  # 改为2或4
    "comment_run_times": ["09:00", "14:00", "20:00"],  # 修改时间
    "max_comments_per_day": 15,  # 增加或减少每日限额
}
```

### 调整每次评论数量

编辑 `substack_comment_farmer.py`:

```python
COMMENTS_PER_RUN = 3  # 改为2-5之间
```

### 调整评论间隔

编辑 `substack_comment_farmer.py`:

```python
DELAY_BETWEEN_COMMENTS = (180, 300)  # 改为(120, 240) 更快，或(300, 600) 更慢
```

### 调整发布时间表

编辑 `schedule_substack_posts.py`:

```python
PUBLISH_SCHEDULE = [
    {"days_from_now": 3, "title_prefix": "Week 6"},
    {"days_from_now": 6, "title_prefix": "Week 7"},
    # 添加更多...
]

PUBLISH_TIME = "09:00"  # 改为其他时间
```

## 监控和调试

### 查看实时日志

```bash
# Autopilot日志
tail -f /tmp/substack_autopilot.log

# 错误日志
tail -f /tmp/substack_autopilot_error.log
```

### 检查评论历史

```bash
# 查看所有评论
cat substack_commented_posts.json | python3 -m json.tool

# 统计评论数
python3 -c "import json; print(len(json.load(open('substack_commented_posts.json'))))"

# 查看今天的评论
python3 -c "
import json
from datetime import datetime
h = json.load(open('substack_commented_posts.json'))
today = datetime.now().date()
today_comments = [p for p in h if datetime.fromisoformat(p['commented_at']).date() == today]
print(f'Today: {len(today_comments)} comments')
for c in today_comments:
    print(f'  - {c[\"title\"]}')
"
```

### 测试系统运行

```bash
# 测试一次运行（不会重复评论）
python3 substack_autopilot.py --once

# 查看会生成什么评论（不实际发送）
python3 -c "
from substack_comment_farmer import generate_comment
article = {
    'title': 'Test Article',
    'content': 'This is a test article about AI and startups...'
}
print(generate_comment(article))
"
```

## 成本估算

### 每日运行成本

- **3次评论运行/天** × **3条评论/次** = 9条评论/天
- **成本**: ~$0.018/天 (~$0.54/月)
- **发布系统**: 一次性生成4篇文章 ~$0.004

**月度总成本**: < $1美元 💰

### 预期效果

**第1个月:**
- ~270条评论
- 4-8篇定时发布文章
- 预计新增followers: 30-60

**第2-3个月:**
- ~270条评论/月
- 8-12篇文章/月
- 预计新增followers: 60-120/月
- 复合增长开始显现

## 安全注意事项

### 账号安全

1. **使用专用账号** - 不要用个人主账号
2. **监控平台警告** - 检查Substack是否发送警告邮件
3. **调整频率** - 如果遇到限制，降低评论频率
4. **保持真实** - AI生成的评论应该有价值，不要spam

### 认证管理

```bash
# 定期更新cookies（如果登录过期）
# 检查substack_auth.json是否仍然有效

# 如果需要重新登录，删除现有auth并重新运行login脚本
rm substack_auth.json
# 然后手动登录保存cookies
```

### 备份

```bash
# 定期备份评论历史
cp substack_commented_posts.json substack_commented_posts_backup_$(date +%Y%m%d).json

# 备份配置
cp substack_autopilot.py substack_autopilot_backup.py
```

## 故障排除

### 问题: launchd服务不运行

```bash
# 检查服务状态
launchctl list | grep substack

# 查看错误日志
cat /tmp/substack_autopilot_error.log

# 验证Python路径
which python3

# 验证文件路径
ls -la "/Users/l.u.c/my-app/MarketingMind AI/substack_autopilot.py"
```

### 问题: API key错误

```bash
# 验证环境变量
echo $OPENAI_API_KEY

# 测试API
python3 -c "from openai import OpenAI; client = OpenAI(); print('API OK')"
```

### 问题: 没有找到可评论的文章

- 很多Substack文章需要付费订阅才能评论
- 系统会自动跳过这些文章
- 如果连续多次都是付费文章，考虑手动选择一些免费的Substack关注

### 问题: Cookies过期

```bash
# 症状: 无法登录Substack

# 解决: 使用浏览器手动登录，重新保存cookies
# 1. 打开Chrome
# 2. 登录Substack
# 3. F12 → Application → Cookies → 复制所有cookies
# 4. 更新substack_auth.json
```

## 高级配置

### 针对特定Substack评论

编辑 `substack_comment_farmer.py` 中的 `find_relevant_posts()` 函数：

```python
# 替换Discover页面为特定Substack的archive
target_substacks = [
    "https://newsletter1.substack.com/archive",
    "https://newsletter2.substack.com/archive",
]
```

### 自定义AI评论风格

编辑 `substack_comment_farmer.py` 中的 `generate_comment()` 函数的prompt部分。

### 调整为每小时运行（激进模式）

**警告**: 可能被检测为bot

```xml
<!-- 在launchd plist中使用StartInterval -->
<key>StartInterval</key>
<integer>3600</integer>  <!-- 每小时 -->
```

## 总结

### 三个核心脚本

1. **`schedule_substack_posts.py`** - 一次性运行，设置未来几周的文章发布
2. **`substack_comment_farmer.py`** - 单次评论任务（3条评论）
3. **`substack_autopilot.py`** - 协调器，每天自动运行养号系统

### 推荐设置

- **使用launchd** 作为后台服务（macOS）
- **每天3次** 评论（早中晚）
- **每次3-5条** 评论
- **每周安排4-8篇** 定时发布文章

### 成功的关键

✅ 保持系统持续运行
✅ 定期检查日志
✅ 每周安排新的文章发布
✅ 监控账号健康状态
✅ 评论质量 > 数量

现在你拥有了一个**永不停息的Substack增长引擎**！🚀
