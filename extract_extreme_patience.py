#!/usr/bin/env python3
"""
极限耐心提取 - 最后的自动化尝试
策略：等待足够长的时间，反复尝试，直到产品出现
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

def try_extract_products(page) -> list:
    """尝试提取产品"""
    js_code = """
    () => {
        const allLinks = document.querySelectorAll('a[href]');
        const products = [];
        const seen = new Set();

        for (const link of allLinks) {
            const href = link.getAttribute('href');
            if (!href || !href.includes('/posts/')) continue;
            if (href.includes('/posts/new') || href.includes('/posts/all') || href.includes('/posts?')) continue;

            const url = href.startsWith('/') ? 'https://www.producthunt.com' + href : href;
            const cleanUrl = url.split('?')[0].split('#')[0];

            if (!seen.has(cleanUrl) && !cleanUrl.endsWith('/posts/') && !cleanUrl.endsWith('/posts')) {
                seen.add(cleanUrl);
                const text = link.textContent.trim();

                if (text.length > 2 && text.length < 100) {
                    products.push({
                        url: cleanUrl,
                        name: text
                    });

                    if (products.length >= 15) break;
                }
            }
        }

        return products;
    }
    """

    return page.evaluate(js_code)

def extract_with_extreme_patience(commenter: ProductHuntCommenter) -> list:
    """使用极限耐心提取产品"""
    print("\n🔍 极限耐心模式 - 将尝试 2 分钟...")
    print("   策略：反复滚动、等待、提取，直到找到产品\n")

    max_attempts = 12  # 12次尝试 x 10秒 = 2分钟
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        print(f"   🔄 尝试 {attempt}/{max_attempts}...")

        # 随机滚动
        scroll_positions = [0, 500, 1000, 1500, 1000, 500, 0]
        for pos in scroll_positions:
            commenter.page.evaluate(f"window.scrollTo(0, {pos})")
            time.sleep(random.uniform(0.5, 1.0))

        # 等待
        wait_time = 10 if attempt == 1 else 5
        print(f"      ⏳ 等待 {wait_time} 秒...")
        time.sleep(wait_time)

        # 尝试提取
        products = try_extract_products(commenter.page)

        if products:
            print(f"      ✅ 找到 {len(products)} 个产品！")

            # 转换格式
            formatted = []
            for p in products[:10]:
                formatted.append({
                    'url': p['url'],
                    'name': p['name'][:50],
                    'tagline': f"{p['name']} - Product from Product Hunt",
                    'category': 'Various',
                    'description': 'Auto-extracted product',
                    'votes': 0
                })

            return formatted

        print(f"      ⚠️  未找到产品，继续尝试...")

        # 每3次尝试截图一次
        if attempt % 3 == 0:
            screenshot_path = f"debug_attempt_{attempt}.png"
            commenter.page.screenshot(path=screenshot_path)
            print(f"      📸 截图: {screenshot_path}")

    print("\n   ❌ 2分钟后仍未找到产品")
    return []

def main():
    print("=" * 80)
    print("🔍 Product Hunt 极限耐心自动提取")
    print("=" * 80)
    print("\n⏰ 将尝试 2 分钟，请耐心等待...\n")

    commenter = ProductHuntCommenter()

    try:
        print("🌐 启动浏览器...")
        commenter.setup_browser(headless=True)

        if not commenter.verify_login():
            print("❌ 登录失败")
            return 1

        print("🌐 访问 Product Hunt...")
        commenter.page.goto("https://www.producthunt.com", timeout=60000, wait_until='networkidle')
        print("   ✅ 页面加载完成")

        # 极限耐心提取
        products = extract_with_extreme_patience(commenter)

        commenter.close_browser()

        if not products:
            print("\n" + "=" * 80)
            print("❌ 自动提取失败")
            print("=" * 80)
            print("\nProduct Hunt 的反爬虫保护太强，无法自动提取。")
            print("\n建议使用半自动方案（每天30秒）：")
            print("   查看 SIMPLE_DAILY_UPDATE.md")
            return 1

        # 保存
        data = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "source": "Extreme Patience Auto Extraction",
            "products": products,
            "updated_at": datetime.now().isoformat()
        }

        with open(PRODUCT_LIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 80)
        print(f"✅ 成功保存 {len(products)} 个产品！")
        print("=" * 80)
        print("\n📋 产品列表:")
        for i, p in enumerate(products, 1):
            print(f"   {i}. {p['name']}")
            print(f"      {p['url']}")

        print(f"\n📄 已保存到: {PRODUCT_LIST_FILE}")
        print("\n现在可以运行:")
        print("   python3 auto_producthunt_forever.py")

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
