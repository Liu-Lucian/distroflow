# 产品配置系统使用指南

## 📁 文件说明

### 1. `product_config.json` - 产品配置文件（你编辑这个）

这是核心配置文件，控制整个Instagram营销系统的行为。

**主要配置项**：

```json
{
  "product_name": "你的产品名",
  "product_url": "https://你的网站.com",
  "product_description": "一句话产品介绍",

  "detailed_description": "详细描述产品特点、目标用户、解决的痛点",

  "target_audience": ["目标用户1", "目标用户2"],

  "pain_points": ["痛点1", "痛点2"],

  "keywords_instagram": ["关键词1", "关键词2"],

  "message_template": "DM消息模板",

  "ai_settings": {
    "min_intent_score": 0.5,
    "model": "gpt-4o-mini"
  },

  "campaign_settings": {
    "posts_per_keyword": 10,
    "comments_per_post": 20,
    "delay_between_messages_seconds": [5, 10],
    "delay_between_keywords_seconds": [10, 20],
    "max_cycles": 0
  }
}
```

---

## 🚀 使用流程

### 步骤1: 编辑产品配置

```bash
nano product_config.json
```

**重点编辑**：
1. `product_name` - 你的产品名
2. `product_url` - 你的网站
3. `detailed_description` - **详细描述你的产品**（AI会根据这个生成关键词和分析用户）
4. `target_audience` - 目标用户类型
5. `pain_points` - 你的产品解决的痛点

### 步骤2: 让AI生成Instagram关键词

```bash
python3 update_keywords_from_config.py
```

**这个脚本会**：
1. 读取你的产品描述
2. 调用GPT-4o-mini生成15个Instagram hashtag关键词
3. 自动更新 `product_config.json` 中的 `keywords_instagram`

**示例输出**：
```
🤖 AI Keyword Generator for Instagram
======================================================================

📦 Product: HireMeAI
📝 Description: AI-powered interview preparation platform
🎯 Target: 求职者, 应届毕业生, 转行人士

🤖 Asking AI to generate keywords...

✅ AI generated 15 keywords:
   1. #jobsearch
   2. #interviewtips
   3. #careerdevelopment
   ...

✅ Updated product_config.json with new keywords
```

### 步骤3: 运行Instagram营销系统

```bash
python3 run_instagram_campaign_v2.py
```

**脚本会自动**：
1. 从 `product_config.json` 读取所有配置
2. 使用AI生成的关键词搜索Instagram帖子
3. 爬取评论并用AI分析用户匹配度
4. 自动发送个性化DM

---

## 🎯 配置项详解

### 1. 产品信息

```json
{
  "product_name": "HireMeAI",
  "product_url": "https://interviewasssistant.com",
  "product_description": "简短的一句话介绍",
  "detailed_description": "详细描述（AI会用这个来生成关键词和分析用户）"
}
```

**建议**：`detailed_description` 越详细越好，包括：
- 核心功能
- 目标用户
- 解决的痛点
- 竞争优势
- 使用场景

### 2. 目标用户和痛点

```json
{
  "target_audience": [
    "求职者",
    "应届毕业生",
    "转行人士"
  ],
  "pain_points": [
    "面试准备困难",
    "缺乏面试反馈",
    "面试焦虑"
  ]
}
```

**用途**：AI会根据这些信息筛选评论中匹配的用户。

### 3. 消息模板

```json
{
  "message_template": "Hey {name}! I saw your comment about {topic}.\n\nI'm building {product_name} ({product_url}), an AI interview prep platform.\n\n{pain_point}\n\nWould love your thoughts!"
}
```

**可用变量**：
- `{name}` - 用户名
- `{product_name}` - 产品名
- `{product_url}` - 产品URL
- `{topic}` - 关键词主题
- `{pain_point}` - AI识别的用户痛点

### 4. AI设置

```json
{
  "ai_settings": {
    "min_intent_score": 0.5,
    "model": "gpt-4o-mini"
  }
}
```

**参数说明**：
- `min_intent_score`: 0.0-1.0，越高越严格
  - 0.3 = 宽松（更多用户）
  - 0.5 = 中等（推荐）
  - 0.7 = 严格（只要高匹配用户）
- `model`: AI模型（推荐用 `gpt-4o-mini` 省钱）

### 5. 营销活动设置

```json
{
  "campaign_settings": {
    "posts_per_keyword": 10,
    "comments_per_post": 20,
    "delay_between_messages_seconds": [60, 120],
    "delay_between_keywords_seconds": [300, 600],
    "max_cycles": 0
  }
}
```

