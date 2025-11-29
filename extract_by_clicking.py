#!/usr/bin/env python3
"""
通过点击产品元素来提取真实 URL
最可靠的方法：直接与页面交互
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
from datetime import datetime

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def extract_products_by_clicking(commenter: ProductHuntCommenter) -> list:
    """通过点击产品卡片来提取 URL"""
    print("\n🔍 通过点击提取产品...")

    products = []

    try:
        # 等待页面加载
        print("   ⏳ 等待页面加载...")
        time.sleep(10)

        # 查找所有可点击的产品元素
        js_code = """
        () => {
            // 查找所有可能是产品的元素
            // Product Hunt 通常使用 article 或特定的 div
            const candidates = [
                ...document.querySelectorAll('article'),
                ...document.querySelectorAll('[data-test*="post"]'),
                ...document.querySelectorAll('div[class*="Post"]'),
                ...document.querySelectorAll('div[role="article"]')
            ];

            const products = [];
            const seen = new Set();

            for (const elem of candidates) {
                // 查找内部的链接
                const link = elem.querySelector('a[href*="/posts/"]');
                if (!link) continue;

                const href = link.getAttribute('href');
                if (!href || href.includes('/posts/new')) continue;

                // 尝试获取产品名称
                const nameElem = elem.querySelector('h2, h3, strong, [class*="name"], [class*="title"]');
                const name = nameElem ? nameElem.textContent.trim() : '';

                if (name && !seen.has(href)) {
                    seen.add(href);
                    products.push({
                        name: name,
                        href: href,
                        elem_id: products.length
                    });

                    // 给元素添加 ID 以便后续点击
                    elem.setAttribute('data-product-id', products.length.toString());
                }

                if (products.length >= 10) break;
            }

            return products;
        }
        """

        initial_products = commenter.page.evaluate(js_code)
        print(f"   ✅ 找到 {len(initial_products)} 个产品元素")

        if not initial_products:
            print("   ⚠️  未找到产品元素，尝试简单链接提取...")

            # 备用方案：直接查找链接并访问
            js_code_simple = """
            () => {
                const links = document.querySelectorAll('a[href*="/posts/"]');
                const products = [];

                for (const link of links) {
                    const href = link.getAttribute('href');
                    if (href && !href.includes('/posts/new') && !href.includes('/posts/all')) {
                        const text = link.textContent.trim();
                        if (text.length > 2 && text.length < 100) {
                            products.push({
                                name: text,
                                href: href
                            });

                            if (products.length >= 10) break;
                        }
                    }
                }

                return products;
            }
            """

            initial_products = commenter.page.evaluate(js_code_simple)
            print(f"   备用方案找到 {len(initial_products)} 个链接")

        # 对每个产品，访问其页面获取完整信息
        for i, prod_info in enumerate(initial_products[:10], 1):
            try:
                name = prod_info.get('name', '')
                href = prod_info.get('href', '')

                if not href:
                    continue

                print(f"\n   📦 产品 {i}/{len(initial_products)}: {name[:40]}...")

                # 构造完整 URL
                if href.startswith('/'):
                    full_url = f"https://www.producthunt.com{href}"
                else:
                    full_url = href

                # 访问产品页面
                commenter.page.goto(full_url, timeout=30000)
                time.sleep(3)

                # 从浏览器地址栏获取实际 URL（可能有重定向）
                actual_url = commenter.page.url.split('?')[0].split('#')[0]

                # 检查是否是 404
                page_text = commenter.page.text_content('body').lower()
                is_404 = 'lost this page' in page_text or '404' in page_text

                if is_404:
                    print(f"      ❌ 404 - 跳过")
                    continue

                # 尝试从页面提取更多信息
                page_info_js = """
                () => {
                    return {
                        title: document.title,
                        tagline: (document.querySelector('[class*="tagline"]') ||
                                 document.querySelector('meta[name="description"]'))?.textContent ||
                                 document.querySelector('meta[name="description"]')?.getAttribute('content') || ''
                    };
                }
                """

                page_info = commenter.page.evaluate(page_info_js)

                # 提取 slug
                slug_match = actual_url.split('/posts/')[1] if '/posts/' in actual_url else ''

                if slug_match:
                    products.append({
                        'url': actual_url,
                        'name': page_info.get('title', name).split('|')[0].split('-')[0].strip()[:50],
                        'tagline': page_info.get('tagline', f'{name} - Product from Product Hunt')[:200],
                        'category': 'Various',
                        'description': page_info.get('tagline', '')[:200],
                        'votes': 0
                    })

                    print(f"      ✅ URL: {actual_url}")

                # 返回首页继续
                commenter.page.goto("https://www.producthunt.com", timeout=30000)
                time.sleep(2)

            except Exception as e:
                print(f"      ❌ 错误: {e}")
                # 尝试返回首页
                try:
                    commenter.page.goto("https://www.producthunt.com", timeout=30000)
                    time.sleep(2)
                except:
                    pass
                continue

        print(f"\n   ✅ 成功提取 {len(products)} 个产品")
        return products

    except Exception as e:
        print(f"   ❌ 提取失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=" * 80)
    print("🔍 Product Hunt 点击提取（最可靠方法）")
    print("=" * 80)

    commenter = ProductHuntCommenter()

    try:
        print("\n🌐 访问 Product Hunt 首页...")
        commenter.setup_browser(headless=True)

        if not commenter.verify_login():
            print("❌ 登录失败")
            return 1

        commenter.page.goto("https://www.producthunt.com", timeout=60000)

        # 提取产品
        products = extract_products_by_clicking(commenter)

        commenter.close_browser()

        if not products:
            print("\n❌ 未能提取产品")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "Click and Extract Method",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n" + "=" * 80)
        print(f"✅ 成功保存 {len(products)} 个产品")
        print("=" * 80)
        print("\n📋 产品列表:")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p['name']}")
            print(f"      {p['tagline'][:70]}...")
            print(f"      {p['url']}")
            print()

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
