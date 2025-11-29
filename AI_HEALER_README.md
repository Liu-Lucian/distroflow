# 🤖 AI Scraper Healer System

## 概述

AI Scraper Healer 是一个**自适应爬虫自愈系统**，当爬虫遇到问题时，能够：

1. **自动诊断** - 使用GPT-4 Vision分析页面截图
2. **智能修复** - 自动生成新的CSS选择器
3. **自适应行为** - 模拟真人操作，绕过反爬虫检测

## 核心能力

### 💡 1. 智能反检测

- **DOM结构变化自动识别** - 当网站更新UI时，AI自动分析新结构
- **自动修复选择器** - 根据页面截图生成3-5个候选选择器
- **类人操作模拟** - 随机延迟、滚动速率、鼠标轨迹

### 🔍 2. 视觉语义理解

- **页面状态识别** - 理解当前在哪个页面、有什么元素
- **元素定位** - 能够"看懂"哪个是按钮、输入框、链接
- **错误诊断** - 分析为什么选择器失效（元素不存在、权限问题、动态加载等）

### ⚙️ 3. 自我迭代

- **失败学习** - 记录哪些选择器有效，哪些失效
- **策略调整** - 根据成功率动态调整行为模式
- **多重后备方案** - 如果直接点击不行，尝试其他导航路径

### 🧠 4. 数据智能筛选

- **语义过滤** - 理解哪段文本是有价值的信息
- **结构化提取** - 自动识别人名、公司、联系方式等实体
- **价值判断** - 只抓取有意义的数据，过滤噪音

## 使用方法

### 基础用法

```python
from ai_scraper_healer import AIScraperHealer

# 初始化
healer = AIScraperHealer()

# 当遇到问题时，让AI分析页面
analysis = healer.analyze_page_with_vision(
    page=page,  # Playwright page对象
    task_description="Find and click the Message button on Instagram",
    current_url=page.url,
    error_message="Could not find message button with selector 'button:has-text(Message)'"
)

# AI会返回详细分析
print(analysis['problem_analysis'])
print(analysis['suggested_selectors'])
print(analysis['alternative_approach'])
```

### 自动修复

```python
# 尝试AI建议的选择器
success, working_selector = healer.try_selectors_with_ai_guidance(
    page=page,
    ai_analysis=analysis,
    action="click"  # 或 "fill"
)

if success:
    print(f"✅ 修复成功！有效选择器: {working_selector}")
else:
    # 尝试替代方案
    healer.execute_alternative_approach(page, analysis)
```

### 应用类人操作

```python
# AI会建议需要执行的操作（如滚动、延迟、鼠标移动）
healer.apply_human_like_actions(page, analysis)
```

## AI分析输出示例

```json
{
    "page_state": "Instagram post modal is open. User 'startupgrind' profile visible. No direct message button visible in current view.",

    "problem_analysis": "The Message button is not directly accessible from the post modal. Instagram requires navigating to the user's profile page or using the direct message URL /direct/new/",

    "suggested_selectors": [
        {
            "selector": "a[href='/direct/inbox/']",
            "priority": 1,
            "reason": "This is the main direct messages link in Instagram's navigation bar"
        },
        {
            "selector": "div[role='button']:has-text('发消息')",
            "priority": 2,
            "reason": "Chinese UI 'Send Message' button if on profile page"
        },
        {
            "selector": "header a[href*='/startupgrind/']",
            "priority": 3,
            "reason": "Username link in post header - clicking this will go to profile where message button should appear"
        }
    ],

    "alternative_approach": "Navigate directly to https://www.instagram.com/direct/new/ and search for the username in the recipient field. This bypasses the need to find the message button on the profile.",

    "recommended_actions": [
        "Scroll down 300px to check if message button loads below fold",
        "Wait 3 seconds for any lazy-loaded elements",
        "Move mouse randomly to simulate human behavior",
        "Close any overlays or modals that might be blocking elements"
    ],

    "confidence": 0.85
}
```

## 工作流程

```
爬虫遇到问题
    ↓
截取页面screenshot
    ↓
GPT-4 Vision分析
    ├── 理解页面状态
    ├── 诊断问题原因
    └── 生成解决方案
    ↓
尝试AI建议的选择器
    ├── 成功 → 继续执行
    └── 失败 → 尝试替代方案
    ↓
应用类人操作
    ├── 随机延迟
    ├── 滚动加载
    └── 鼠标轨迹
    ↓
完成任务
```

## 环境配置

```bash
# 设置OpenAI API Key
export OPENAI_API_KEY='your-openai-api-key-here'

# 安装依赖
pip install openai playwright
```

## 测试AI Healer

```bash
# 测试Instagram DM with AI自愈
python3 test_ai_instagram_healer.py
```

## 实际应用场景

### 1. Instagram DM自动化
- 自动寻找Message按钮（即使UI改版）
- 识别DM输入框（即使class名变化）
- 处理各种弹窗和overlay

### 2. 多平台通用
- Twitter/X
- TikTok
- LinkedIn
- Reddit
- 任何动态网页

### 3. 反爬虫对抗
- 自动识别验证码类型
- 调整操作节奏避免检测
- 动态生成访问模式

## 优势

### vs 传统爬虫
| 特性 | 传统爬虫 | AI Healer爬虫 |
|------|---------|--------------|
| **适应性** | 网站改版就失效 | 自动适应UI变化 |
| **维护成本** | 需要人工修复选择器 | 自动修复 |
| **成功率** | 固定选择器，容易失效 | 多重后备方案 |
| **反检测** | 易被识别 | 模拟真人行为 |
| **语义理解** | 只能匹配固定文本 | 理解页面含义 |

### 核心技术
- **GPT-4 Vision** - 图像理解 + 语义分析
- **Playwright** - 现代浏览器自动化
- **动态选择器生成** - 基于视觉理解而非硬编码
- **行为模式学习** - 持续优化反检测策略

## 注意事项

⚠️ **合法使用**
- 仅用于授权的数据采集
- 遵守robots.txt和网站TOS
- 尊重用户隐私和平台规则

⚠️ **API成本**
- GPT-4 Vision API调用有成本
- 建议只在失败时调用AI（不要每次都用）
- 可以缓存成功的选择器减少API调用

⚠️ **响应时间**
- AI分析需要2-5秒
- 适合非实时场景
- 可以异步处理多个任务

## 未来扩展

### 🚀 计划中的功能
1. **验证码自动识别** - OCR + GPT-4推理
2. **代理池智能管理** - 检测封禁自动切换
3. **A/B测试选择器** - 实时评估多个方案
4. **集群协同学习** - 多个爬虫共享成功经验
5. **自动生成爬虫代码** - 给URL就能生成完整爬虫

## 作者

Built with 🤖 AI + 🧠 Human Intelligence

## License

MIT - Use at your own risk