**参数说明**：
- `posts_per_keyword`: 每个关键词搜索多少个帖子
- `comments_per_post`: 每个帖子爬多少条评论
- `delay_between_messages_seconds`: 发送DM的延迟（秒）
  - `[60, 120]` = 1-2分钟随机延迟
  - `[5, 10]` = 5-10秒（测试模式）
- `delay_between_keywords_seconds`: 换关键词的延迟（秒）
  - `[300, 600]` = 5-10分钟
  - `[10, 20]` = 10-20秒（测试模式）
- `max_cycles`: 最大循环次数
  - `0` = 无限循环
  - `5` = 运行5轮后停止

---

## 📋 完整工作流示例

### 场景：推广新的AI产品

**1. 编辑配置文件**

```bash
nano product_config.json
```

```json
{
  "product_name": "MyAITool",
  "product_url": "https://myaitool.com",
  "product_description": "AI-powered productivity assistant for remote workers",

  "detailed_description": "MyAITool helps remote workers stay productive with AI-powered task management, time tracking, and focus mode. Perfect for freelancers, digital nomads, and remote teams who struggle with distractions and time management.",

  "target_audience": [
    "远程工作者",
    "自由职业者",
    "数字游民",
    "创业者"
  ],

  "pain_points": [
    "工作效率低",
    "时间管理困难",
    "容易分心",
    "任务管理混乱"
  ]
}
```

**2. 生成关键词**

```bash
python3 update_keywords_from_config.py
```

AI会生成：
- `remotework`
- `productivity`
- `digitalnomad`
- `freelancer`
- `workfromhome`
- ...

**3. 运行营销系统**

```bash
python3 run_instagram_campaign_v2.py
```

系统会：
1. 在Instagram搜索 `#remotework`、`#productivity` 等
2. 爬取帖子评论
3. AI分析评论者是否匹配（远程工作者、有生产力问题等）
4. 自动发送个性化DM

---

## 🔄 更新配置

**随时可以修改配置，无需重启**：

```bash
# 1. 修改配置
nano product_config.json

# 2. 重新生成关键词（如果改了产品描述）
python3 update_keywords_from_config.py

# 3. 重新运行（会读取新配置）
python3 run_instagram_campaign_v2.py
```

---

## 💡 最佳实践

### 1. 测试模式 vs 生产模式

**测试模式**（快速验证）：
```json
{
  "campaign_settings": {
    "posts_per_keyword": 3,
    "comments_per_post": 10,
    "delay_between_messages_seconds": [5, 10],
    "delay_between_keywords_seconds": [10, 20],
    "max_cycles": 2
  }
}
```

**生产模式**（正式营销）：
```json
{
  "campaign_settings": {
    "posts_per_keyword": 20,
    "comments_per_post": 30,
    "delay_between_messages_seconds": [60, 180],
    "delay_between_keywords_seconds": [300, 600],
    "max_cycles": 0
  }
}
```

### 2. 优化关键词

如果生成的关键词效果不好：

1. **改进产品描述** - 在 `detailed_description` 中加入更多细节
2. **重新生成** - `python3 update_keywords_from_config.py`
3. **手动调整** - 直接编辑 `keywords_instagram` 数组

### 3. 调整用户质量

**想要更多用户**（降低门槛）：
```json
{
  "ai_settings": {
    "min_intent_score": 0.3
  }
}
```

**只要高质量用户**（提高门槛）：
```json
{
  "ai_settings": {
    "min_intent_score": 0.7
  }
}
```

---

## 📊 追踪结果

系统会自动保存已发送的用户到：
```
instagram_v2_sent.json
```

查看统计：
```bash
python3 -c "import json; d=json.load(open('instagram_v2_sent.json')); print(f'Total sent: {len(d)}')"
```

---

## ❓ 常见问题

**Q: 如何修改DM消息内容？**
A: 编辑 `product_config.json` 中的 `message_template`

**Q: 关键词太少/太多怎么办？**
A: 运行 `python3 update_keywords_from_config.py` 重新生成，或手动编辑配置文件

**Q: 如何暂停/继续营销活动？**
A: Ctrl+C 停止，重新运行脚本继续（会跳过已发送用户）

**Q: 如何重置已发送列表？**
A: 删除或重命名 `instagram_v2_sent.json`

---

## 🎉 快速开始

```bash
# 1. 编辑产品信息
nano product_config.json

# 2. 生成关键词
python3 update_keywords_from_config.py

# 3. 开始营销！
python3 run_instagram_campaign_v2.py
```

That's it! 系统会自动运行。
