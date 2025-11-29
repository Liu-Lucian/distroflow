# Product Hunt 完整营销系统 - 快速开始

## 📋 系统概述

Product Hunt 营销系统包含**两大功能模块**，全方位帮助 **HireMeAI (即答侠)** 在 Product Hunt 上推广：

### 🔥 模块 1：评论系统 (`auto_producthunt_forever.py`)
- **定位**：真实社区成员，不是推销员
- **风格**：热情、网络用语（lol, ngl, tbh, fr）、专注对方产品
- **原则**：80% 评论不提及 HireMeAI，像朋友聊天
- **频率**：每天 1-3 条高质量评论

### 🚀 模块 2：发布系统 (`producthunt_launcher.py`)
- **用途**：发布 HireMeAI 产品到 Product Hunt
- **格式**：标准 Launch 格式（Product Description + First Comment）
- **方式**：半自动（基础信息自动，图片手动）
- **时机**：产品正式发布时使用（建议太平洋时间 12:00-1:00 AM）

### 🎯 推广产品：HireMeAI
- **产品名**: HireMeAI (中文名：即答侠)
- **网址**: https://interviewasssistant.com
- **定位**: Real-time AI interview assistant that helps you answer like a pro
- **核心功能**:
  - AI 简历优化 + ATS 评分
  - 实时语音辅助（<1s 延迟）
  - 基于简历+JD 的智能问答模版
  - 说话人识别（区分面试官/面试者）
  - STAR/PREP 框架答案生成
- **技术栈**: GPT-4, Azure Speech, Picovoice Eagle, ChromaDB
- **目标用户**: Job seekers, career coaches, HR professionals

### 💡 系统特点
- 🤖 **AI 生成评论** - GPT-4o-mini 生成 Build in Public 风格的真诚评论
- ⏰ **智能调度** - 每天 1-3 次评论，避免 spam
- 🎯 **精准定位** - 专注于 AI Tools / Productivity / Career / HR Tech 相关产品
- 💬 **自然推广** - 评论中自然提及 HireMeAI，不硬推销

---

## 🚀 快速开始

### 选项 A：评论系统（日常使用，建议每天运行）

#### 1️⃣ 保存 Product Hunt 登录状态

```bash
python3 producthunt_login_and_save_auth.py
```

**操作步骤**:
1. 脚本会自动打开浏览器
2. 手动登录 Product Hunt（邮箱/Google/Twitter）
3. 登录成功后，脚本自动提取并保存 cookies
4. 认证信息保存到 `platforms_auth.json`

**提示**: Product Hunt 登录可能需要邮箱验证码

---

#### 2️⃣ 设置 OpenAI API Key

```bash
export OPENAI_API_KEY='sk-proj-...'
```

**作用**: AI 生成评论内容（使用 GPT-4o-mini，成本约 $0.001/条评论）

---

#### 3️⃣ 运行自动评论系统

```bash
python3 auto_producthunt_forever.py
```

**运行效果**:
- ✅ 每天自动生成 1-3 条评论
- ✅ 在指定时间段自动发布（9:00 / 13:00 / 17:00）
- ✅ 自动点赞产品 + 发布评论
- ✅ 评论风格：热情、网络用语、专注对方产品
- ✅ 永久运行，第二天自动生成新评论

---

### 选项 B：发布系统（产品 Launch 时使用，一次性）

#### 1️⃣ 准备素材（Launch 前 3 天）

**必备素材**:
- 封面图（512x512 PNG，简洁 Logo + Tagline）
- Gallery 图片（3-5 张，1200x800，展示核心功能）
- Demo 视频（30-60秒，<50MB，产品演示）

**制作工具**: Canva / Figma / Loom

---

#### 2️⃣ 预览 Launch 内容

```bash
python3 producthunt_launcher.py
# 选择 "2. 预览 Launch 内容"
```

**检查项**:
- ✅ Product Description（300-600 字）
- ✅ First Comment（置顶留言）
- ✅ Topic Tags
- ✅ Key Features

---

#### 3️⃣ 生成 Launch Checklist

```bash
python3 producthunt_launcher.py
# 选择 "1. 生成 Launch Checklist"
```

会生成 `producthunt_launch_checklist.txt`，包含完整发布清单

---

