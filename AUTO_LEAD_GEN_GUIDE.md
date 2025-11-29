# 🤖 全自动Lead Generation系统 - 使用指南

## 🎯 系统概述

这是一个**完全自动化**的潜在客户生成系统！

### 工作流程

```
产品文档（PDF/MD/URL）
        ↓
   文档解析
        ↓
   AI分析（Product Brain）
   - 提取关键词
   - 识别目标用户画像
   - 生成搜索策略
        ↓
   自动找种子账号
   - AI推荐相关Twitter账号
   - 基于行业和关键词
        ↓
   智能爬取
   - 从种子账号爬取粉丝
   - 提取所有联系方式
   - 人性化行为（不被检测）
        ↓
   智能过滤和评分
   - 相关性评分
   - 联系信息质量评分
        ↓
   输出高质量leads
   - CSV + JSON
   - 包含所有联系方式
```

---

## 🚀 快速开始

### 步骤1：准备产品文档

创建一个Markdown文件描述你的产品：

```markdown
# 我的产品

## 产品简介
我们提供...

## 目标客户
- 车队管理员
- 物流公司
- ...

## 核心功能
1. 功能A
2. 功能B
...
```

或者使用：
- PDF文件
- DOCX文件
- 网页URL

### 步骤2：运行自动化系统

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate

# 基本用法
python src/auto_lead_generator.py product.md

# 高级用法（自定义参数）
python src/auto_lead_generator.py product.pdf 200 15
#                                    文档路径  每个账号爬多少 最多几个种子账号
```

### 步骤3：等待完成

系统会自动：
1. ✅ 解析产品文档
2. ✅ AI分析提取关键信息
3. ✅ 找到10-30个相关Twitter账号
4. ✅ 爬取每个账号的粉丝
5. ✅ 提取所有联系方式
6. ✅ 智能过滤和评分
7. ✅ 导出高质量leads

### 步骤4：查看结果

```bash
# 查看输出文件夹
ls auto_leads/

# 打开CSV文件
open auto_leads/leads_20250116_143022.csv
```

---

## 📊 输出文件

### 1. leads_YYYYMMDD_HHMMSS.csv

**主要字段：**
- `username` - Twitter用户名
- `name` - 显示名称
- `bio` - 个人简介
- `email` - 主要邮箱
- `all_emails` - 所有找到的邮箱（逗号分隔）
- `phones` - 电话号码
- `websites` - 个人网站
- `linkedin` - LinkedIn账号
- `github` - GitHub账号
- `profile_url` - Twitter主页
- `scraped_from` - 从哪个账号爬取
- `relevance_score` - 相关性评分（0-100）
- `contact_quality_score` - 联系信息质量（0-100）
- `total_score` - 总评分（0-100）

### 2. leads_YYYYMMDD_HHMMSS.json

完整的JSON数据，包含所有提取的信息。

### 3. product_analysis.json

AI分析的产品信息：
- 关键词
- 目标用户画像
- 行业
- 痛点
- 使用场景
- 推荐的Twitter标签
- 等等...

### 4. summary_YYYYMMDD_HHMMSS.json

运行总结：
- 总lead数
- 有邮箱的数量
- 有电话的数量
- 高质量lead数量

---

## 💡 使用示例

### 示例1：使用示例产品文档

```bash
# 使用提供的示例文件
python src/auto_lead_generator.py example_product.md

