# 🍪 手动保存 Cookies 教程

## 最简单可靠的方法！

使用你日常浏览器的 cookies，不会被 Twitter 检测。

---

## 📋 步骤（5分钟完成）

### 方法A：使用 Chrome 浏览器（推荐）

#### 1. 安装浏览器扩展

打开 Chrome，访问：
```
https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg
```

或者搜索：**EditThisCookie**

点击"添加至 Chrome"安装。

#### 2. 登录 Twitter

在 Chrome 中访问：
```
https://twitter.com
```

正常登录你的账号。

#### 3. 导出 Cookies

1. 点击浏览器右上角的 **EditThisCookie** 图标（饼干图标）
2. 点击底部的 **"导出"** 按钮（Export）
3. Cookies 已复制到剪贴板！

#### 4. 保存到文件

```bash
# 打开终端
cd "/Users/l.u.c/my-app/MarketingMind AI"

# 创建 cookies 文件
nano twitter_cookies.json

# 粘贴刚才复制的内容（Cmd+V）
# 按 Ctrl+X，然后 Y，然后 Enter 保存
```

或者直接用文本编辑器：
```bash
open -a TextEdit twitter_cookies.json
# 粘贴 cookies，保存
```

#### 5. 转换为 Playwright 格式

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate

python convert_cookies.py twitter_cookies.json
```

会自动生成 `auth.json` 文件！

#### 6. 开始爬取

```bash
python quick_scrape_playwright.py elonmusk 50
```

---

### 方法B：使用 Safari 浏览器

#### 1. 在 Safari 中登录 Twitter

访问 https://twitter.com 并登录

#### 2. 打开开发者工具

- 按 `Cmd + Option + C` 打开开发者工具
- 或者菜单栏：**开发 → 显示Web检查器**

（如果没有"开发"菜单，去 **Safari 设置 → 高级 → 勾选"在菜单栏中显示开发菜单"**）

#### 3. 导出 Cookies

1. 在开发者工具中，点击 **"存储"** 标签
2. 展开 **"Cookies"** → 选择 `https://twitter.com`
3. 会看到所有 cookies 列表

#### 4. 手动复制关键 Cookies

创建文件 `twitter_cookies_manual.txt`，复制以下重要的 cookies：

```
auth_token=你的auth_token值
ct0=你的ct0值
```

找到这两个 cookie，复制它们的值。

#### 5. 使用手动转换脚本

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate

python create_auth_manual.py
```

会提示你输入 `auth_token` 和 `ct0` 的值。

---

### 方法C：使用浏览器控制台（最快）

#### 1. 登录 Twitter

在任意浏览器（Chrome/Safari/Firefox）中登录 https://twitter.com

#### 2. 打开控制台

- Chrome: `Cmd + Option + J`
- Safari: `Cmd + Option + C`
- Firefox: `Cmd + Option + K`

#### 3. 运行脚本导出

在控制台中粘贴并运行以下代码：

```javascript
// 获取所有 cookies
let cookies = document.cookie.split('; ').map(c => {
    let [name, value] = c.split('=');
    return {
        name: name,
        value: value,
        domain: '.twitter.com',
        path: '/',
        expires: Date.now() / 1000 + 365 * 24 * 60 * 60,
        httpOnly: false,
        secure: true,
        sameSite: 'None'
    };
});

// 转换为 JSON
let cookiesJson = JSON.stringify(cookies, null, 2);

// 复制到剪贴板
copy(cookiesJson);

console.log('✅ Cookies 已复制到剪贴板！');
console.log('共', cookies.length, '个 cookies');
```

#### 4. 保存到文件

```bash
cd "/Users/l.u.c/my-app/MarketingMind AI"
nano twitter_cookies.json
# 粘贴（Cmd+V）
# 保存（Ctrl+X, Y, Enter）
```

#### 5. 转换格式

```bash
python convert_cookies.py twitter_cookies.json
```

---

## 🔧 我创建的辅助脚本

### 1. `convert_cookies.py`

自动转换 EditThisCookie 格式到 Playwright 格式

```bash
python convert_cookies.py twitter_cookies.json
```

### 2. `create_auth_manual.py`

手动输入关键 cookies 创建 auth.json

```bash
python create_auth_manual.py
```

### 3. `validate_auth.py`

验证 auth.json 是否有效

```bash
python validate_auth.py
```

---

## 📊 三种方法对比

| 方法 | 难度 | 速度 | 推荐度 |
|------|------|------|--------|
| **方法A (EditThisCookie)** | ⭐ 简单 | 2分钟 | ⭐⭐⭐⭐⭐ |
| 方法B (Safari手动) | ⭐⭐ 中等 | 5分钟 | ⭐⭐⭐ |
| 方法C (控制台脚本) | ⭐⭐⭐ 复杂 | 3分钟 | ⭐⭐⭐⭐ |

**推荐：方法A（EditThisCookie）** - 最简单！

---

## ✅ 验证是否成功

```bash
# 检查文件
ls -lh auth.json

# 验证格式
python validate_auth.py

# 测试爬虫
python quick_scrape_playwright.py elonmusk 10
```

---

## 🔍 常见问题

### Q1: EditThisCookie 导出的格式不对？

**A:** 使用转换脚本：
```bash
python convert_cookies.py twitter_cookies.json
```

### Q2: 只知道 auth_token 和 ct0 怎么办？

**A:** 使用手动创建脚本：
```bash
python create_auth_manual.py
```

### Q3: Cookies 多久会过期？

**A:** 通常 1-3 个月。过期后重新导出即可。

### Q4: 如何知道 cookies 是否还有效？

**A:** 运行验证脚本：
```bash
python validate_auth.py
```

---

## 💡 提示

1. **最简单：** 使用 Chrome + EditThisCookie 扩展
2. **导出后立即转换：** `python convert_cookies.py twitter_cookies.json`
3. **定期更新：** Cookies 过期后重新导出
4. **保护隐私：** 不要分享 `auth.json` 文件

---

## 🎯 完整流程（推荐）

```bash
# 1. 在 Chrome 安装 EditThisCookie 扩展

# 2. 登录 Twitter

# 3. 点击扩展图标 → 导出（Cookies 已复制）

# 4. 保存到文件
cd "/Users/l.u.c/my-app/MarketingMind AI"
source venv/bin/activate
nano twitter_cookies.json
# 粘贴，保存

# 5. 转换格式
python convert_cookies.py twitter_cookies.json

# 6. 验证
python validate_auth.py

# 7. 开始爬取
python quick_scrape_playwright.py elonmusk 50
```

---

## 🎉 优势

使用手动 cookies 的好处：

✅ **100% 不会被检测** - 因为是真实浏览器的 cookies
✅ **无需自动化登录** - 避免所有自动化检测
✅ **简单可靠** - 只需要复制粘贴
✅ **长期有效** - Cookies 通常几周到几个月有效

---

下一步：安装 EditThisCookie 扩展开始吧！
