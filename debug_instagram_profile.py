#!/usr/bin/env python3
"""
调试Instagram profile页面 - 查看帖子加载情况
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Profile Post Debugger")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

# 使用一个已知有帖子的用户
test_username = "natgeo"  # National Geographic - 肯定有很多帖子

with sync_playwright() as p:
    print(f"\n🚀 启动浏览器...")
    browser = p.chromium.launch(headless=False, slow_mo=500)
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

    # 访问用户profile
    print(f"\n📱 访问 @{test_username} 的profile...")
    page.goto(f'https://www.instagram.com/{test_username}/', timeout=60000)

    # 关闭通知弹窗
    try:
        dismiss_button = page.wait_for_selector('button:has-text("以后再说")', timeout=3000)
        if dismiss_button:
            print("   🔕 关闭通知弹窗...")
            dismiss_button.click()
            time.sleep(1)
    except:
        pass

    print(f"   当前URL: {page.url}")

    # 等待页面完全加载
    print("\n⏳ 等待页面加载...")
    time.sleep(5)

    # 尝试多种帖子选择器
    print("\n🔎 测试各种帖子选择器...")

    selectors_to_test = [
        'a[href*="/p/"]',
        'a[href*="/reel/"]',
        'article a',
        'article a[href*="/p/"]',
        'article a[href*="/reel/"]',
        'div[role="button"] a[href*="/p/"]',
        'main article a',
        'main a[href*="/p/"]',
        'img[src*="instagram"]',  # 图片元素
        'div._aagw',  # Instagram帖子容器类名
    ]

    for selector in selectors_to_test:
        elements = page.query_selector_all(selector)
        print(f"   {selector}: {len(elements)} 个")

        if len(elements) > 0 and len(elements) <= 5:
            # 如果找到少量元素，打印详细信息
            for i, elem in enumerate(elements[:3]):
                try:
                    if 'href' in selector:
                        href = elem.get_attribute('href')
                        print(f"      [{i+1}] href: {href}")
                    elif 'img' in selector:
                        src = elem.get_attribute('src')
                        print(f"      [{i+1}] src: {src[:80]}...")
                except Exception as e:
                    print(f"      [{i+1}] 无法获取属性: {e}")

    # 滚动页面加载更多内容
    print("\n📜 滚动页面...")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(3)

    # 再次检查帖子
    print("\n🔎 滚动后再次检查...")
    posts = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    print(f"   找到 {len(posts)} 个帖子链接")

    if len(posts) > 0:
        print(f"\n✅ 找到帖子！选择器有效")
        print(f"   第一个帖子: {posts[0].get_attribute('href')}")

        # 测试点击第一个帖子
        print("\n🧪 测试点击第一个帖子...")
        try:
            page.evaluate('(element) => element.click()', posts[0])
            print("   ✅ 点击成功")
            time.sleep(3)

            # 查看弹窗中的元素
            print("\n🔎 查看帖子弹窗...")
            print(f"   当前URL: {page.url}")

            # 查找Message按钮
            message_selectors = [
                'button:has-text("消息")',
                'button:has-text("Message")',
                'div[role="button"]:has-text("消息")',
                'div[role="button"]:has-text("Message")',
                'a:has-text("消息")',
                'a:has-text("Message")',
            ]

            for selector in message_selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"   ✅ 找到Message按钮: {selector} ({len(elements)}个)")
                else:
                    print(f"   ❌ 未找到: {selector}")

            # 查找用户名链接
            print("\n   查找用户名链接...")
            username_links = page.query_selector_all('header a')
            print(f"   header a: {len(username_links)} 个")

            for i, link in enumerate(username_links[:3]):
                href = link.get_attribute('href')
                text = link.inner_text()
                print(f"      [{i+1}] {text} -> {href}")

        except Exception as e:
            print(f"   ❌ 点击失败: {e}")
    else:
        print(f"\n❌ 没有找到帖子")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开60秒供检查...")
    print("=" * 60)

    time.sleep(60)

    browser.close()
    print("\n✅ 完成")
