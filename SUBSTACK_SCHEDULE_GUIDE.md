# Substack定时发布指南

## 功能

自动生成文章并设置定时发布，避免一次性发布太多文章。

## 使用方法

### 1. 直接运行（使用默认时间表）

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
export OPENAI_API_KEY='sk-proj-YOUR_OPENAI_API_KEY_HERE'
python3 schedule_substack_posts.py
```

### 2. 自定义发布时间表

编辑 `schedule_substack_posts.py` 文件，修改这两个配置：

```python
# 发布时间表（可以自定义）
PUBLISH_SCHEDULE = [
    {"days_from_now": 3, "title_prefix": "Week 6"},   # 3天后
    {"days_from_now": 6, "title_prefix": "Week 7"},   # 6天后
    {"days_from_now": 9, "title_prefix": "Week 8"},   # 9天后
    {"days_from_now": 12, "title_prefix": "Week 9"},  # 12天后
]

# 发布时间（早上9点）
PUBLISH_TIME = "09:00"  # 可以改成其他时间，如 "14:00" 下午2点
```

## 默认设置

当前默认设置会安排4篇文章：

1. **Week 6** - 3天后的早上9:00发布
2. **Week 7** - 6天后的早上9:00发布
3. **Week 8** - 9天后的早上9:00发布
4. **Week 9** - 12天后的早上9:00发布

## 工作流程

脚本会自动：

1. ✅ 使用AI生成文章内容（标题、副标题、正文）
2. ✅ 登录Substack
3. ✅ 创建新文章
4. ✅ 填写内容
5. ✅ 设置定时发布时间
6. ✅ 点击"Schedule"按钮

全程自动化，无需手动操作！

## 修改时间间隔

如果你想每5天发一篇，可以这样修改：

```python
PUBLISH_SCHEDULE = [
    {"days_from_now": 5, "title_prefix": "Week 6"},
    {"days_from_now": 10, "title_prefix": "Week 7"},
    {"days_from_now": 15, "title_prefix": "Week 8"},
    {"days_from_now": 20, "title_prefix": "Week 9"},
]
```

## 修改发布时间

如果你想下午2点发布：

```python
PUBLISH_TIME = "14:00"
```

如果你想晚上8点发布：

```python
PUBLISH_TIME = "20:00"
```

## 查看定时文章

运行完脚本后，登录Substack后台，你可以在 **Scheduled** 标签页看到所有定时发布的文章。

## 注意事项

1. **时间准确性** - 脚本会自动计算准确的发布时间（从当前时间开始计算）
2. **时区** - 使用你本地的时区
3. **检查截图** - 脚本会生成截图文件，可以查看：
   - `schedule_post_dialog.png` - 发布对话框
   - `schedule_post_set.png` - 设置时间后的状态
   - `schedule_post_final.png` - 最终确认

## 取消或修改定时文章

如果需要修改或取消已经定时的文章：

1. 登录Substack后台
2. 点击 **Posts** → **Scheduled**
3. 找到对应文章
4. 可以选择：
   - **Edit** - 修改内容或时间
   - **Delete** - 删除定时任务
   - **Publish now** - 立即发布

## 对比两个脚本

### `test_substack_auto_post.py`（立即发布）
- 生成文章后立即发布
- 适合测试或需要马上发布的情况

### `schedule_substack_posts.py`（定时发布）
- 批量生成多篇文章
- 设置未来的发布时间
- 适合规划长期内容发布

## 示例输出

运行成功后会看到类似这样的输出：

```
================================================================================
📅 Substack Scheduled Posting
================================================================================
Will schedule 4 posts
Publish time: 09:00

================================================================================
📝 Post 1/4
================================================================================
Schedule for: 2025-10-26 09:00 (3 days from now)

🤖 Generating article with AI...

✅ Article generated:
   Title: Week 6: Can AI Really Nail Your Next Interview?
   Subtitle: Here's what we learned this week building HireMeAI
   Content: 1234 chars

📅 Scheduling post for: 2025-10-26 09:00
1. Going to Substack home...
2. Clicking Create button...
3. Clicking Post from menu...
4. Filling title...
5. Filling subtitle...
6. Filling content...
7. Clicking Continue button...
8. Setting up scheduled publish...
   ✅ Clicked schedule option
   Setting date: 10/26/2025
   Setting time: 09:00 AM
   ✅ Date and time set
9. Clicking final schedule button...
   ✅ Article scheduled!

✅ Post 1 scheduled successfully!
```

## 常见问题

### Q: 如何检查文章是否真的定时了？
A: 登录Substack，查看 Posts → Scheduled 标签页

### Q: 能否一次定时更多文章？
A: 可以！在 `PUBLISH_SCHEDULE` 列表中添加更多条目

### Q: 时间设置错了怎么办？
A: 登录Substack后台，在Scheduled列表中编辑文章，修改时间

### Q: 可以改成每周一发布吗？
A: 可以！设置 `days_from_now` 为 7, 14, 21, 28... （每7天）
