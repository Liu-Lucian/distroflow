#!/usr/bin/env python3
"""
检查 Product Hunt 首页产品链接结构
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import time

commenter = ProductHuntCommenter()
commenter.setup_browser(headless=False)

if not commenter.verify_login():
    print("❌ 未登录")
    commenter.close_browser()
    sys.exit(1)

print("🌐 访问 Product Hunt 首页...")
commenter.page.goto("https://www.producthunt.com", timeout=60000)
time.sleep(5)

print("\n🔍 查找产品链接...")

# 尝试不同的选择器
selectors = [
    'a[href*="/posts/"]',
    'article a[href*="/posts/"]',
    'div[data-test="post-item"] a',
    'main a[href*="/posts/"]',
    '[data-test*="post"] a[href*="/posts/"]',
]

for selector in selectors:
    links = commenter.page.query_selector_all(selector)
    print(f"\n选择器: {selector}")
    print(f"  找到 {len(links)} 个链接")

    if links:
        print("  前5个链接:")
        for i, link in enumerate(links[:5], 1):
            href = link.get_attribute('href')
            text = link.inner_text()[:50] if link.inner_text() else "(无文本)"
            print(f"    {i}. {href} - {text}")

print("\n\n按 Enter 关闭浏览器...")
input()

commenter.close_browser()
