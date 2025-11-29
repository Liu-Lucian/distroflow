# 声誉毒药清理清单

**目标**：把项目从"营销工具"升级为"技术基础设施"

---

## 🔴 必须立即删除/修改的内容

### 1. 中文内容清理

运行这个命令找出所有中文：
```bash
# 查找所有包含中文的文件
find . -name "*.py" -o -name "*.md" | xargs grep -l "[\u4e00-\u9fa5]" > chinese_files.txt

# 查看列表
cat chinese_files.txt
```

**需要处理的文件**：
- [ ] 所有中文注释改为英文
- [ ] 中文变量名改为英文
- [ ] 中文文档移到 `archive/` 或删除

### 2. 营销术语清理

查找这些词并替换：
```bash
# 查找营销相关词汇
grep -r "营销\|矩阵\|养号\|灰产\|引流\|变现" . --include="*.py" --include="*.md"
```

**替换规则**：
- ❌ "营销" → ✅ "distribution"
- ❌ "矩阵" → ✅ "multi-platform presence"
- ❌ "养号" → ✅ "account management"
- ❌ "灰产" → 🗑️ 删除
- ❌ "引流" → ✅ "user acquisition" / "lead generation"
- ❌ "变现" → ✅ "monetization" (仅在合法语境下)

### 3. 敏感功能重新定位

#### Instagram DM 功能
**当前描述**：
```
Instagram Lead Generation
Find and engage users interested in your product
```

**改为**：
```
Instagram User Research
Analyze user engagement patterns for market research
(Use responsibly and respect platform ToS)
```

#### TikTok 批量操作
**当前描述**：
```
Auto-DM 100 users in 30 minutes
```

**改为**：
```
TikTok Engagement Research Tool
Study comment patterns and user interactions
(For research purposes only)
```

### 4. 文件重命名

**需要重命名的文件**：
```bash
# 营销相关文件名
mv run_instagram_campaign_optimized.py run_instagram_research.py
mv run_tiktok_campaign_optimized.py run_tiktok_research.py
mv run_facebook_campaign.py run_facebook_research.py

# DM sender 改为 engagement analyzer
mv src/instagram_dm_sender_optimized.py src/instagram_engagement_analyzer.py
mv src/tiktok_dm_sender_optimized.py src/tiktok_engagement_analyzer.py
```

---

## ✅ 必须添加的内容

### 1. ETHICS.md

创建 `ETHICS.md`：

```markdown
# Ethics & Responsible Use

## Intended Uses

DistroFlow is designed for legitimate automation of YOUR OWN content across platforms.

### ✅ Appropriate Uses
- Posting your own content to multiple platforms
- Scheduling your own updates
- Research on content distribution patterns
- Building in public / developer presence
- Product launches and announcements

### ❌ Prohibited Uses
- Spam or unsolicited messages
- Mass direct messaging without consent
- Vote manipulation or fake engagement
- Astroturfing or coordinated inauthentic behavior
- Scraping private data
- Violating platform Terms of Service

## Your Responsibility

You are responsible for:
1. Following each platform's Terms of Service
2. Respecting rate limits and platform rules
3. Obtaining appropriate consent for messaging
4. Using the tool ethically and legally

## Platform Terms of Service

Before using DistroFlow, review these platform policies:
- Twitter: https://twitter.com/tos
- Reddit: https://www.redditinc.com/policies/user-agreement
- Instagram: https://help.instagram.com/581066165581870
- HackerNews: https://news.ycombinator.com/newsguidelines.html

## Research Use

If using for academic research:
- Obtain IRB approval if studying human subjects
- Follow data privacy regulations (GDPR, CCPA)
- Cite this tool appropriately
- Share findings with the community

## Reporting Abuse

If you see DistroFlow being used unethically:
- Report to platform directly
- Open GitHub issue (we'll investigate)
- Email: lucian@uci.edu

**Remember**: With great automation comes great responsibility.
```

### 2. 更新 README 的 Ethics 部分

在主 README 中强调：

```markdown
## Ethics & Compliance

**DistroFlow is designed for legitimate use only.**

This tool is for posting YOUR OWN content across platforms, not for spam or manipulation.

### ✅ Allowed
- Distributing your own content
- Research with appropriate consent
- Building in public
- Product launches

### ❌ Not Allowed
- Spam or unsolicited messages
- Vote manipulation
- Astroturfing
- ToS violations

See [ETHICS.md](ETHICS.md) for full guidelines.

**Your Responsibility**: You control the code. Use it responsibly.
```

### 3. 添加 LICENSE 提醒

在代码文件顶部添加：

```python
"""
DistroFlow - Open-source cross-platform distribution infrastructure
Copyright (c) 2025 Lucian Liu

Licensed under MIT License. See LICENSE for details.

IMPORTANT: Use responsibly. Respect platform ToS. No spam.
"""
```

---

## 🔧 技术定位调整

### 1. 项目描述更新

**所有地方统一使用这个描述**：

