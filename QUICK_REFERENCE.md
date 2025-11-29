# ⚡ 快速参考卡

## 🚀 立即开始（3个命令）

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate
python quick_scrape_playwright.py <用户名> <数量>
```

---

## 📖 常用命令

### 爬取粉丝
```bash
# 小规模测试
python quick_scrape_playwright.py techcrunch 20

# 中等规模
python quick_scrape_playwright.py competitor 100

# 大规模
python quick_scrape_playwright.py target 300
```

### 验证和工具
```bash
# 验证登录状态
python validate_auth.py

# 手动创建auth.json
python create_auth_manual.py

# 转换cookies格式
python convert_cookies.py twitter_cookies.json
```

---

## 📊 性能指标

| 粉丝数 | 时间 | 邮箱数 |
|--------|------|--------|
| 20个 | 1-2分钟 | 3-6个 |
| 100个 | 6-10分钟 | 20-30个 |
| 300个 | 20-30分钟 | 60-90个 |

---

## 🎯 推荐目标账号（高邮箱率）

```bash
python quick_scrape_playwright.py ycombinator 200
python quick_scrape_playwright.py producthunt 200
python quick_scrape_playwright.py stripe 200
python quick_scrape_playwright.py github 200
python quick_scrape_playwright.py indiehackers 200
```

---

## 📁 文件位置

```
auth.json                    # 登录状态
exports/                     # 导出的CSV文件
quick_scrape_playwright.py   # 爬虫脚本
```

---

## 🔧 常见问题

### Q: auth.json过期？
```bash
python create_auth_manual.py
```

### Q: 如何查看结果？
```bash
open exports/
# 或
cat exports/twitter_*.csv
```

### Q: 如何合并多个CSV？
```python
python -c "
import pandas as pd
import glob
files = glob.glob('exports/twitter_*_playwright.csv')
df = pd.concat([pd.read_csv(f) for f in files])
df.to_csv('combined.csv', index=False)
print(f'合并了 {len(files)} 个文件')
"
```

---

## 📚 完整文档

- **START_HERE_CN.md** - 从这里开始
- **FINAL_SUCCESS.md** - 完整总结
- **HUMAN_BEHAVIOR_V2.md** - 人性化行为
- **EASIEST_METHOD_CN.md** - 最简单登录方法

---

## 💡 最佳实践

### 1. 批量爬取
```bash
python quick_scrape_playwright.py account1 100
sleep 3600  # 等待1小时
python quick_scrape_playwright.py account2 100
```

### 2. 每日任务
```bash
# 每天爬取3-4个账号
# 每个100-200粉丝
# 总计: 300-800个潜在客户/天
```

### 3. 数据清洗
```python
import pandas as pd
df = pd.read_csv('exports/twitter_target_100.csv')
emails = df[df['email'].notna()]
emails.to_csv('leads.csv', index=False)
```

---

**就是这么简单！开始使用吧！** 🎉
