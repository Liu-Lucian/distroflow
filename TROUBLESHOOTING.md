# 🔧 故障排除指南 - Troubleshooting Guide

## 目录 (Table of Contents)

1. [邮箱发现率低 - Low Email Discovery Rate](#1-邮箱发现率低)
2. [AI分析失败 - AI Analysis Fails](#2-ai分析失败)
3. [Twitter登录问题 - Twitter Login Issues](#3-twitter登录问题)
4. [爬取速度慢 - Slow Scraping Speed](#4-爬取速度慢)
5. [账号被限制 - Account Restricted](#5-账号被限制)
6. [网站爬取失败 - Website Scraping Fails](#6-网站爬取失败)
7. [内存/性能问题 - Memory/Performance Issues](#7-内存性能问题)

---

## 1. 邮箱发现率低

### 问题: 爬取了500个粉丝，只找到0-5个邮箱 (<1%)

#### ✅ 解决方案 1: 检查种子账号类型

**问题诊断:**
```bash
# 查看最近一次的产品分析
cat auto_leads/product_analysis.json
```

查看 AI 推荐的种子账号。如果看到这些类型，邮箱率会很低：
- ❌ @techcrunch, @theverge (媒体)
- ❌ @elonmusk, @billgates (名人)
- ❌ @cnn, @bbc (新闻)
- ❌ @spotify, @netflix (娱乐)

**修复:**
修改你的产品文档，强调 B2B 用户画像：

```markdown
## 目标客户
- **SaaS Founders** (不是 "创业者")
- **B2B Sales Leaders** (不是 "销售人员")
- **Startup CTOs** (不是 "技术人员")

## 相关社区
- @ycombinator
- @indiehackers
- @MicroConf
- @stripe
```

**验证:**
```bash
# 使用优化的文档测试
python src/auto_lead_generator.py saas_product_optimized.md 50 3

# 应该看到这些种子账号:
# @ycombinator, @indiehackers, @stripe, @notion
```

**预期改进:** 1% → 20-30%

---

#### ✅ 解决方案 2: 启用详细日志检查网站爬取

**问题诊断:**
网站爬取可能在失败但没有显示详细错误。

**修复:**
编辑 `src/auto_lead_generator.py`，在文件开头修改日志级别：

```python
# 第 19 行
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')
```

**运行测试:**
```bash
python src/auto_lead_generator.py saas_product_optimized.md 50 3 2>&1 | tee debug.log
```

**查看日志:**
```bash
# 查找网站爬取尝试
grep "Trying website" debug.log

# 查找成功提取
grep "Found.*emails on website" debug.log

# 查找错误
grep "Error" debug.log
```

**常见问题:**
- "Timeout" → 网站太慢，增加 timeout 参数
- "Connection refused" → 网站阻止爬虫，需要更好的 headers
- "404" → 个人网站不存在

---

#### ✅ 解决方案 3: 增加网站爬取超时时间

**修复:**
编辑 `src/auto_lead_generator.py` 第 185 行:

```python
# 之前:
website_contacts = self.contact_extractor.extract_from_website(website, timeout=5)

# 修改为:
website_contacts = self.contact_extractor.extract_from_website(website, timeout=10)
```

---

#### ✅ 解决方案 4: 手动测试邮箱提取

**测试脚本:**
```python
# test_email_extraction.py
from src.contact_extractor import ContactExtractor

extractor = ContactExtractor()

# 测试 bio
test_bio = "Founder @mystartup | Contact: hello@example.com | DM for collabs"
contacts = extractor.extract_all_contacts(test_bio)
print(f"Emails: {contacts['emails']}")
print(f"Websites: {contacts['websites']}")

# 测试网站爬取
if contacts['websites']:
    website_contacts = extractor.extract_from_website(contacts['websites'][0])
    print(f"Website emails: {website_contacts['emails']}")
```

**运行:**
```bash
python test_email_extraction.py
```

如果这个测试失败，说明 contact_extractor 有问题。

---

## 2. AI分析失败

### 问题: "NameError: name 're' is not defined"

#### ✅ 解决方案: 检查 re 模块导入

**验证问题:**
```bash
grep "import re" src/product_brain.py
```

**应该看到:**
```python
import os
import re  # ← 这行必须存在
import json
```

**如果没有，添加:**
```bash
# 编辑文件
nano src/product_brain.py

# 在第7行添加: import re
```

**或使用 sed 自动修复:**
```bash
sed -i '' '6a\
import re' src/product_brain.py
```

---

### 问题: "ANTHROPIC_API_KEY not found"

#### ✅ 解决方案: 检查 .env 文件

**验证:**
```bash
cat .env | grep ANTHROPIC_API_KEY
```

**应该看到:**
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

**如果没有:**
```bash
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

**获取 API Key:**
1. 访问 https://console.anthropic.com/
2. 创建账号
3. 生成 API Key
4. 复制到 .env

---

## 3. Twitter登录问题

### 问题: "此浏览器或应用可能不安全"

#### ✅ 解决方案 1: 手动登录一次

**步骤:**
```bash
# 使用非 headless 模式
python create_auth_manual.py
```

这会打开真实浏览器，你手动登录一次。登录成功后会保存到 `auth.json`。

**之后使用:**
```bash
# 正常运行即可，会使用保存的登录状态
python src/auto_lead_generator.py product.md
```

---

#### ✅ 解决方案 2: 检查 auth.json

**验证:**
```bash
cat auth.json
```

**应该看到:**
```json
{
  "cookies": [
    {
      "name": "auth_token",
      "value": "...",
      "domain": ".twitter.com"
    }
  ]
}
```

**如果文件为空或格式错误:**
```bash
rm auth.json
python create_auth_manual.py
```

---

### 问题: "Login timeout"

#### ✅ 解决方案: 增加超时时间

**编辑 `src/twitter_scraper_playwright.py`:**

```python
# 第 96 行
try:
    page.wait_for_selector('a[href="/home"]', timeout=60000)  # 改为 60 秒
```

---

## 4. 爬取速度慢

### 问题: 爬取100个粉丝需要10分钟以上

这是**正常的**！人类化行为会慢。

**当前速度:**
- 每个粉丝: 4-6 秒
- 100个粉丝: 7-10 分钟
- 1000个粉丝: 70-100 分钟

**为什么这么慢？**
- ✅ 随机滚动速度
- ✅ 阅读暂停
- ✅ 随机分心（10%概率暂停2-20秒）
- ✅ 鼠标移动模拟

#### ⚠️ 不推荐: 加速（可能被检测）

**如果你愿意承担风险:**

编辑 `src/twitter_scraper_playwright.py`:

```python
# 减少阅读时间 (第 186 行)
reading_time = random.uniform(0.2, 0.5)  # 之前: 0.5-3s

# 减少分心概率 (第 189 行)
if random.random() < 0.02:  # 之前: 0.1

# 减少滚动暂停 (第 318 行)
time.sleep(random.uniform(0.3, 0.8))  # 之前: 0.8-2.5s
```

**风险:** 更容易被 Twitter 检测为机器人。

---

## 5. 账号被限制

### 问题: "Rate limit exceeded" 或 "Account suspended"

#### ✅ 解决方案 1: 减少爬取量

**推荐限制:**
- 每小时: <500 粉丝
- 每天: <2000 粉丝
- 账号间延迟: 60-120 秒

**修改配置:**
```bash
# 小规模测试
python src/auto_lead_generator.py product.md 50 5

# 而不是
python src/auto_lead_generator.py product.md 500 20  # ❌ 太激进
```

---

#### ✅ 解决方案 2: 增加延迟

**编辑 `src/auto_lead_generator.py` 第 221 行:**

```python
# 之前:
delay = 60  # 1分钟

# 修改为:
delay = 120  # 2分钟
```

---

#### ✅ 解决方案 3: 使用多个账号轮换

**创建:**
```bash
python create_auth_manual.py  # 账号1 → auth.json
python create_auth_manual.py  # 账号2 → 手动重命名为 auth2.json
python create_auth_manual.py  # 账号3 → 手动重命名为 auth3.json
```

**修改脚本使用不同账号:**
```python
# 账号1
generator = AutoLeadGenerator(auth_file="auth.json")
generator.run_full_pipeline("product.md", 100, 5)

# 等待1小时

# 账号2
generator = AutoLeadGenerator(auth_file="auth2.json")
generator.run_full_pipeline("product.md", 100, 5)
```

---

## 6. 网站爬取失败

### 问题: 尝试访问个人网站但没找到邮箱

#### ✅ 解决方案 1: 检查 requests 和 beautifulsoup4

**验证安装:**
```bash
pip list | grep -E "requests|beautifulsoup4"
```

**应该看到:**
```
beautifulsoup4    4.12.2
requests          2.31.0
```

**如果没有:**
```bash
pip install requests beautifulsoup4
```

---

#### ✅ 解决方案 2: 改进 User-Agent

有些网站会阻止爬虫。

**编辑 `src/contact_extractor.py` 第 228 行:**

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}
```

---

#### ✅ 解决方案 3: 手动测试网站爬取

**测试脚本:**
```python
from src.contact_extractor import ContactExtractor

extractor = ContactExtractor()
url = "https://example.com"  # 替换为实际URL

contacts = extractor.extract_from_website(url)
print(contacts)
```

**常见错误处理:**
- "SSL Error" → 使用 `verify=False` (不安全)
- "Timeout" → 增加 timeout
- "403 Forbidden" → 网站阻止爬虫

---

## 7. 内存/性能问题

### 问题: Python进程占用大量内存

#### ✅ 解决方案: 批量处理并清理

**编辑 `src/auto_lead_generator.py`:**

```python
def _scrape_all_seeds(self, seed_accounts, followers_per_account):
    for i, account in enumerate(seed_accounts):
        # ... 爬取代码 ...

        # 每爬取5个账号，保存一次
        if (i + 1) % 5 == 0:
            self._save_intermediate_results()
            self.all_leads = []  # 清空内存
```

---

### 问题: 浏览器崩溃

#### ✅ 解决方案: 定期重启浏览器

**编辑 `src/auto_lead_generator.py`:**

```python
# 每爬取10个账号，重启浏览器
if (i + 1) % 10 == 0:
    self.scraper.close()
    time.sleep(5)
    self.scraper = TwitterPlaywrightScraper(headless=self.headless, auth_file=self.auth_file)
    self.scraper.start()
```

---

## 快速诊断检查清单

运行出问题时，按顺序检查：

### ✅ 环境检查
```bash
# 1. Python 版本
python --version  # 应该 >= 3.8

# 2. 依赖安装
pip list | grep -E "playwright|anthropic|pandas|beautifulsoup4"

# 3. Playwright 浏览器
playwright install chromium

# 4. 环境变量
cat .env | grep ANTHROPIC_API_KEY

# 5. 登录状态
test -f auth.json && echo "✓ auth.json exists" || echo "❌ Missing auth.json"
```

### ✅ 功能检查
```bash
# 1. 测试邮箱提取
python -c "from src.contact_extractor import ContactExtractor; print(ContactExtractor().extract_emails('test@example.com'))"

# 2. 测试AI分析
python -c "from src.product_brain import ProductBrain; print('✓ ProductBrain OK')"

# 3. 测试文档解析
python -c "from src.document_parser import DocumentParser; print('✓ DocumentParser OK')"
```

### ✅ 小规模测试
```bash
# 最小测试: 1个账号，10个粉丝
python src/auto_lead_generator.py saas_product_optimized.md 10 1
```

如果这个测试成功，说明系统正常，可以扩大规模。

---

## 获取帮助

如果以上方案都不起作用：

1. **启用详细日志:**
   ```bash
   python src/auto_lead_generator.py product.md 2>&1 | tee full_debug.log
   ```

2. **检查日志中的错误信息**

3. **查看最近的结果文件:**
   ```bash
   ls -lt auto_leads/
   cat auto_leads/product_analysis.json
   ```

4. **常见日志关键词:**
   - "NameError" → Python 导入问题
   - "Timeout" → 网络或速度问题
   - "Rate limit" → Twitter 限制
   - "KeyError" → 数据结构问题

---

## 快速修复命令

**重置一切:**
```bash
# 删除所有缓存和结果
rm -rf auto_leads/ test_results/
rm -f auth.json

# 重新安装依赖
pip install -r requirements.txt
playwright install chromium

# 重新登录
python create_auth_manual.py

# 小规模测试
python src/auto_lead_generator.py saas_product_optimized.md 50 3
```

这会给你一个干净的开始。
