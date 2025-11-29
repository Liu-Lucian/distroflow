# Substack 自动发布与回答系统使用指南

## 📋 系统概述

这是一个完整的 Substack 自动化系统，包含两大核心功能：

1. **自动发布系统** - 定期生成并发布 Build in Public 风格的Newsletter文章
2. **自动回答系统** - 监控文章评论，智能生成并发布有价值的回答

**核心特点**：
- ✅ 采用用户验证的**高转化率Substack文章格式**（参考用户提供的模板）
- ✅ 回答风格：**简短、热情、不推销、可用网络用语**
- ✅ 永久运行，无需人工干预
- ✅ 成本极低（AI调用使用 GPT-4o-mini）

---

## 🚀 快速开始

### 1. 前置要求

```bash
# Python 3.8+
# 已安装依赖
pip install playwright openai

# 安装Playwright浏览器
playwright install chromium

# 设置OpenAI API Key
export OPENAI_API_KEY='sk-proj-your-key-here'
```

### 2. 配置Substack域名

编辑以下文件，替换 `SUBSTACK_DOMAIN`：
- `auto_substack_forever.py`
- `test_substack_system.py`

```python
SUBSTACK_DOMAIN = "yourname.substack.com"  # 替换为你的域名
```

### 3. 登录并保存认证信息

```bash
python3 substack_login_and_save_auth.py
```

**操作步骤**：
1. 输入你的Substack域名（如 `yourname.substack.com`）
2. 浏览器会自动打开
3. 手动登录Substack（邮箱验证链接登录）
4. 登录成功后回到终端按Enter
5. 脚本会自动提取并保存cookies到 `substack_auth.json`

✅ **认证完成！** 之后所有脚本都会自动使用这些cookies登录

---

## 📝 核心功能使用

### 功能1: 自动发布Build in Public文章

#### 文章格式（高转化率模板）

系统自动生成的文章遵循以下结构：

```
标题格式: Week X: [吸引力] + [价值点] + [解决方案暗示]
例: "Week 3: Why 90% of Candidates Fail Behavioral Interviews (and How AI Fixes It)"

文章结构 (800-1200字):
1. Hook Opening (1-2段) - 吸引人的故事或数据
2. The Problem (2-3段) - 明确痛点
3. The Insight/Solution (3-4段) - 技术发现 + 具体指标
4. Case/Example (2段) - 真实案例
5. Takeaway (1-2段) - 升华观点
6. Call to Action - 自然引导

语气: 对话式但专业，有数据支撑，透明的build in public风格
```

#### 立即生成并发布一篇文章

```bash
python3 auto_substack_forever.py --mode generate
```

**流程**：
1. AI自动生成文章（根据当前周数）
2. 终端显示文章预览
3. 询问是否发布
4. 确认后自动发布到Substack

#### 永久运行模式（推荐）

```bash
python3 auto_substack_forever.py --mode forever
```

**运行逻辑**：
- **每周一 9:00** 自动生成并发布新文章
- **每天 10:00 和 16:00** 检查评论并自动回复
- 永久运行，无需干预

**自定义发布时间**（编辑 `auto_substack_forever.py`）：
```python
PUBLISH_DAY = 0  # 0=周一, 1=周二...6=周日
PUBLISH_HOUR = 9  # 发布时间（24小时制）
COMMENT_CHECK_HOURS = [10, 16]  # 评论检查时间
```

---

### 功能2: 自动回答评论

#### 回答风格特点

根据用户要求，回答系统具有以下特点：

✅ **简短、热情但不过分**
```
❌ 避免: "This is absolutely amazing! You are so smart! Our product will definitely solve all your problems!"
✅ 推荐: "哈哈说得太对了👍 我们测试时也发现这个问题，后来用speaker ID解决了"
```

✅ **可用网络用语**
```
示例: "卧槽确实"、"绷不住了"、"牛逼"、"这个方案很6"
```

✅ **回答相关领域问题，不直接推产品**
```
❌ 避免: "Use HireMeAI! Sign up now at https://..."
✅ 推荐: "面试紧张很正常，关键是提前准备好STAR框架。我们在做AI辅助时也发现，准备好的人更放松"
```

