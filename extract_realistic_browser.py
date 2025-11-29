#!/usr/bin/env python3
"""
使用更真实的浏览器行为来提取产品
关键：不使用 headless模式，模拟人类行为
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import os
import json
import time
from datetime import datetime
import random

PRODUCT_LIST_FILE = "todays_producthunt_products.json"

def human_like_scroll(page):
    """模拟人类滚动行为"""
    # 随机滚动
    for i in range(5):
        scroll_amount = random.randint(200, 500)
        page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(random.uniform(0.5, 1.5))

    # 滚回顶部
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(2)

def extract_products_realistic(commenter: ProductHuntCommenter) -> list:
    """使用真实浏览器行为提取产品"""
    print("\n🔍 使用真实浏览器提取产品...")

    try:
        print("   ⏳ 等待页面完全加载（30秒）...")
        time.sleep(30)  # 长时间等待，让所有内容加载

        # 模拟人类浏览行为
        print("   📜 模拟人类滚动...")
        human_like_scroll(commenter.page)

        # 再等一会儿
        time.sleep(5)

        # 尝试提取链接
        js_code = """
        () => {
            const allLinks = Array.from(document.querySelectorAll('a[href]'));
            const postLinks = allLinks
                .map(a => ({
                    href: a.getAttribute('href'),
                    text: a.textContent.trim()
                }))
                .filter(item => {
                    const href = item.href;
                    return href &&
                           href.includes('/posts/') &&
                           !href.includes('/posts/new') &&
                           !href.includes('/posts/all') &&
                           !href.includes('/posts?') &&
                           item.text.length > 2 &&
                           item.text.length < 100;
                });

            // 去重
            const seen = new Set();
            const unique = [];
            for (const item of postLinks) {
                const url = item.href.startsWith('/') ?
                    'https://www.producthunt.com' + item.href :
                    item.href;
                const cleanUrl = url.split('?')[0].split('#')[0];

                if (!seen.has(cleanUrl)) {
                    seen.add(cleanUrl);
                    unique.push({
                        url: cleanUrl,
                        name: item.text
                    });
                }

                if (unique.length >= 15) break;
            }

            return {
                totalLinks: allLinks.length,
                postLinks: postLinks.length,
                unique: unique
            };
        }
        """

        result = commenter.page.evaluate(js_code)
        print(f"\n   📊 统计:")
        print(f"      总链接数: {result['totalLinks']}")
        print(f"      /posts/ 链接数: {result['postLinks']}")
        print(f"      去重后: {len(result['unique'])}")

        if not result['unique']:
            print("   ❌ 未找到产品链接")

            # 截图保存状态
            commenter.page.screenshot(path="debug_no_products.png")
            print("   📸 已保存调试截图: debug_no_products.png")

            # 保存HTML
            with open("debug_no_products.html", 'w', encoding='utf-8') as f:
                f.write(commenter.page.content())
            print("   📄 已保存HTML: debug_no_products.html")

            return []

        # 转换为标准格式
        products = []
        for item in result['unique'][:10]:
            url = item['url']
            name = item['name'][:50]

            products.append({
                'url': url,
                'name': name,
                'tagline': f'{name} - Product from Product Hunt Today',
                'category': 'Various',
                'description': 'Auto-extracted product',
                'votes': 0
            })

        print(f"   ✅ 提取到 {len(products)} 个产品\n")

        # 显示产品列表
        for i, p in enumerate(products, 1):
            print(f"      {i}. {p['name']}")
            print(f"         {p['url']}")

        return products

    except Exception as e:
        print(f"   ❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("=" * 80)
    print("🔍 Product Hunt 真实浏览器提取（最后尝试）")
    print("=" * 80)
    print("\n⚠️  将打开可见浏览器窗口，请勿关闭！")
    print("   需要等待约 40 秒完成提取...\n")

    commenter = ProductHuntCommenter()

    try:
        print("🌐 启动浏览器...")
        commenter.setup_browser(headless=False)  # 使用可见浏览器！

        if not commenter.verify_login():
            print("❌ 登录失败")
            return 1

        print("🌐 访问 Product Hunt...")
        commenter.page.goto("https://www.producthunt.com", timeout=60000)

        # 提取产品
        products = extract_products_realistic(commenter)

        print("\n⏸️  按回车键关闭浏览器并保存结果...")
        input()

        commenter.close_browser()

        if not products:
            print("\n❌ 未能提取产品")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "Realistic Browser Extraction",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n" + "=" * 80)
        print(f"✅ 成功保存 {len(products)} 个产品到 {PRODUCT_LIST_FILE}")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n❌ 错误: {e}")
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
