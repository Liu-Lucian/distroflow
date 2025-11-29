# 测试：真实浏览器 vs Playwright

## 目的
测试 Product Hunt 的产品链接是否只在真实浏览器中可见

## 步骤

### 1. 在真实浏览器中测试

1. 打开 Chrome/Safari
2. 访问 https://www.producthunt.com
3. **等待 15 秒**让页面完全加载
4. 按 F12 打开 Console
5. 粘贴以下代码：

```javascript
// 测试代码
const links = document.querySelectorAll('a[href*="/posts/"]');
console.log('找到链接数:', links.length);

const products = Array.from(links)
    .filter(a => !a.href.includes('/new'))
    .slice(0, 10)
    .map(a => ({
        url: a.href.split('?')[0],
        text: a.textContent.trim().substring(0, 50)
    }));

console.log('产品列表:', products);
console.table(products);
```

### 2. 记录结果

如果真实浏览器中**找到了产品链接**（> 1 个），但 Playwright 找不到，这说明：

- ✅ 产品数据**确实存在于 DOM 中**
- ❌ Playwright 被 Product Hunt 的反爬虫机制屏蔽了

### 3. 可能的解决方案

如果真实浏览器能找到产品：

#### 方案 A: 使用 Selenium + 真实 Chrome 配置
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 使用真实的 Chrome 用户数据
options = Options()
options.add_argument("user-data-dir=/Users/l.u.c/Library/Application Support/Google/Chrome")
options.add_argument("profile-directory=Default")

driver = webdriver.Chrome(options=options)
# ... 然后提取产品
```

#### 方案 B: CDP (Chrome DevTools Protocol) 连接
连接到真实浏览器实例，避开反爬虫检测

#### 方案 C: 浏览器扩展
创建一个简单的 Chrome 扩展，每天自动提取产品并保存

## 关键问题

**Product Hunt 是否能检测 Playwright？**

- Playwright 使用的是 Chromium
- 有特定的指纹特征（navigator.webdriver 等）
- Product Hunt 可能专门屏蔽自动化浏览器

## 下一步

运行真实浏览器测试，查看结果！