✅ **自然提及产品（非强制）**
```
✅ 示例: "我们在测试HireMeAI时也遇到这个，后来发现...（技术细节）"
```

#### 立即检查并回复评论

```bash
python3 auto_substack_forever.py --mode comments
```

**流程**：
1. 抓取最近3篇文章的评论
2. AI判断哪些评论值得回答
3. 生成简短、有价值的回答
4. 自动发布回复
5. 记录已回答评论（避免重复）

#### 回答逻辑

系统会回答以下类型的评论：
- 包含问题词（how, why, what, 如何, 为什么等）
- 提及相关主题（interview, job, AI, career, 面试等）
- 长度 >10 字符

跳过的评论：
- 太短的评论（<10字符）
- 已回答过的评论
- 完全不相关的话题

---

## 🧪 测试系统

在正式使用前，建议先测试：

```bash
python3 test_substack_system.py
```

**测试内容**：
1. ✅ 文章生成测试（AI生成）
2. ✅ 回答生成测试（针对多种评论）
3. ✅ 发布器测试（不实际发布，保存为草稿）

---

## 📂 文件说明

### 核心脚本
- `auto_substack_forever.py` - **主脚本**，永久运行系统
- `substack_login_and_save_auth.py` - 登录并保存认证信息

### 模块文件（src/）
- `src/substack_poster.py` - 文章发布器类
- `src/substack_answer_bot.py` - 评论回答机器人类
- `src/social_media_poster_base.py` - 基类（已有）

### 测试与文档
- `test_substack_system.py` - 完整测试脚本
- `SUBSTACK_SYSTEM_GUIDE.md` - 本文档

### 数据文件（自动生成）
- `substack_auth.json` - 认证信息（cookies）
- `substack_published_articles.json` - 已发布文章列表
- `substack_answered_comments.json` - 已回答评论ID

---

## 🎯 实际使用场景

### 场景1: Build in Public 长期运行

```bash
# 1. 首次配置
python3 substack_login_and_save_auth.py

# 2. 测试系统
python3 test_substack_system.py

# 3. 启动永久运行
nohup python3 auto_substack_forever.py --mode forever > substack.log 2>&1 &
```

**效果**：
- 每周一早上9点自动发布新文章
- 每天2次自动回复评论
- 完全自动化，持续build in public

### 场景2: 手动发布单篇文章

```bash
python3 auto_substack_forever.py --mode generate
```

**适用于**：
- 想要立即发布一篇文章
- 测试文章生成效果
- 手动控制发布节奏

### 场景3: 只做评论回复

```bash
python3 auto_substack_forever.py --mode comments
```

**适用于**：
- 已经手动发布了文章
- 只想使用自动回答功能
- 批量处理积压的评论

---

## 🔧 高级配置

### 自定义文章生成Prompt

编辑 `auto_substack_forever.py` 中的 `generate_substack_article()` 函数：

```python
def generate_substack_article(self, week_number: int) -> dict:
    prompt = f"""
    你的自定义prompt...

    要求：
    - 字数：800-1200字
    - 格式：标题 + 副标题 + 正文
    - 主题：{你的主题}

    输出JSON格式...
    """
```

### 自定义回答风格

编辑 `src/substack_answer_bot.py` 中的 `generate_answer()` 函数：

```python
product_context = """
你是{你的产品}的创始人...

回答风格：
- 简短（50-150字）
- {你的风格要求}
- 可用网络用语：{你允许的用语}
"""
```

### 调整发布频率

编辑 `auto_substack_forever.py`：

```python
# 改为每周三发布
PUBLISH_DAY = 2  # 0=周一, 2=周三

# 改为晚上8点发布
PUBLISH_HOUR = 20

# 每天检查3次评论（早中晚）
COMMENT_CHECK_HOURS = [9, 14, 20]

# 每次最多回复10条评论
MAX_REPLIES_PER_CHECK = 10
```

---

## 🚨 常见问题

