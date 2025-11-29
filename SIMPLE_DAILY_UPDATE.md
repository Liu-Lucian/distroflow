# Product Hunt 每日更新 - 简单方案

## 问题总结

Product Hunt 使用了严格的反爬虫保护：
- 产品不会渲染为 DOM 链接
- 即使等待 30+ 秒也提取不到产品
- 2天前的产品已经 404
- **必须每天更新才能正常运行**

## ✅ 可行方案（30秒完成）

### 方法 1: 使用浏览器扩展（推荐）

1. 在浏览器中访问 https://www.producthunt.com
2. 打开浏览器开发者工具（F12）
3. 在 Console 中粘贴以下代码：

```javascript
// 提取今日产品
const products = [];
const links = document.querySelectorAll('a[href*="/posts/"]');
const seen = new Set();

for (const link of links) {
    const href = link.getAttribute('href');
    if (href && href.includes('/posts/') && !href.includes('/new')) {
        const url = href.startsWith('/') ? 'https://www.producthunt.com' + href : href;
        const cleanUrl = url.split('?')[0];

        if (!seen.has(cleanUrl)) {
            seen.add(cleanUrl);
            const name = link.textContent.trim();

            if (name.length > 2 && name.length < 100) {
                products.push({
                    url: cleanUrl,
                    name: name,
                    tagline: name + " - Product from Product Hunt",
                    category: "Various",
                    description: "Product from Product Hunt Today",
                    votes: 0
                });

                if (products.length >= 10) break;
            }
        }
    }
}

// 生成 JSON
const data = {
    date: new Date().toISOString().split('T')[0],
    source: "Manual Browser Extraction",
    products: products,
    updated_at: new Date().toISOString()
};

// 复制到剪贴板
copy(JSON.stringify(data, null, 2));
console.log(`✅ 已复制 ${products.length} 个产品到剪贴板！`);
console.log('请粘贴到 todays_producthunt_products.json 文件');
```

4. 按回车
5. JSON 已自动复制到剪贴板
6. 粘贴到 `todays_producthunt_products.json` 文件

**总耗时：30 秒**

### 方法 2: 手动输入（备用）

使用现有的辅助脚本：

```bash
python3 update_product_list_helper.py
```

然后输入 5-10 个产品 URL（从 Product Hunt 首页复制）。

## 为什么不能完全自动化？

Product Hunt 的反爬虫措施：
1. 不在 HTML 中渲染产品链接
2. 使用 React/Next.js 动态加载
3. 检测无头浏览器
4. 产品数据存储在复杂的 Apollo GraphQL 结构中
5. 即使用 AI Vision 也无法获取准确的 URL（slug 不可预测）

## 自动化程度

- ✅ 评论内容：100% 自动（AI 生成）
- ✅ 点赞/评论：100% 自动（浏览器自动化）
- ✅ 每日调度：100% 自动（forever 脚本）
- ❌ 产品列表：需要每天 30 秒手动更新

## 推荐工作流

1. **每天早上**（1分钟）：
   ```bash
   # 打开 Product Hunt
   open https://www.producthunt.com

   # 使用浏览器 Console 提取产品（30秒）
   # 粘贴到 todays_producthunt_products.json
   ```

2. **让系统自动运行**：
   ```bash
   # 系统会全天候自动评论
   python3 auto_producthunt_forever.py
   ```

## 结论

由于 Product Hunt 的技术限制，**无法实现 100% 自动化**。

但通过浏览器 Console 方法，每天只需 **30 秒**手动操作，系统就能全自动运行 24 小时。

这是目前最实际的解决方案。
