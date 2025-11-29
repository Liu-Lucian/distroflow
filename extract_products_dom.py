#!/usr/bin/env python3
"""
从 Product Hunt 页面 DOM 直接提取产品链接
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
from datetime import datetime

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def extract_products_from_dom(commenter: ProductHuntCommenter) -> list:
    """从页面 DOM 提取产品"""
    print("\n🔍 从 DOM 提取产品...")

    try:
        # 等待页面充分加载
        print("   ⏳ 等待产品加载...")
        time.sleep(5)

        # 滚动页面以触发加载
        for i in range(3):
            commenter.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 3 * " + str(i+1) + ")")
            time.sleep(2)
        commenter.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # 使用 JavaScript 提取所有产品信息
        js_code = """
        () => {
            const products = [];
            const seenSlugs = new Set();

            // 查找所有链接
            const links = document.querySelectorAll('a[href]');

            for (const link of links) {
                const href = link.getAttribute('href');

                // 只要包含 /posts/ 的链接
                if (!href || !href.includes('/posts/')) continue;

                // 跳过特殊页面
                if (href.includes('/posts/new') ||
                    href.includes('/posts/all') ||
                    href.includes('/posts/search')) {
                    continue;
                }

                // 提取 slug
                const match = href.match(/\/posts\/([^/?#]+)/);
                if (!match) continue;

                const slug = match[1];
                if (seenSlugs.has(slug)) continue;
                seenSlugs.add(slug);

                // 尝试从链接附近的元素提取名称和描述
                let name = '';
                let tagline = '';

                // 尝试多种方式获取产品名
                name = link.textContent.trim();

                // 如果名称太长，可能包含了描述
                if (name.length > 50) {
                    name = name.substring(0, 50).trim();
                }

                // 查找父元素中的描述
                let parent = link.parentElement;
                for (let i = 0; i < 3 && parent; i++) {
                    const paragraphs = parent.querySelectorAll('p, div[class*="tagline"], div[class*="description"]');
                    for (const p of paragraphs) {
                        const text = p.textContent.trim();
                        if (text.length > 10 && text.length < 200 && !text.includes('votes') && !text.includes('comments')) {
                            tagline = text;
                            break;
                        }
                    }
                    if (tagline) break;
                    parent = parent.parentElement;
                }

                products.push({
                    slug: slug,
                    name: name || slug,
                    tagline: tagline
                });

                // 限制提取数量
                if (products.length >= 20) break;
            }

            return products;
        }
        """

        raw_products = commenter.page.evaluate(js_code)
        print(f"   ✅ 提取到 {len(raw_products)} 个产品")

        # 转换为标准格式
        products = []
        for p in raw_products:
            slug = p.get('slug', '')
            if not slug:
                continue

            name = p.get('name', slug)
            # 清理名称
            if len(name) > 50:
                name = name[:50].strip()

            tagline = p.get('tagline', '')
            if not tagline:
                tagline = f"{name} - Product from Product Hunt"

            products.append({
                'url': f"https://www.producthunt.com/posts/{slug}",
                'name': name,
                'tagline': tagline,
                'category': 'Various',
                'description': tagline,
                'votes': 0
            })

        print(f"   ✅ 格式化 {len(products)} 个产品")
        return products[:10]  # 只返回前10个

    except Exception as e:
        print(f"   ❌ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=" * 80)
    print("🔍 Product Hunt DOM 提取")
    print("=" * 80)

    commenter = ProductHuntCommenter()

    try:
        # 访问首页
        print("\n🌐 访问 Product Hunt 首页...")
        commenter.setup_browser(headless=True)

        if not commenter.verify_login():
            print("❌ 登录失败")
            return 1

        commenter.page.goto("https://www.producthunt.com", timeout=60000)
        print("⏳ 等待页面加载...")
        time.sleep(10)

        # 提取产品
        products = extract_products_from_dom(commenter)

        commenter.close_browser()

        if not products:
            print("\n❌ 未能提取产品")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "DOM Extraction",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 成功保存 {len(products)} 个产品")
        print("\n📋 产品列表:")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p['name']}")
            print(f"      {p['tagline'][:80]}...")
            print(f"      {p['url']}")

        print("\n" + "=" * 80)
        print("✅ DOM 提取完成！")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        try:
            commenter.close_browser()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())