#### 4️⃣ 执行发布（半自动）

```bash
python3 producthunt_launcher.py
# 选择 "3. 开始发布流程"
```

**自动完成**:
- ✅ 填写 Product Name, Tagline, Website
- ✅ 填写 Product Description
- ✅ 添加 Topic Tags

**需手动完成**:
- ⚠️ 上传封面图和 Gallery
- ⚠️ 设置 Pricing
- ⚠️ 添加 Makers
- ⚠️ 点击 Submit/Schedule

---

#### 5️⃣ 发布后立即行动（1 分钟内）

1. **发 First Comment**（脚本会显示预生成内容）
2. **分享到 Twitter/LinkedIn**
3. **回复所有评论**（15 分钟响应时间）
4. **更新进展**（每 2-4 小时）

**详细发布指南**: 参考 `PRODUCTHUNT_LAUNCH_GUIDE.md`

---

### 🎯 最佳实践建议

**日常**（每天）：
- ✅ 运行评论系统，保持社区活跃度
- ✅ 每天 1-3 条真诚评论
- ✅ 建立 Product Hunt 社区存在感

**Launch 时**（一次性）：
- ✅ 提前 3 天准备素材
- ✅ 选择最佳时间（太平洋时间 12:00-1:00 AM）
- ✅ 发布后 24 小时内持续互动
- ✅ 争取进入 Top 10 或 Product of the Day

---

## 📂 文件结构

```
MarketingMind AI/
├── auto_producthunt_forever.py          # 主脚本 - 永久运行
├── producthunt_login_and_save_auth.py   # 认证保存工具
├── src/
│   ├── producthunt_commenter.py         # 评论发布器
│   └── producthunt_scraper.py           # 产品爬虫（可选）
├── platforms_auth.json                   # 认证信息（自动生成）
└── producthunt_schedule_YYYYMMDD.json   # 每日调度（自动生成）
```

---

## 🎯 评论策略

### 推荐频率

| 类型 | 频率 | 说明 |
|------|------|------|
| **评论互动** | 每天 1-3 次 | ✅ 当前系统实现 |
| 产品发布（Launch） | 每 3 个月 1 次 | 每个产品只发布 1 次 |
| 产品更新（Update） | 每周 1-2 次 | 在评论区更新进展 |
| 讨论区发帖 | 每周 1 次 | 分享经验、问题 |

**核心原则**: 质量 > 数量，避免被判为 spam

---

### 目标产品类别

**优先选择** (与 HireMeAI 相关):
- ✅ **AI Tools** - AI 辅助工具
- ✅ **Productivity** - 生产力工具
- ✅ **Career** - 职业发展相关
- ✅ **Developer Tools** - 开发者工具
- ✅ **HR Tech** - 人力资源科技

**避免**:
- ❌ 完全无关的产品（游戏、娱乐等）
- ❌ 竞争对手的直接竞品
- ❌ 低质量、spam 产品

---

### 评论风格示例（🔥 新风格）

**⚠️ 重要**：评论系统已更新为**真实社区成员**风格，不再是推销员风格！

#### ✅ 新风格示例 1（热情 + 网络用语 + 专注对方）

```
Yooo this looks fire 🔥 ngl the real-time feature is exactly what I've been
looking for. Quick Q - does it work with Slack? That'd be a game changer fr
```

**特点**:
- 🔥 热情、真实（Yooo, fire, ngl, fr）
- 💬 专注对方产品（90%）
- ❓ 提出实际问题
- 😊 像朋友聊天

---

#### ✅ 新风格示例 2（技术好奇 + 网络用语）

```
gg on the launch 🎉 The latency optimization is impressive tbh. Curious about
your tech stack - did you go with streaming or batching? Debating that myself lol
```

**特点**:
- 🎮 网络用语（gg, tbh, lol）
- 🧠 技术好奇心
- 🚫 不提及自己的产品
- 🤝 真诚交流

---

#### ✅ 新风格示例 3（痛点共鸣）

```
This solves a real pain point ngl. I've tried like 5 similar tools and they
all struggled with [problem]. How'd you tackle that?
```

**特点**:
- 💯 真实经历分享
- ⚡ 简洁有力（ngl）
- 🎯 聚焦对方的解决方案
- ❌ 完全不提 HireMeAI

---