```
DistroFlow - Open-source cross-platform distribution infrastructure

Browser automation framework for programmatic content delivery
across social platforms when APIs are unavailable or restricted.
```

**不要再说**：
- ❌ "营销工具"
- ❌ "自动化引流"
- ❌ "批量私信"

**要说**：
- ✅ "Distribution infrastructure"
- ✅ "Content automation framework"
- ✅ "Platform-agnostic posting system"

### 2. 功能重新框架

| 当前功能 | 当前命名 | 新命名 | 新定位 |
|---------|----------|--------|--------|
| Instagram DM | Lead Generation | User Engagement Research | 研究工具 |
| TikTok 批量操作 | Auto Campaign | Content Research | 内容分析 |
| Facebook DM | Marketing Tool | Community Engagement | 社区工具 |
| 批量发帖 | Campaign Launch | Multi-platform Post | 分发系统 |

### 3. 代码注释更新

**Before**:
```python
# 批量发送私信给潜在客户
async def send_dm_batch(users):
    for user in users:
        await send_dm(user, "购买我的产品")
```

**After**:
```python
# Research user engagement patterns
# NOTE: Only use with explicit user consent
async def analyze_engagement(users):
    for user in users:
        await send_research_message(user, template)
```

---

## 📝 文档重写优先级

### High Priority (本周完成)

1. **README.md** - 用 `README_REPUTATION.md` 替换
2. **ETHICS.md** - 新建
3. **TECHNICAL_DEEP_DIVE.md** - 已创建，添加到文档链接
4. **CONTRIBUTING.md** - 审查并更新

### Medium Priority (下周完成)

5. **ARCHITECTURE.md** - 审查技术准确性
6. **PLATFORMS.md** - 重新定位各平台用途
7. **API.md** - 添加 API 文档

### Low Priority (可选)

8. **RESEARCH.md** - 学术用例
9. **CASE_STUDIES.md** - 合法使用案例
10. **FAQ.md** - 常见问题

---

## 🚨 危险文件清理

### 需要删除或归档的文件

```bash
# 创建 archive 目录
mkdir -p archive/legacy_marketing

# 移动营销相关文件
mv 一键启动说明.md archive/legacy_marketing/
mv FACEBOOK_QUICKSTART.md archive/legacy_marketing/
mv README_MARKETING_SYSTEM.md archive/legacy_marketing/
mv LINKEDIN_DM_GUIDE.md archive/legacy_marketing/

# 或者直接删除（如果不需要保留）
# rm 一键启动说明.md FACEBOOK_QUICKSTART.md ...
```

### 需要重写的文件

- [ ] `marketing-campaign` 脚本 → 改名为 `distroflow-research`
- [ ] 所有 `campaign` 相关脚本 → 改为 `research` 或 `experiment`

---

## ✅ 执行计划

### Day 1 (今天)
- [ ] 运行清理脚本找出所有中文和营销术语
- [ ] 用 `README_REPUTATION.md` 替换主 README
- [ ] 创建 `ETHICS.md`
- [ ] 移动/删除危险文件到 `archive/`

### Day 2 (明天)
- [ ] 重命名所有包含 "campaign"、"marketing" 的文件
- [ ] 更新所有代码注释（英文化）
- [ ] 审查并更新 CONTRIBUTING.md

### Day 3 (后天)
- [ ] 添加 TECHNICAL_DEEP_DIVE.md 到文档链接
- [ ] 更新所有文档的技术定位
- [ ] 运行 `pre_launch_test.sh` 确保一切正常

---

## 📊 完成标准

清理完成的标志：

✅ **零中文内容**
```bash
# 这个命令应该返回空
find . -name "*.py" -o -name "*.md" | xargs grep -l "[\u4e00-\u9fa5]"
```

✅ **零营销术语**
```bash
# 这些词应该不存在
grep -r "营销\|矩阵\|养号\|灰产" . --include="*.py" --include="*.md"
```

✅ **清晰的伦理声明**
```bash
# 这些文件应该存在
ls ETHICS.md
grep -q "Responsible Use" README.md
```

✅ **专业的项目定位**
```bash
# README 第一段应该是技术描述，不是营销话术
head -20 README.md | grep "infrastructure"
```

---

## 🎯 最终目标

完成后，你的项目应该：

1. **看起来像**：Playwright, FastAPI, Supabase（技术项目）
2. **不像**：营销工具、灰产脚本、矩阵号系统

3. **适合展示给**：
   - ✅ 面试官
   - ✅ 教授
   - ✅ YC 投资人
   - ✅ HN 社区

4. **不适合展示给**：
   - ❌ 微商
   - ❌ 灰产从业者
   - ❌ 营销公司

---

## 🚀 下一步

完成清理后：

1. **GitHub 公开发布**
2. **Reddit 技术社区分享**
3. **HN Show HN 发帖**
4. **LinkedIn 技术输出**

时间很关键 - 寒假是黄金窗口，我们要在 2 周内完成清理并公开发布。

**准备好了吗？从 Day 1 的任务开始！** 🚀
