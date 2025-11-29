#!/usr/bin/env python3
"""
Instagram DM自动调试 - 持续监控页面变化
"""

import sys
sys.path.append('src')

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram DM Auto Debug")
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
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 800}
    )

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
    print("📋 PROFILE PAGE ANALYSIS")
    print("=" * 60)

    # 分析profile页面上的按钮
    print("\n🔎 Looking for action buttons on profile...")

    button_selectors = [
        'button:has-text("Message")',
        'button:has-text("message")',
        'div[role="button"]:has-text("Message")',
        'div[role="button"]:has-text("message")',
        'a:has-text("Message")',
        'button',  # 所有button
        'div[role="button"]',  # 所有role=button的div
    ]

    found_buttons = []

    for selector in button_selectors:
        elements = page.query_selector_all(selector)
        count = len(elements)

        if 'Message' in selector or 'message' in selector:
            print(f"   {selector}: {count} found")

        if count > 0 and 'Message' in selector:
            for i, elem in enumerate(elements[:3]):  # 只看前3个
                try:
                    text = elem.inner_text()
                    aria_label = elem.get_attribute('aria-label') or ''
                    tag_name = elem.evaluate('el => el.tagName')
                    print(f"      → Match {i+1}: {tag_name}, Text: '{text}', Aria: '{aria_label}'")
                    found_buttons.append((selector, elem))
                except Exception as e:
                    print(f"      → Could not get details: {e}")

    # 检查所有button，看有没有包含"Message"的
    print("\n🔎 Scanning all buttons for 'Message' text...")
    all_buttons = page.query_selector_all('button')
    print(f"   Total buttons found: {len(all_buttons)}")

    message_buttons = []
    for i, btn in enumerate(all_buttons):
        try:
            text = btn.inner_text().strip()
            if text and ('message' in text.lower() or 'send' in text.lower()):
                aria = btn.get_attribute('aria-label') or ''
                print(f"   Button {i}: '{text}' (aria: '{aria}')")
                message_buttons.append(btn)
        except:
            pass

    # 步骤3: 尝试点击Message按钮（如果找到）
    if message_buttons:
        print("\n" + "=" * 60)
        print("✅ FOUND MESSAGE BUTTON - ATTEMPTING CLICK")
        print("=" * 60)

        try:
            first_msg_btn = message_buttons[0]
            print(f"   Clicking button: {first_msg_btn.inner_text()}")
            first_msg_btn.click()
            time.sleep(3)

            print(f"\n📍 After click URL: {page.url}")

            # 分析DM页面
            print("\n🔎 Looking for message input after click...")

            input_selectors = [
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="message"]',
                'div[contenteditable="true"]',
                'textarea[aria-label*="Message"]',
                'div[role="textbox"]',
                'textarea',
                'div[contenteditable="true"][role="textbox"]',
            ]

            for selector in input_selectors:
                elements = page.query_selector_all(selector)
                count = len(elements)
                print(f"   {selector}: {count} found")

                if count > 0:
                    first_elem = elements[0]
                    try:
                        placeholder = first_elem.get_attribute('placeholder') or ''
                        aria_label = first_elem.get_attribute('aria-label') or ''
                        role = first_elem.get_attribute('role') or ''
                        tag_name = first_elem.evaluate('el => el.tagName')

                        print(f"      → Match details:")
                        print(f"         Tag: {tag_name}")
                        if placeholder:
                            print(f"         Placeholder: {placeholder}")
                        if aria_label:
                            print(f"         Aria-label: {aria_label}")
                        if role:
                            print(f"         Role: {role}")

                        # 尝试输入测试消息
                        print("\n      🧪 Testing input...")
                        first_elem.click()
                        time.sleep(0.5)
                        first_elem.fill("Test message")
                        print("      ✅ Successfully typed test message!")

                        # 查找发送按钮
                        print("\n      🔎 Looking for Send button...")
                        send_btns = page.query_selector_all('button')
                        for btn in send_btns:
                            try:
                                btn_text = btn.inner_text().strip()
                                if btn_text and 'send' in btn_text.lower():
                                    print(f"         Found: '{btn_text}'")
                            except:
                                pass

                        # 清除测试消息
                        first_elem.fill('')
                        print("      🧹 Cleared test message")

                        break  # 找到可用input就停止

                    except Exception as e:
                        print(f"      → Error: {e}")

        except Exception as e:
            print(f"❌ Error clicking button: {e}")

    else:
        print("\n⚠️  No Message button found on profile")
        print("   Possible reasons:")
        print("   - User has restricted DMs")
        print("   - Need to follow first")
        print("   - Instagram UI changed")

        # 尝试直接访问DM页面
        print("\n📱 Trying direct /direct/ navigation...")
        page.goto('https://www.instagram.com/direct/inbox/', timeout=60000)
        time.sleep(3)

        print(f"   Current URL: {page.url}")

        # 查找"New message"按钮
        print("\n🔎 Looking for New Message button...")
        new_msg_selectors = [
            'svg[aria-label*="New message"]',
            'button:has-text("New message")',
            'div[role="button"]:has-text("New")',
        ]

        for selector in new_msg_selectors:
            elements = page.query_selector_all(selector)
            print(f"   {selector}: {len(elements)} found")

    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 60)
    print("\n⏸️  Browser will stay open for 60 seconds...")
    print("   You can manually interact with the page if needed")

    time.sleep(60)

    browser.close()
    print("\n✅ Browser closed")