#### ✅ 新风格示例 4（偶尔提及背景，10-20%概率）

```
Love the approach! As someone who's built similar stuff, I'm curious how you
handle edge cases? We struggled with latency early on but found [solution]
```

**特点**:
- ✅ 只在真正相关时提及背景
- 🎯 重点仍是对方的产品
- 💡 分享经验，不推销
- 🤝 提供价值

---

#### ❌ 旧风格（已废弃，不要这样）

```
Love the concept! As someone building HireMeAI (AI interview assistant),
I'm curious about your approach. We found <1s latency critical.
```

**问题**:
- ❌ 强行关联 HireMeAI
- ❌ 太正式，像写评论不像聊天
- ❌ 推销员感觉，不像社区成员

---

#### ❌ 不好的评论（硬推销）

```
Great product! You should try HireMeAI for your interview prep needs.
Check it out at https://interviewasssistant.com
```

**问题**:
- 纯推销，无价值
- 与对方产品无关
- 会被判为 spam

---

## ⚙️ 配置文件说明

### `producthunt_schedule_YYYYMMDD.json` 格式

```json
{
  "generated_at": "2025-10-23T09:00:00",
  "target_date": "2025-10-23",
  "schedule": [
    {
      "time_slot": "09:00-11:00",
      "product": {
        "url": "https://www.producthunt.com/posts/product-name",
        "name": "Product Name",
        "tagline": "Product tagline",
        "category": "AI Tools",
        "description": "Brief description"
      },
      "comment": "Your AI-generated comment here...",
      "posted": false,
      "posted_at": null
    }
  ]
}
```

**字段说明**:
- `time_slot` - 发布时间段
- `product` - 目标产品信息
- `comment` - 预生成的评论内容
- `posted` - 是否已发布
- `posted_at` - 实际发布时间

---

## 🔧 自定义配置

### 1. 修改每日评论数量

编辑 `auto_producthunt_forever.py:144`:

```python
# 原始（每天 1-3 条）
num_comments = min(random.randint(1, 3), len(products))

# 修改为每天固定 2 条
num_comments = min(2, len(products))

# 修改为每天 1 条
num_comments = min(1, len(products))
```

---

### 2. 修改发布时间段

编辑 `auto_producthunt_forever.py:149`:

```python
# 原始时间段
time_slots = ["09:00-11:00", "13:00-15:00", "17:00-19:00"]

# 修改为早中晚
time_slots = ["08:00-10:00", "12:00-14:00", "18:00-20:00"]

# 修改为仅白天
time_slots = ["10:00-12:00", "14:00-16:00"]
```

**建议**: 太平洋时间上午 12:00-1:00 AM 是 Product Hunt 发布高峰，上午 9:00-11:00 适合评论

---

### 3. 自定义产品列表（重要！）

**当前系统使用手动配置的产品列表**，需要你每天/每周更新。

编辑 `auto_producthunt_forever.py:97-123`:

```python
def get_todays_target_products(self) -> list:
    """获取今天要评论的产品"""

    # 手动配置每天的产品
    target_products = [
        {
            'url': 'https://www.producthunt.com/posts/product-name-1',
            'name': 'Product Name 1',
            'tagline': 'One-line description',
            'category': 'AI Tools, Productivity',
            'description': 'Detailed description...'
        },
        {
            'url': 'https://www.producthunt.com/posts/product-name-2',
            'name': 'Product Name 2',
            'tagline': '...',
            'category': 'Career',
            'description': '...'
        },
    ]

    return target_products
```