### Q1: 登录失败 / Cookies过期

**解决**：重新运行登录脚本
```bash
python3 substack_login_and_save_auth.py
```

### Q2: 生成的文章太长 / 太短

**解决**：调整prompt中的 `max_tokens` 参数
```python
# auto_substack_forever.py
response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=2000,  # 调整这个值：1000-3000
    ...
)
```

### Q3: 回答风格不符合预期

**解决**：
1. 检查 `src/substack_answer_bot.py` 中的 `product_context`
2. 增加更多示例到prompt
3. 调整 `temperature` 参数（0.7 = 保守，0.9 = 创意）

### Q4: 评论抓取失败

**可能原因**：
- Substack UI更新，选择器失效
- 网络问题

**解决**：
1. 查看截图文件（自动生成）
2. 更新 `src/substack_answer_bot.py` 中的选择器
3. 提issue反馈

### Q5: 如何停止永久运行？

```bash
# 找到进程ID
ps aux | grep auto_substack_forever.py

# 停止进程
kill <PID>

# 或直接按 Ctrl+C（如果在前台运行）
```

---

## 💡 最佳实践

### 1. 文章发布频率

**推荐**：每周1篇（周一发布）
- 给读者期待感
- 保证质量
- 有足够时间收集反馈

**避免**：每天发布
- 容易疲劳
- 质量下降
- 读者审美疲劳

### 2. 评论回复策略

**推荐**：
- 每天检查2次（上午+下午）
- 每次最多回复5条
- 优先回答有深度的问题

**避免**：
- 立即回复所有评论（看起来像机器人）
- 回复太频繁（可能被标记为spam）

### 3. 内容主题规划

**建议轮换**：
- Week 1: 技术突破
- Week 2: 用户反馈
- Week 3: 产品迭代
- Week 4: 行业洞察
- Week 5: 失败经验
- ...循环

### 4. 数据监控

定期检查：
```bash
# 查看已发布文章
cat substack_published_articles.json | python3 -m json.tool

# 查看已回答评论数量
cat substack_answered_comments.json | wc -l

# 查看运行日志
tail -f substack.log
```

---

## 📊 成本估算

基于 GPT-4o-mini 定价（截至2025年）：

**每周成本**：
- 生成1篇文章（~1500 tokens）：约 $0.001
- 回复14次评论检查（每次5条，平均150 tokens/回复）：约 $0.01
- **总计**：约 **$0.011 / 周** ≈ **$0.05 / 月**

**对比人工**：
- 写1篇文章：2-4小时
- 回复评论：每天30分钟
- 总时间节省：**每周 10+ 小时**

---

## 🔗 相关资源

### Substack 官方文档
- [Substack Writer Guide](https://support.substack.com/hc/en-us/categories/360004764232-For-writers)
- [Substack Best Practices](https://on.substack.com/p/grow-1)

### Build in Public 参考
- [Indie Hackers](https://www.indiehackers.com/)
- [公开构建案例研究](https://trends.vc/trends-0050-build-in-public/)

### 文章格式灵感
- 用户提供的高转化率模板（已集成到系统）
- [Patrick McKenzie的写作风格](https://www.kalzumeus.com/)

---

## 📧 支持

如有问题，请：
1. 查看本文档"常见问题"部分
2. 运行 `python3 test_substack_system.py` 诊断问题
3. 查看错误截图（自动生成）
4. 提交 Issue 到项目仓库

---

## ✅ 检查清单

开始使用前，确认：
- [ ] 已安装 Python 3.8+
- [ ] 已安装依赖（`playwright`, `openai`）
- [ ] 已设置 `OPENAI_API_KEY` 环境变量
- [ ] 已配置 `SUBSTACK_DOMAIN`
- [ ] 已运行 `substack_login_and_save_auth.py`
- [ ] `substack_auth.json` 文件存在
- [ ] 已运行 `test_substack_system.py` 测试通过

全部完成？开始使用：
```bash
python3 auto_substack_forever.py --mode forever
```

🎉 **享受自动化的Build in Public之旅！**
