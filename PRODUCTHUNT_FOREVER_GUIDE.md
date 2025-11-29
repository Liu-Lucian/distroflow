# Product Hunt 永久评论系统 - 使用指南

## 🎯 系统概述

**auto_producthunt_forever.py** 是一个永久运行的 Product Hunt 自动评论系统，每天自动发布 3 条真诚评论，建立社区存在感。

### 特点

- ✅ **每天自动运行** - 每 4 小时检查一次，确保完成每日目标
- ✅ **真诚社区风格** - 100% 专注于他人产品，不推销
- ✅ **AI 生成评论** - 使用 GPT-4o-mini，自然的 internet slang + emoji
- ✅ **智能防重复** - 永不重复评论同一产品
- ✅ **进度追踪** - 完整记录所有互动历史
- ✅ **自动点赞** - 每条评论自动附带点赞

---

## 🚀 快速开始

### 前提条件

1. ✅ Product Hunt 账号已登录（`platforms_auth.json` 包含 localStorage）
2. ✅ OpenAI API Key 已设置
3. ✅ 今日产品列表已准备 (`todays_producthunt_products.json`)

### 启动命令

```bash
# 1. 设置 API key
export OPENAI_API_KEY='sk-proj-...'

# 2. 启动永久运行
python3 auto_producthunt_forever.py
```

**就这么简单！**

---

## 📋 每日工作流程

### 每天早上（5 分钟）

#### 选项 A: 手动更新产品列表（推荐）

1. 访问 https://www.producthunt.com
2. 查看 "Today" 页面
3. 选择 3-5 个相关产品（AI Tools, Productivity, Developer Tools）
4. 更新 `todays_producthunt_products.json`：

```json
{
  "date": "2025-10-24",
  "products": [
    {
      "url": "https://www.producthunt.com/posts/product-name",
      "name": "Product Name",
      "tagline": "Product tagline",
      "category": "AI Tools, Productivity",
      "description": "Brief description"
    }
    // ... 更多产品
  ]
}
```

#### 选项 B: 半自动获取

```bash
python3 fetch_todays_producthunt_products.py
# 然后手动编辑生成的文件
```

### 系统自动运行

脚本会：
- 每 4 小时检查一次
- 如果今日任务未完成，自动执行
- 完成后等待下一个检查周期

---

## ⚙️ 配置说明

### 可调整参数

在 `auto_producthunt_forever.py` 顶部：

```python
DAILY_COMMENT_TARGET = 3     # 每天目标评论数（建议 2-4）
CHECK_INTERVAL_HOURS = 4     # 检查间隔（建议 4-6 小时）
PRODUCT_LIST_FILE = "todays_producthunt_products.json"  # 产品列表文件
PROGRESS_FILE = "producthunt_forever_progress.json"     # 进度文件
```

### 评论风格配置

编辑 `generate_comment()` 函数的 prompt 可以调整：
- Internet slang 使用频率
- Emoji 数量
- 评论长度
- 提问风格

---

## 📊 进度追踪

### 查看实时进度

脚本运行时会自动显示进度：

```
📊 Product Hunt 永久评论系统 - 进度报告

⏰ 运行时间:
   开始日期: 2025-10-23
   运行天数: 5 天

📈 总体统计:
   总评论数: 15
   总点赞数: 15
   互动产品: 15 个

📅 最近 7 天:
   2025-10-27: 3 评论, 3 点赞
   2025-10-26: 3 评论, 3 点赞
   2025-10-25: 3 评论, 3 点赞
   ...
```

### 查看进度文件

```bash
cat producthunt_forever_progress.json | python3 -m json.tool
```

### 查看日志文件

```bash
tail -f producthunt_forever.log
```

---

## 🔍 工作原理

### 执行流程

```
启动 → 检查今日进度 → 是否需要运行？
                      ↓
                     是
                      ↓
          加载可用产品（排除已互动）
                      ↓
          设置浏览器 + 验证登录
                      ↓
     For 每个产品（直到达到目标）:
       • 生成评论（AI）
       • 访问产品页面
       • 点赞
       • 发布评论
       • 随机延迟 5-15 分钟
                      ↓
          关闭浏览器 + 保存进度
                      ↓
          等待 4 小时后重新检查
```

### 智能防重复

系统维护两个列表：
1. **每日已互动产品** - 当天完成后清零
2. **全局已互动产品** - 永久记录，永不重复

---

## 💬 评论风格示例

### 好的评论（AI 会生成类似的）

```
✅ "Yooo this looks fire 🔥 ngl I've been searching for something
    like this. Quick Q - does it integrate with Notion?"

✅ "Love this! The UI is clean af. Congrats on the launch 🎉
    What was your biggest challenge building this?"

✅ "This solves a real problem tbh. I've struggled with workflow
    automation forever. Does it work on mobile too?"
```

### 评论特点

- 🎯 100% 专注于他人产品
- 🗣️ 使用 internet slang（ngl, tbh, fr, lol, gg）
- 😊 1-2 个 emoji
- ❓ 提出真诚问题
- 💯 具体说明喜欢什么

---

## 🛠️ 故障排查

### 问题 1: "未找到 todays_producthunt_products.json"

**解决**:
```bash
# 创建产品列表
python3 fetch_todays_producthunt_products.py
# 或手动创建文件
```

### 问题 2: "Product Hunt 未登录"