# 预期结果：
# - 找到15个相关账号（EV、fleet management相关）
# - 爬取1500个粉丝（每个100）
# - 过滤后约300-500个高质量leads
# - 其中50-150个有邮箱
```

### 示例2：从网站URL

```bash
# 直接使用你的产品网站
python src/auto_lead_generator.py https://myproduct.com/about 150 20
```

### 示例3：使用PDF

```bash
# 使用产品宣传册
python src/auto_lead_generator.py product_brochure.pdf 200 15
```

---

## 🎯 工作原理

### 1. 文档解析器（DocumentParser）

**支持格式：**
- ✅ PDF (.pdf)
- ✅ Word (.docx)
- ✅ Markdown (.md)
- ✅ 纯文本 (.txt)
- ✅ HTML文件
- ✅ 网页URL

**功能：**
- 提取文本
- 清理格式
- 分块处理

### 2. Product Brain（AI分析）

**使用Anthropic Claude分析产品文档**

**提取信息：**
- 10-15个关键词
- 3-5类目标用户画像
- 2-5个相关行业
- 3-5个痛点
- 3-5个使用场景
- 5-10个竞争对手关键词
- 10-15个Twitter标签
- 应该爬取的账号类型

**AI Prompt示例：**
```
"分析以下产品描述，提取关键信息..."
```

**输出JSON格式：**
```json
{
  "keywords": ["EV", "fleet", "telematics", ...],
  "target_personas": ["fleet manager", "logistics", ...],
  "industries": ["automotive", "logistics", ...],
  ...
}
```

### 3. 自动找种子账号

**AI推荐相关Twitter账号：**

基于产品分析，AI会推荐：
- 行业媒体（如：techcrunch, theverge）
- 技术博主和意见领袖
- 相关公司官方账号
- 行业组织和社区
- 活跃的从业者

**示例（电动车队管理产品）：**
```
@tesla
@rivian
@evcharging
@fleetowner
@logisticstech
...
```

### 4. 智能爬取

**使用人性化Playwright爬虫：**
- 随机鼠标移动
- 不规则滚动
- 模拟阅读时间
- 随机分神
- 完全不可预测

**每个种子账号：**
- 爬取N个粉丝（默认100）
- 提取基本信息
- 间隔1分钟再爬下一个账号

### 5. 联系方式提取（ContactExtractor）

**从多个来源提取：**

#### 邮箱提取：
- 标准格式：john@example.com
- 混淆格式：john [at] example [dot] com
- 带空格：john @ example . com
- 所有变体

#### 电话提取：
- 国际格式：+1-234-567-8900
- 美国格式：(234) 567-8900
- 简单格式：234-567-8900
- 各种分隔符

#### 网站提取：
- 完整URL：https://mysite.com
- 域名：mysite.com
- 生成潜在联系页面URL

#### 社交媒体：
- LinkedIn账号
- GitHub账号
- Instagram账号
- Telegram账号
- Discord账号

### 6. 智能过滤和评分

**相关性评分（0-100）：**
- 检查bio中的关键词（+10分/个）
- 检查目标用户画像（+15分/个）
- 检查行业（+12分/个）

**联系信息质量（0-100）：**
- 有邮箱：+50分
- 有电话：+20分
- 有网站：+15分
- 有社交媒体：+3分/个
- 有联系指示词：+2分/个

**总评分：**
```
总分 = 相关性 × 0.6 + 联系质量 × 0.4
```

**过滤条件：**
- 总分 > 20 或
- 有任何联系信息

---

## 📈 性能和预期结果

### 时间估算

| 种子账号数 | 每个爬取 | 总leads | 预计时间 |
|----------|---------|--------|---------|
| 5个 | 100 | 500 | 30-45分钟 |
| 10个 | 100 | 1000 | 1-1.5小时 |
| 15个 | 200 | 3000 | 3-4小时 |
| 20个 | 200 | 4000 | 4-5小时 |

**注意：** 包含人性化延迟，确保安全

### 质量预期

**典型结果（以1000个爬取的粉丝为例）：**

- 原始leads: 1000
- 过滤后: 300-500（30-50%）
- 有邮箱: 75-150（15-30%）
- 有电话: 20-50（4-10%）
- 有网站: 100-200（20-40%）
- 高质量（评分>50）: 100-200（20-40%）

**邮箱率取决于：**
- 目标账号类型（B2B高，C2C低）
- 行业（技术/创业高，娱乐低）
- 种子账号质量

---

## 🔧 高级配置

### 修改参数

编辑 `auto_lead_generator.py`:

```python
# 修改每个账号爬取的粉丝数
followers_per_account = 200  # 默认100

# 修改种子账号数量
max_seed_accounts = 20  # 默认10

# 修改评分阈值
if total_score > 30:  # 默认20，提高阈值=更严格
    qualified_leads.append(lead)
