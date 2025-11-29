# 🚀 Playwright Twitter Scraper - Quick Start

## 超简单的2步使用方法

### 第1步：首次登录（只做一次）

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate
python login_and_save_auth.py
```

- 会打开浏览器
- 你手动登录 Twitter
- 按 Enter 保存登录状态
- ✅ 完成！以后不用再登录

### 第2步：开始爬取（以后每次用）

```bash
python quick_scrape_playwright.py 用户名 数量
```

**例子：**
```bash
# 爬取 Elon Musk 的 100 个粉丝
python quick_scrape_playwright.py elonmusk 100

# 爬取竞争对手的 500 个粉丝
python quick_scrape_playwright.py competitor 500
```

---

## 📖 完整文档

详细使用指南请看：[PLAYWRIGHT_GUIDE_CN.md](PLAYWRIGHT_GUIDE_CN.md)

---

## ⚡ 为什么用 Playwright？

| 特性 | Playwright (新) | Selenium (旧) |
|------|----------------|---------------|
| 登录 | 只需1次 | 每次都要 |
| 速度 | ⚡⚡⚡ | ⚡⚡ |
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🔧 故障排除

### 找不到 auth.json？
```bash
python login_and_save_auth.py
```

### 登录过期？
```bash
python login_and_save_auth.py
```

### 需要帮助？
查看完整文档：[PLAYWRIGHT_GUIDE_CN.md](PLAYWRIGHT_GUIDE_CN.md)

---

## 📊 输出文件

数据保存在 `exports/` 目录：
- `twitter_用户名_数量_playwright.csv`

包含：用户名、显示名、简介、邮箱、主页链接等

---

## 🎉 完成！

就这么简单！首次登录一次，以后自动爬取。

祝你 lead generation 成功！
