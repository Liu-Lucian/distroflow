# ⚡ 快速开始 - 2分钟设置指南

## 🎯 目标
2分钟内完成设置，开始爬取 Twitter 粉丝和邮箱！

---

## 📋 步骤

### 1️⃣ 激活环境（每次使用前）

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate
```

### 2️⃣ 首次使用：设置登录（只需一次）

```bash
python setup_login.py
```

**会看到交互式菜单：**
```
🔐 Twitter 登录设置向导

请选择登录方法:

1. 使用 Chrome 配置 (推荐！)
2. 使用 Firefox
3. 使用 Chromium (原方案)
4. 查看详细说明
5. 退出
```

**推荐选择 1** - 最简单，成功率最高

### 3️⃣ 开始爬取！

```bash
# 爬取 Elon Musk 的 100 个粉丝
python quick_scrape_playwright.py elonmusk 100

# 爬取竞争对手的 500 个粉丝
python quick_scrape_playwright.py competitor 500
```

---

## 🎉 完成！

就这么简单！

**输出文件在：** `exports/twitter_用户名_数量_playwright.csv`

---

## 💡 常用命令

```bash
# 小规模测试
python quick_scrape_playwright.py techcrunch 20

# 中等规模
python quick_scrape_playwright.py producthunt 200

# 大规模
python quick_scrape_playwright.py stripe 500
```

---

## 🔧 遇到问题？

### "无法登录" 或 "不安全浏览器"

**最简单的解决方法：**

```bash
# 1. 关闭所有 Chrome 窗口
killall "Google Chrome"

# 2. 重新运行设置
python setup_login.py

# 3. 选择方法 1 (Chrome 配置)
```

### "auth.json 未找到"

```bash
# 重新运行登录设置
python setup_login.py
```

### 登录过期

```bash
# 重新保存登录状态
python setup_login.py
```

---

## 📚 详细文档

- **登录方法对比：** [LOGIN_METHODS_CN.md](LOGIN_METHODS_CN.md)
- **完整使用指南：** [PLAYWRIGHT_GUIDE_CN.md](PLAYWRIGHT_GUIDE_CN.md)
- **原版指南：** [FINAL_GUIDE_CN.md](FINAL_GUIDE_CN.md)

---

## 🚀 实际使用示例

### 场景1：快速测试

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate
python quick_scrape_playwright.py elonmusk 20
```

### 场景2：批量爬取

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate

# 爬取多个账号
python quick_scrape_playwright.py competitor1 300
sleep 600  # 等待10分钟
python quick_scrape_playwright.py competitor2 300
sleep 600
python quick_scrape_playwright.py competitor3 300
```

### 场景3：查看结果

```bash
# 打开导出文件夹
open exports/

# 或在终端查看
cat exports/twitter_elonmusk_100_playwright.csv
```

---

## 📊 预期结果

**100 个粉丝大约需要：**
- 时间：5-8 分钟
- 邮箱发现率：15-30%
- 成功率：95%+

**示例输出：**
```
✓ 成功爬取 100 个粉丝
📧 找到邮箱: 23 (23.0%)

有邮箱的粉丝样例:
1. @user1 - user1@example.com
2. @user3 - user3@startup.com
3. @user15 - contact@business.com
```

---

## 🎯 记住这3个命令

```bash
# 1. 激活环境
source venv/bin/activate

# 2. 首次设置（只需一次）
python setup_login.py

# 3. 开始爬取
python quick_scrape_playwright.py <用户名> <数量>
```

---

**就是这么简单！开始你的 lead generation 之旅吧！** 🎊
