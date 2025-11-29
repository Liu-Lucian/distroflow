#!/usr/bin/env python3
"""
Instagram完整流程测试：搜索 → 点帖子 → 在弹窗中找Message按钮
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Complete Flow Test")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

test_keyword = "startup founder"  # 搜索关键词

with sync_playwright() as p:
    print(f"\n🚀 启动浏览器...")
    browser = p.chromium.launch(headless=False, slow_mo=1000)
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

    # 步骤1: 访问主页
    print("\n📱 Step 1: 访问Instagram主页...")
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

    # 步骤2: 点击搜索
    print(f"\n🔍 Step 2: 搜索 '{test_keyword}'...")
    search_icon = page.wait_for_selector('svg[aria-label="搜索"]', timeout=5000)
    search_icon.click()
    time.sleep(1)

    # 输入搜索
    search_input = page.wait_for_selector('input[type="text"]', timeout=3000)
    for char in test_keyword:
        search_input.type(char)
        time.sleep(0.1)
    time.sleep(2)

    # 步骤3: 点击搜索结果中的第一个用户
    print("\n👤 Step 3: 点击搜索结果...")

    # 尝试找到用户链接
    user_links = page.query_selector_all('a[href*="/"]')
    print(f"   找到 {len(user_links)} 个链接")

    # 找到看起来像用户profile的链接
    profile_link = None
    for link in user_links[:10]:  # 只检查前10个
        href = link.get_attribute('href')
        if href and href.startswith('/') and href.count('/') == 2 and not any(x in href for x in ['explore', 'reel', 'p/', 'direct']):
            print(f"   找到用户链接: {href}")
            profile_link = link
            break

    if profile_link:
        # 使用JavaScript点击避免overlay问题
        href = profile_link.get_attribute('href')
        print(f"   导航到用户: {href}")
        page.goto(f'https://www.instagram.com{href}', timeout=30000)
        time.sleep(3)
        print(f"   ✅ 访问了用户profile")
    else:
        print("   ❌ 没找到用户链接")
        browser.close()
        exit(1)

    # 步骤4: 在profile页面，点击第一个帖子
    print("\n📸 Step 4: 点击第一个帖子...")

    posts = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    print(f"   找到 {len(posts)} 个帖子")

    if posts:
        first_post = posts[0]
        href = first_post.get_attribute('href')
        print(f"   点击帖子: {href}")
        # 使用JavaScript点击避免overlay问题
        page.evaluate('(element) => element.click()', first_post)
        time.sleep(3)

        # 步骤5: 在帖子弹窗中查找元素
        print("\n🔎 Step 5: 分析帖子弹窗...")

        # 查找用户名链接（在帖子header中）
        print("   查找用户名链接...")
        username_links = page.query_selector_all('header a')
        print(f"   找到 {len(username_links)} 个header链接")

        # 查找Message按钮（可能在弹窗中）
        print("\n   查找Message/消息按钮...")
        message_selectors = [
            'button:has-text("消息")',
            'button:has-text("Message")',
            'div[role="button"]:has-text("消息")',
            'div[role="button"]:has-text("Message")',
        ]

        found_message_btn = False
        for selector in message_selectors:
            buttons = page.query_selector_all(selector)
            if buttons:
                print(f"   ✅ 找到: {selector} ({len(buttons)}个)")
                found_message_btn = True

                # 尝试点击第一个
                try:
                    buttons[0].click()
                    print("   ✅ 点击了Message按钮")
                    time.sleep(3)
                    break
                except Exception as e:
                    print(f"   ❌ 点击失败: {e}")
            else:
                print(f"   ❌ 未找到: {selector}")

        if not found_message_btn:
            print("\n   ⚠️  没找到Message按钮，尝试点击用户头像...")
            # 如果没有Message按钮，尝试点击帖子中的用户名
            if username_links:
                username_links[0].click()
                time.sleep(3)
                print("   ✅ 点击了用户名")

                # 再次查找Message按钮
                print("\n   在profile页面查找Message按钮...")
                for selector in message_selectors:
                    buttons = page.query_selector_all(selector)
                    if buttons:
                        print(f"   ✅ 找到: {selector}")
                        buttons[0].click()
                        time.sleep(3)
                        break

        # 步骤6: 查找消息输入框
        print("\n💬 Step 6: 查找消息输入框...")

        input_selectors = [
            'textarea[placeholder*="消息"]',
            'textarea[placeholder*="Message"]',
            'div[contenteditable="true"]',
            'textarea[aria-label*="Message"]',
            'div[role="textbox"]',
        ]

        for selector in input_selectors:
            inputs = page.query_selector_all(selector)
            count = len(inputs)
            print(f"   {selector}: {count}个")

            if count > 0:
                try:
                    inp = inputs[0]
                    placeholder = inp.get_attribute('placeholder')
                    aria_label = inp.get_attribute('aria-label')
                    print(f"      Placeholder: {placeholder}")
                    print(f"      Aria-label: {aria_label}")

                    # 尝试输入测试消息
                    print("      🧪 测试输入...")
                    inp.click()
                    time.sleep(0.5)
                    inp.fill("Test message")
                    print("      ✅ 输入成功！")

                    # 清除
                    inp.fill("")
                    break
                except Exception as e:
                    print(f"      ❌ 输入失败: {e}")

    else:
        print("   ❌ 没找到帖子")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开90秒供检查...")
    print("=" * 60)

    time.sleep(90)

    browser.close()
    print("\n✅ 完成")