```

### 使用不同的AI

```python
# 使用OpenAI而不是Anthropic
brain = ProductBrain(api_provider="openai")
```

### 自定义种子账号

```python
# 不使用AI推荐，手动指定
seed_accounts = [
    "mycompetitor1",
    "mycompetitor2",
    "industry_leader",
    "tech_influencer"
]
```

---

## 💰 成本估算

### AI API调用

**Anthropic Claude：**
- 文档分析：1次（~$0.05-0.10）
- 种子账号推荐：1次（~$0.03-0.05）
- **总计：** ~$0.08-0.15/次运行

**OpenAI GPT-4：**
- 类似成本，略高

### 总成本

**单次运行（1000个leads）：**
- AI成本：$0.10
- 时间成本：1-2小时人工监督
- **总计：** 几乎免费

**vs 购买leads：**
- 市场价：$5-50/lead
- 1000个leads：$5,000-50,000
- **你的成本：** $0.10

**ROI：** 50,000-500,000倍！

---

## 🎯 最佳实践

### 1. 优化产品文档

**好的产品文档应该包含：**
- ✅ 清晰的产品描述
- ✅ 明确的目标客户
- ✅ 核心功能和优势
- ✅ 使用场景
- ✅ 行业术语和关键词

**示例对比：**

❌ **不好：**
```
我们的产品很好，欢迎使用。
```

✅ **好：**
```
# FleetEV - 电动车队管理

我们为物流公司和车队管理员提供AI驱动的
电动汽车车队管理平台，优化充电、路线和维护。

目标客户：
- 50-500辆车的物流公司
- 车队管理员
- 共享出行运营商
...
```

### 2. 选择合适的参数

**小规模测试：**
```bash
python src/auto_lead_generator.py product.md 50 5
# 5个账号 × 50 = 250 leads
# 时间：15-20分钟
# 用于测试系统是否正常
```

**中等规模：**
```bash
python src/auto_lead_generator.py product.md 100 10
# 10个账号 × 100 = 1000 leads
# 时间：1-1.5小时
# 推荐日常使用
```

**大规模：**
```bash
python src/auto_lead_generator.py product.md 200 20
# 20个账号 × 200 = 4000 leads
# 时间：4-5小时
# 用于建立大型数据库
```

### 3. 分批运行

```bash
# 上午运行
python src/auto_lead_generator.py product.md 100 5

# 下午运行
python src/auto_lead_generator.py product.md 100 5

# 晚上运行
python src/auto_lead_generator.py product.md 100 5

# 每天收集1500个leads，安全可靠
```

### 4. 处理结果

```python
import pandas as pd

# 读取结果
df = pd.read_csv('auto_leads/leads_20250116_143022.csv')

# 只看高质量的
high_quality = df[df['total_score'] > 50]

# 只看有邮箱的
with_email = df[df['all_emails'].notna()]

# 按评分排序
top_leads = df.sort_values('total_score', ascending=False).head(100)

# 导出特定子集
top_leads.to_csv('top_100_leads.csv', index=False)
```

---

## 🔍 故障排除

### 问题1：AI分析失败

**错误：** "ANTHROPIC_API_KEY not found"

**解决：**
```bash
# 检查.env文件
cat .env | grep ANTHROPIC

# 如果没有，添加
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
```

### 问题2：找不到种子账号

**现象：** AI推荐的账号都不存在

**解决：**
- 改进产品文档（添加更多关键词）
- 手动指定种子账号
- 使用行业知名账号

### 问题3：爬取失败

**错误：** "auth.json not found"

**解决：**
```bash
# 重新创建auth.json
python create_auth_manual.py
```

### 问题4：没有找到邮箱

**这是正常的！** 只有15-30%的用户公开邮箱。

**提高方法：**
- 爬取B2B相关账号（邮箱率更高）
- 增加爬取数量
- 使用其他渠道（LinkedIn）

---

## 🎉 总结

**你现在拥有：**

- ✅ 完全自动化的Lead生成系统
- ✅ AI驱动的目标账号发现
- ✅ 智能联系方式提取
- ✅ 相关性和质量评分
- ✅ 人性化爬取（不被检测）
- ✅ 完整的数据导出

**可以做到：**

- 🚀 从产品文档到高质量leads，完全自动化
- 📧 自动提取所有联系方式（邮箱、电话、网站、社交媒体）
- 🎯 智能过滤，只保留相关的高质量leads
- 💰 成本几乎为零（只有AI API费用）
- 🔒 安全可靠，长期使用

**立即开始：**

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate
python src/auto_lead_generator.py example_product.md
```

**祝你自动化Lead Generation成功！** 🎊
