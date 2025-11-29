#!/usr/bin/env python3
"""
Instagram DM交互式调试 - 用户手动操作，程序观察学习
"""

import sys
sys.path.append('src')

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram DM Interactive Debug")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

instagram_config = platforms.get('instagram', {})
sessionid = instagram_config.get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found in platforms_auth.json")
    sys.exit(1)

print("✅ Found Instagram sessionid")

# 测试用户
test_user = {
    'username': 'natgeo',
    'name': 'National Geographic'
}

with sync_playwright() as p:
    print("\n🚀 Launching browser (visible mode)...")
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context()

    # 添加sessionid cookie
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.instagram.com',
        'path': '/'
    }])

    page = context.new_page()

    # 步骤1: 访问主页验证登录
    print("\n📱 Step 1: Visiting Instagram homepage...")
    page.goto('https://www.instagram.com/', timeout=60000)
    time.sleep(3)

    current_url = page.url
    print(f"   Current URL: {current_url}")

    if 'login' in current_url:
        print("❌ Not logged in - sessionid may be expired")
        browser.close()
        sys.exit(1)

    print("✅ Logged in successfully")

    # 步骤2: 访问用户主页
    print(f"\n📱 Step 2: Opening @{test_user['username']} profile...")
    page.goto(f'https://www.instagram.com/{test_user["username"]}/', timeout=60000)
    time.sleep(3)

    print("\n" + "=" * 60)
    print("🛑 PAUSE FOR MANUAL OPERATION")
    print("=" * 60)
    print("\n📋 Instructions:")
    print(f"   1. The browser should show @{test_user['username']}'s profile")
    print("   2. Please MANUALLY click the 'Message' button")
    print("   3. Wait for the DM input box to appear")
    print("   4. DO NOT type anything yet")
    print("   5. Come back here and press ENTER")
    print("\n⏸️  Waiting for you to click Message and then press ENTER...")

    input()

    # 步骤3: 观察页面结构
    print("\n🔍 Step 3: Analyzing page structure after manual click...")
    time.sleep(1)

    current_url = page.url
    print(f"\n📍 Current URL: {current_url}")

    # 检查各种可能的消息输入框选择器
    print("\n🔎 Looking for message input box...")

    selectors_to_try = [
        'textarea[placeholder*="Message"]',
        'textarea[placeholder*="message"]',
        'div[contenteditable="true"]',
        'textarea[aria-label*="Message"]',
        'div[role="textbox"]',
        'textarea',
        'div.x1i10hfl',
        'div[contenteditable="true"][role="textbox"]',
    ]

    found_selectors = []

    for selector in selectors_to_try:
        elements = page.query_selector_all(selector)
        count = len(elements)
        print(f"   {selector}: {count} found")

        if count > 0:
            found_selectors.append(selector)
            # 获取第一个元素的详细信息
            first_elem = elements[0]
            try:
                placeholder = first_elem.get_attribute('placeholder') or ''
                aria_label = first_elem.get_attribute('aria-label') or ''
                role = first_elem.get_attribute('role') or ''
                tag_name = first_elem.evaluate('el => el.tagName')

                print(f"      → First match details:")
                print(f"         Tag: {tag_name}")
                if placeholder:
                    print(f"         Placeholder: {placeholder}")
                if aria_label:
                    print(f"         Aria-label: {aria_label}")
                if role:
                    print(f"         Role: {role}")
            except Exception as e:
                print(f"      → Could not get details: {e}")

    # 检查发送按钮
    print("\n🔎 Looking for Send button...")

    send_selectors = [
        'button:has-text("Send")',
        'div[role="button"]:has-text("Send")',
        'button[type="submit"]',
        'div[role="button"]:has-text("发送")',
    ]

    for selector in send_selectors:
        elements = page.query_selector_all(selector)
        count = len(elements)
        print(f"   {selector}: {count} found")

        if count > 0:
            first_elem = elements[0]
            try:
                text = first_elem.inner_text()
                aria_label = first_elem.get_attribute('aria-label') or ''
                print(f"      → Text: '{text}', Aria-label: '{aria_label}'")
            except Exception as e:
                print(f"      → Could not get details: {e}")

    # 步骤4: 测试输入
    if found_selectors:
        print("\n" + "=" * 60)
        print("🧪 TESTING MESSAGE INPUT")
        print("=" * 60)

        test_message = "Test message - please ignore"
        best_selector = found_selectors[0]

        print(f"\n📝 Attempting to type using: {best_selector}")

        try:
            message_input = page.query_selector(best_selector)

            if message_input:
                # 清除已有内容
                message_input.click()
                time.sleep(0.5)

                # 尝试输入
                message_input.fill(test_message)
                print(f"✅ Successfully typed: '{test_message}'")

                time.sleep(2)

                # 检查发送按钮是否可用
                send_button = page.query_selector('button:has-text("Send")')
                if send_button:
                    is_disabled = send_button.is_disabled()
                    print(f"\n🔘 Send button status: {'Disabled' if is_disabled else 'Enabled'}")

                # 清除测试消息
                message_input.fill('')
                print("🧹 Cleared test message")

        except Exception as e:
            print(f"❌ Error during input test: {e}")

    print("\n" + "=" * 60)
    print("✅ DEBUG COMPLETE")
    print("=" * 60)

    if found_selectors:
        print("\n📋 RECOMMENDED SELECTOR:")
        print(f"   {found_selectors[0]}")
    else:
        print("\n⚠️  No input elements found")
        print("   This suggests Instagram's UI may have changed")
        print("   or we need to navigate differently")

    print("\n⏸️  Browser will stay open for 30 seconds for inspection...")
    time.sleep(30)

    browser.close()
    print("\n✅ Browser closed")
