#!/usr/bin/env python3
"""
调试Instagram用户profile页面，查找帖子元素
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Profile Posts Debugger")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

test_username = 'garyvee'  # 或者其他用户

with sync_playwright() as p:
    print(f"\n🚀 启动浏览器，访问 @{test_username}...")
    browser = p.chromium.launch(headless=False, slow_mo=800)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 900}
    )

    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/'
    }])

    page = context.new_page()

    # 访问主页
    print("\n📱 访问Instagram主页...")
    page.goto('https://www.instagram.com/', timeout=60000)
    time.sleep(2)

    # 关闭通知弹窗
    try:
        dismiss_button = page.wait_for_selector('button:has-text("以后再说")', timeout=3000)
        if dismiss_button:
            print("   🔕 关闭通知弹窗...")
            dismiss_button.click()
            time.sleep(1)
    except:
        pass

    # 访问用户profile
    print(f"\n👤 访问 @{test_username} 的profile...")
    page.goto(f'https://www.instagram.com/{test_username}/', timeout=60000)
    time.sleep(3)

    print(f"当前URL: {page.url}")

    # 详细扫描帖子元素
    print("\n🔎 扫描帖子元素...")

    post_selectors = [
        'article a[href*="/p/"]',
        'article a[href*="/reel/"]',
        'a[href*="/p/"]',
        'a[href*="/reel/"]',
        'article a',
        'div._aagw a',
        'div[role="button"] a',
    ]

    found_any = False

    for selector in post_selectors:
        elements = page.query_selector_all(selector)
        count = len(elements)

        if count > 0:
            print(f"\n   ✅ {selector}: {count} 个")
            found_any = True

            # 显示前3个
            for i, elem in enumerate(elements[:3]):
                try:
                    href = elem.get_attribute('href')
                    print(f"      [{i+1}] href: {href}")
                except Exception as e:
                    print(f"      [{i+1}] 无法获取: {e}")
        else:
            print(f"   ❌ {selector}: 0 个")

    if not found_any:
        print("\n   ⚠️  没有找到任何帖子链接！")
        print("   尝试检查页面HTML结构...")

        # 保存页面HTML
        html = page.content()
        print(f"   页面HTML长度: {len(html)} 字符")

        # 查找所有<a>标签
        all_links = page.query_selector_all('a')
        print(f"   总共找到 {len(all_links)} 个链接")

        # 显示前10个链接
        print("   前10个链接的href:")
        for i, link in enumerate(all_links[:10]):
            try:
                href = link.get_attribute('href') or ''
                if href:
                    print(f"      {i+1}. {href}")
            except:
                pass

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开60秒，你可以手动查看")
    print("=" * 60)

    time.sleep(60)

    browser.close()
    print("\n✅ 完成")
