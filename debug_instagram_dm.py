#!/usr/bin/env python3
"""
Instagram DM发送调试脚本
用于找出输入框选择器的问题
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright

# 加载认证
with open('platforms_auth.json', 'r') as f:
    config = json.load(f)
sessionid = config.get('instagram', {}).get('sessionid', '')

print("=" * 70)
print("🔍 Instagram DM Debug Script")
print("=" * 70)

# 测试用户名（从qualified_users.json读取）
try:
    with open('instagram_qualified_users.json', 'r') as f:
        users = json.load(f)
    test_user = users[0]['username'].lstrip('@') if users else input("Enter test username: ")
except:
    test_user = input("Enter test username: ")

print(f"📱 Test user: @{test_user}")
print()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 720}
    )

    if sessionid:
        context.add_cookies([{
            'name': 'sessionid',
            'value': sessionid,
            'domain': '.instagram.com',
            'path': '/'
        }])

    page = context.new_page()

    # 步骤1: 访问用户profile
    print(f"📱 Step 1: Going to profile...")
    page.goto(f'https://www.instagram.com/{test_user}/', timeout=30000)
    time.sleep(3)

    # 关闭弹窗
    try:
        not_now = page.query_selector('button:has-text("Not Now")')
        if not_now:
            not_now.click()
            time.sleep(1)
    except:
        pass

    # 步骤2: Follow
    print("👥 Step 2: Following user...")
    follow_selectors = [
        'button:has-text("Follow")',
        'div[role="button"]:has-text("Follow")',
    ]

    for selector in follow_selectors:
        try:
            follow_btn = page.wait_for_selector(selector, timeout=3000)
            if follow_btn and follow_btn.is_visible():
                print(f"   ✅ Found follow button: {selector}")
                page.evaluate('(el) => el.click()', follow_btn)
                time.sleep(2)
                break
        except:
            continue

    # 步骤3: 点击Message按钮
    print("💬 Step 3: Clicking Message button...")
    message_selectors = [
        'div:has-text("Message")',
        'button:has-text("Message")',
        'div[role="button"]:has-text("Message")',
    ]

    message_opened = False
    for selector in message_selectors:
        try:
            msg_btn = page.wait_for_selector(selector, timeout=3000)
            if msg_btn and msg_btn.is_visible():
                print(f"   ✅ Found message button: {selector}")
                page.evaluate('(el) => el.click()', msg_btn)
                time.sleep(3)  # 增加等待时间
                message_opened = True
                break
        except Exception as e:
            print(f"   ❌ {selector} failed: {e}")
            continue

    if not message_opened:
        print("❌ Could not open message dialog")
        input("Press Enter to close browser...")
        browser.close()
        sys.exit(1)

    # 步骤4: 查找输入框（详细调试）
    print("✏️  Step 4: Finding input box...")
    print("   Waiting for page to load...")
    time.sleep(3)  # 额外等待

    # 打印页面上所有可能的输入元素
    print("\n🔍 Debug: Looking for all possible input elements...")

    try:
        # 查找所有contenteditable元素
        all_contenteditable = page.query_selector_all('[contenteditable="true"]')
        print(f"   Found {len(all_contenteditable)} contenteditable elements")
        for i, elem in enumerate(all_contenteditable):
            visible = elem.is_visible()
            role = elem.get_attribute('role')
            aria_label = elem.get_attribute('aria-label')
            print(f"   [{i}] visible={visible}, role={role}, aria-label={aria_label}")
    except Exception as e:
        print(f"   Error checking contenteditable: {e}")

    try:
        # 查找所有textarea
        all_textarea = page.query_selector_all('textarea')
        print(f"   Found {len(all_textarea)} textarea elements")
        for i, elem in enumerate(all_textarea):
            visible = elem.is_visible()
            placeholder = elem.get_attribute('placeholder')
            print(f"   [{i}] visible={visible}, placeholder={placeholder}")
    except Exception as e:
        print(f"   Error checking textarea: {e}")

    # 尝试所有可能的选择器
    input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][aria-label*="Message"]',
        'div[contenteditable="true"]',
        'textarea[placeholder*="Message"]',
        'div[role="textbox"]',
        'p[contenteditable="true"]',
    ]

    print("\n🔍 Trying input selectors...")
    message_input = None
    for selector in input_selectors:
        try:
            print(f"   Trying: {selector}")
            elem = page.wait_for_selector(selector, timeout=2000)
            if elem and elem.is_visible():
                print(f"   ✅ FOUND: {selector}")
                message_input = elem
                break
            else:
                print(f"   ❌ Found but not visible")
        except Exception as e:
            print(f"   ❌ Not found: {e}")
            continue

    if not message_input:
        print("\n❌ Could not find input box!")
        print("\n📸 Taking screenshot for debugging...")
        page.screenshot(path='instagram_dm_debug.png')
        print("   Saved to: instagram_dm_debug.png")
        input("\nPress Enter to close browser...")
        browser.close()
        sys.exit(1)

    # 步骤5: 输入消息
    print("\n✏️  Step 5: Typing message...")
    test_message = "Hi! Testing DM system."

    try:
        message_input.click()
        time.sleep(1)
        message_input.fill(test_message)
        time.sleep(2)
        print("   ✅ Message typed")
    except Exception as e:
        print(f"   ❌ Failed to type: {e}")
        input("Press Enter to close browser...")
        browser.close()
        sys.exit(1)

    # 步骤6: 发送
    print("📤 Step 6: Sending...")

    send_selectors = [
        'div[role="button"]:has-text("Send")',
        'button:has-text("Send")',
    ]

    sent = False
    for selector in send_selectors:
        try:
            send_btn = page.wait_for_selector(selector, timeout=3000)
            if send_btn and send_btn.is_visible():
                print(f"   ✅ Found send button: {selector}")
                page.evaluate('(el) => el.click()', send_btn)
                time.sleep(2)
                sent = True
                break
        except:
            continue

    if not sent:
        print("   ℹ️  Trying Enter key...")
        message_input.press('Enter')
        time.sleep(2)
        sent = True

    if sent:
        print("\n✅ SUCCESS! Message sent!")
    else:
        print("\n❌ Failed to send")

    print("\n📸 Taking final screenshot...")
    page.screenshot(path='instagram_dm_final.png')
    print("   Saved to: instagram_dm_final.png")

    input("\nPress Enter to close browser...")
    browser.close()