**解决**:
```bash
# 重新提取登录状态
python3 extract_producthunt_storage.py
# 或完整重新登录
python3 producthunt_login_enhanced.py
```

### 问题 3: "评论发布失败"

**检查**:
1. 查看截图 `producthunt_*.png`
2. 手动访问产品页面确认是否发布
3. 检查 cookies 是否过期
4. 页面选择器可能已改变（运行 `inspect_producthunt_page.py`）

### 问题 4: "无可用产品"

**原因**: 所有产品都已互动过

**解决**:
1. 更新 `todays_producthunt_products.json` 为新产品
2. 或清空 `producthunt_forever_progress.json` 的 `interacted_products`（慎用）

---

## 📈 性能优化

### API 成本

```
每天 3 条评论:
  • AI 生成评论: 3 × $0.0001 = $0.0003
  • 每月成本: ~$0.009

非常经济！
```

### 时间投入

```
初次设置: 10 分钟
每日维护: 5 分钟（更新产品列表）
自动运行: 0 分钟
```

---

## 🎯 最佳实践

### 1. 每天更新产品列表

**关键**: 每天早上花 5 分钟更新产品列表

**选择标准**:
- ✅ 相关类别（AI Tools, Productivity, Developer Tools）
- ✅ 今日发布（更容易获得回复）
- ✅ 真正感兴趣的产品
- ❌ 避免直接竞品

### 2. 保持真诚

**系统已配置为 100% 真诚风格**:
- 绝不提及自己的产品
- 专注于帮助和学习
- 提出真实问题
- 分享真实想法

### 3. 监控效果

**每周检查一次**:
- 访问 Product Hunt 查看评论
- 是否有人回复你的评论？
- 评论质量如何？
- 需要调整风格吗？

### 4. 调整配置

**根据效果调整**:
- 如果评论太多 → 降低 `DAILY_COMMENT_TARGET` 到 2
- 如果想更活跃 → 提高到 4-5（但注意不要 spam）
- 如果被检测 → 增加 `CHECK_INTERVAL_HOURS` 到 6-8

---

## 🔒 安全注意事项

### 避免被封号

1. **不要过度活跃** - 每天 2-4 条评论足够
2. **保持真诚** - 100% 真实评论，不 spam
3. **随机延迟** - 系统已内置 5-15 分钟随机延迟
4. **不要同时运行多个实例** - 一个账号一个实例

### 数据安全

- `platforms_auth.json` 包含登录信息，妥善保管
- 不要分享 `producthunt_forever_progress.json`（包含完整历史）
- `producthunt_forever.log` 可以分享（不含敏感信息）

---

## 📞 支持

### 遇到问题？

1. **查看日志**: `tail -f producthunt_forever.log`
2. **查看截图**: `open producthunt_*.png`
3. **手动测试**: `python3 test_single_comment.py`
4. **检查页面**: `python3 inspect_producthunt_page.py`

### 相关文档

- `PRODUCTHUNT_LOGIN_FIX_SUMMARY.md` - 登录问题修复
- `PRODUCTHUNT_WARMUP_FIX_COMPLETE.md` - Warmup 脚本修复
- `PRODUCTHUNT_WARMUP_GUIDE.md` - 7天养号指南

---

## 🎊 成功案例

### Day 1 测试结果

```
✅ 2 条评论成功发布
   • Nimo: "Ngl, Nimo sounds like a game changer!..."
   • Migma AI: "Yooo, Migma AI looks awesome!..."

✅ 2 个点赞成功
✅ 创始人已回复评论
✅ 评论风格自然，融入社区
```

---

## 🚦 常见使用场景

### 场景 1: 长期养号

```bash
# 每天自动运行，建立社区存在感
nohup python3 auto_producthunt_forever.py &
# 后台运行，不影响其他工作
```

### 场景 2: 7天冲刺

```bash
# 调整配置为更积极
DAILY_COMMENT_TARGET = 4
CHECK_INTERVAL_HOURS = 3
# 连续运行 7 天准备发布
```

### 场景 3: 测试模式

```bash
# 降低频率测试
DAILY_COMMENT_TARGET = 1
CHECK_INTERVAL_HOURS = 12
# 观察效果后调整
```

---

## 📚 技术细节

### 依赖

- `playwright` - 浏览器自动化
- `openai` - AI 生成评论
- `Python 3.8+` - 运行环境

### 文件结构

```
MarketingMind AI/
├── auto_producthunt_forever.py          # 永久运行主脚本
├── todays_producthunt_products.json     # 今日产品列表
├── producthunt_forever_progress.json    # 进度文件（自动生成）
├── producthunt_forever.log              # 日志文件（自动生成）
├── platforms_auth.json                  # 登录状态
├── src/producthunt_commenter.py         # 评论发布器
└── 相关工具脚本...
```

---

## ✨ 总结

**auto_producthunt_forever.py** 是一个:

- ✅ **可靠的** - 经过完整测试，已成功发布评论
- ✅ **自动的** - 设置后无需人工干预
- ✅ **真诚的** - 100% 社区风格，不推销
- ✅ **智能的** - AI 生成自然评论
- ✅ **经济的** - 每月成本 < $0.01

**设置一次，持续运行，建立 Product Hunt 社区存在感！**

---

**最后更新**: 2025-10-23

**状态**: ✅ 完全可用，已测试成功

**推荐使用**: 所有想在 Product Hunt 建立存在感的产品
