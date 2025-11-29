#!/usr/bin/env python3
"""
智能提取 Product Hunt 产品 - 直接从页面元素提取真实链接
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
from datetime import datetime

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def extract_products_from_page(commenter: ProductHuntCommenter) -> list:
    """直接从页面元素提取产品信息"""
    print("\n🔍 从页面元素提取产品...")

    products = []

    try:
        # 方法 1: 查找所有产品标题元素并提取链接
        # Product Hunt 的产品标题通常包含产品名称和链接

        # 尝试多种方式提取
        print("   尝试方法 1: 查找产品标题...")

        # 等待页面加载
        time.sleep(3)

        # 使用 JavaScript 提取所有产品信息
        js_code = """
        () => {
            const products = [];

            // 尝试多种选择器
            const selectors = [
                'div[data-test*="post"]',
                'article',
                'div[class*="item"]',
                'li[data-test*="post"]'
            ];

            for (const selector of selectors) {
                const elements = document.querySelectorAll(selector);

                for (const elem of elements) {
                    // 查找标题链接
                    const titleLink = elem.querySelector('a[href*="/posts/"]');
                    if (!titleLink) continue;

                    const href = titleLink.getAttribute('href');
                    if (!href || href.includes('/posts/new') || href.includes('/posts/all')) continue;

                    // 提取产品名称
                    const nameElem = elem.querySelector('h2, h3, strong, [class*="title"]') || titleLink;
                    const name = nameElem.textContent.trim();

                    // 提取描述
                    const descElem = elem.querySelector('p, div[class*="tagline"], div[class*="description"]');
                    const desc = descElem ? descElem.textContent.trim() : '';

                    // 构造完整 URL
                    const fullUrl = href.startsWith('/') ? 'https://www.producthunt.com' + href : href;

                    products.push({
                        name: name,
                        url: fullUrl.split('?')[0],  // 移除查询参数
                        tagline: desc
                    });

                    if (products.length >= 10) break;
                }

                if (products.length > 0) break;
            }

            return products;
        }
        """

        extracted = commenter.page.evaluate(js_code)
        print(f"   JavaScript 提取到 {len(extracted)} 个产品")

        if extracted:
            for item in extracted:
                products.append({
                    'url': item['url'],
                    'name': item['name'][:50] if item['name'] else 'Product',  # 限制长度
                    'tagline': item['tagline'][:200] if item['tagline'] else 'Product from Product Hunt',
                    'category': 'Various',
                    'description': item['tagline'][:200] if item['tagline'] else 'Product from Product Hunt'
                })

        # 方法 2: 如果方法 1 失败，尝试点击元素提取
        if not products:
            print("   尝试方法 2: 遍历点击产品...")

            # 查找所有可能的产品元素
            product_elements = commenter.page.query_selector_all('a[href*="/posts/"]:not([href*="/posts/new"])')

            seen_urls = set()
            for elem in product_elements[:15]:
                try:
                    href = elem.get_attribute('href')
                    if not href or href in seen_urls:
                        continue

                    seen_urls.add(href)

                    # 构造完整 URL
                    full_url = f"https://www.producthunt.com{href}" if href.startswith('/') else href
                    full_url = full_url.split('?')[0]

                    # 提取产品名
                    text = elem.inner_text()
                    name = text.strip()[:50] if text else "Product"

                    products.append({
                        'url': full_url,
                        'name': name,
                        'tagline': f'{name} from Product Hunt',
                        'category': 'Various',
                        'description': f'Product from Product Hunt'
                    })

                    if len(products) >= 10:
                        break

                except Exception as e:
                    continue

        print(f"   ✅ 成功提取 {len(products)} 个产品")
        return products[:10]

    except Exception as e:
        print(f"   ❌ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=" * 80)
    print("🔍 Product Hunt 智能产品提取")
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

        # 滚动以加载更多
        commenter.page.evaluate("window.scrollTo(0, 1500)")
        time.sleep(3)
        commenter.page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)

        # 截图
        commenter.page.screenshot(path="ph_smart_extract.png")
        print("📸 截图保存: ph_smart_extract.png")

        # 保存 HTML 用于调试
        html = commenter.page.content()
        with open("ph_page_debug.html", 'w', encoding='utf-8') as f:
            f.write(html)
        print("📄 HTML 保存: ph_page_debug.html")

        # 查找所有包含 /posts/ 的链接
        all_links = commenter.page.query_selector_all('a')
        post_links = []
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/posts/' in href:
                post_links.append(href)

        print(f"\n🔗 找到 {len(post_links)} 个包含 /posts/ 的链接")
        unique_links = list(set(post_links))
        print(f"   去重后: {len(unique_links)} 个")
        for i, link in enumerate(unique_links[:10], 1):
            print(f"   {i}. {link}")

        # 提取产品
        products = extract_products_from_page(commenter)

        commenter.close_browser()

        if not products:
            print("\n❌ 未能提取产品")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "Smart DOM Extraction",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ 成功保存 {len(products)} 个产品")
        print("\n📋 产品列表:")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p['name']}")
            print(f"      {p['url']}")

        print("\n" + "=" * 80)
        print("✅ 智能提取完成！")
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