**如何找到相关产品**:
1. 访问 [Product Hunt - Today](https://www.producthunt.com)
2. 筛选 AI Tools / Productivity 类别
3. 复制产品 URL 和信息
4. 添加到 `target_products` 列表

---

### 4. 实现自动产品抓取（进阶）

**TODO**: 实现自动从 Product Hunt 抓取每日产品

可以基于 `src/producthunt_scraper.py` 扩展:

```python
from src.producthunt_scraper import ProductHuntScraper

def get_todays_target_products(self) -> list:
    """自动抓取今天的相关产品"""
    scraper = ProductHuntScraper()

    # 抓取今日产品
    products = scraper.get_todays_posts(categories=['AI Tools', 'Productivity'])

    # 过滤相关产品
    relevant = [p for p in products if self._is_relevant(p)]

    return relevant[:3]  # 返回前3个
```

---

## 📊 效果跟踪

### 查看每日调度

```bash
# 查看今天的调度
cat producthunt_schedule_$(date +%Y%m%d).json | python3 -m json.tool

# 查看某天的调度
cat producthunt_schedule_20251023.json | python3 -m json.tool
```

---

### 检查发布状态

```python
import json
from datetime import datetime

# 读取今天的调度
today = datetime.now().strftime('%Y%m%d')
with open(f'producthunt_schedule_{today}.json', 'r') as f:
    schedule = json.load(f)

# 统计
total = len(schedule['schedule'])
posted = sum(1 for item in schedule['schedule'] if item['posted'])

print(f"总计: {total} 条评论")
print(f"已发布: {posted} 条")
print(f"待发布: {total - posted} 条")
```

---

## 🐛 常见问题

### Q1: "❌ Product Hunt 未登录"

**原因**: Cookies 过期或未保存

**解决**:
```bash
# 重新保存认证
python3 producthunt_login_and_save_auth.py
```

---

### Q2: "❌ 未找到评论输入框"

**原因**: Product Hunt 页面结构变化

**解决**:
1. 截图已保存到 `producthunt_comment_box_not_found_*.png`
2. 打开截图，手动找到评论框的选择器
3. 编辑 `src/producthunt_commenter.py:80-86`
4. 添加新的选择器

---

### Q3: "未找到相关产品，跳过今天"

**原因**: `get_todays_target_products()` 返回空列表

**解决**:
1. 手动访问 [Product Hunt](https://www.producthunt.com)
2. 找到相关产品
3. 编辑 `auto_producthunt_forever.py:97-123`
4. 添加产品信息

---

### Q4: 评论内容太硬推销

**原因**: AI 生成的评论风格问题

**解决**:
1. 编辑 `auto_producthunt_forever.py:32-76`
2. 修改 prompt 中的指导语
3. 增加 `temperature` 值（0.8 → 0.9）增加创意性
4. 或降低 `temperature` 值（0.8 → 0.7）增加保守性

---

## 🔒 安全建议

1. **不要硬编码 API Key** - 使用环境变量
2. **定期检查评论质量** - 避免被判为 spam
3. **遵守 Product Hunt 社区规范** - 真诚互动，不刷赞
4. **使用专用账号** - 不要用个人主账号测试

---

## 📈 优化建议

### 提升评论质量

1. **手动审核**（推荐）:
   ```python
   # 修改 auto_producthunt_forever.py
   # 生成评论后暂停，手动审核

   comment = self.generate_authentic_comment(product)
   print(f"\n预览评论:\n{comment}\n")
   confirm = input("是否发布？(y/N): ")
   if confirm.lower() != 'y':
       continue
   ```

2. **使用更强的模型**:
   ```python
   # 将 gpt-4o-mini 改为 gpt-4o
   model="gpt-4o",  # 更高质量，但成本 20x
   ```

3. **添加评论模板库**:
   ```python
   # 预定义一些高质量评论模板
   templates = [
       "Love the [feature]! Quick question: {question}",
       "Congrats on the launch! Have you considered {suggestion}?",
       ...
   ]
   ```

---

### 提升曝光效果

1. **在多个时间段分散评论** - 已实现
2. **先点赞再评论** - 已实现
3. **关注产品制造者** - TODO
4. **分享到 Twitter** - TODO

---

## 🚧 待实现功能

- [ ] 自动抓取每日相关产品（基于 Product Hunt API）
- [ ] 评论效果追踪（点赞数、回复数）
- [ ] 多账号轮换评论
- [ ] 集成到 `marketing-campaign` 全局命令
- [ ] 评论历史去重（避免重复评论同一产品）
- [ ] Webhook 通知（评论成功后发送通知）

---

## 📞 技术支持

**问题反馈**: liu.lucian6@gmail.com

**产品官网**: https://interviewasssistant.com

---

## 📚 相关文档

- `auto_twitter_forever.py` - Twitter 自动发布系统（参考模式）
- `CLAUDE.md` - 项目整体架构说明
- `产品介绍.md` - HireMeAI 产品详情

---

**Happy Hunting! 🚀**
