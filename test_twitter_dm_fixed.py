#!/usr/bin/env python3
"""
测试Twitter DM发送功能
"""

import json
import sys
from playwright.sync_api import sync_playwright
import time

def test_twitter_dm():
    """测试Twitter DM"""

    # 加载认证
    with open('auth.json', 'r') as f:
        storage_state = json.load(f)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(storage_state=storage_state)
        page = context.new_page()

        # 测试用户（使用一个公开账号）
        test_username = "elonmusk"  # 改成你想测试的用户名

        print(f"\n🧪 Testing Twitter DM to @{test_username}...")
        print("=" * 60)

        try:
            # 访问用户profile
            profile_url = f"https://twitter.com/{test_username}"
            print(f"1️⃣ Loading profile: {profile_url}")
            page.goto(profile_url, wait_until='domcontentloaded', timeout=15000)
            time.sleep(3)

            # 检查是否登录
            if 'login' in page.url:
                print("❌ Not logged in")
                return False

            print("✅ Logged in")

            # 查找"Message"按钮
            print("\n2️⃣ Looking for Message button...")
            message_btn_selectors = [
                'div[data-testid="sendDMFromProfile"]',
                'a[data-testid="sendDMFromProfile"]',
                'button[data-testid="sendDMFromProfile"]',
            ]

            message_button = None
            for selector in message_btn_selectors:
                try:
                    message_button = page.wait_for_selector(selector, timeout=3000)
                    if message_button:
                        print(f"✅ Found message button: {selector}")
                        break
                except:
                    continue

            if not message_button:
                print("⚠️  DMs may not be enabled for this user")
                print("\n💡 Tip: Try a different user who allows DMs")
                return False

            # 点击Message按钮
            print("\n3️⃣ Clicking Message button...")
            message_button.click()
            time.sleep(3)
            print("✅ Clicked")

            # 等待DM输入框
            print("\n4️⃣ Looking for DM input box...")
            dm_box_selectors = [
                'div[data-testid="dmComposerTextInput"]',
                'div[contenteditable="true"][data-testid="dmComposerTextInput"]',
            ]

            dm_box = None
            for selector in dm_box_selectors:
                try:
                    dm_box = page.wait_for_selector(selector, timeout=5000)
                    if dm_box:
                        print(f"✅ Found DM input box: {selector}")
                        break
                except:
                    continue

            if not dm_box:
                print("❌ Could not find DM input box")
                return False

            # 测试输入（不实际发送）
            print("\n5️⃣ Testing message input...")
            test_message = "This is a test message (will not be sent)"
            dm_box.click()
            time.sleep(0.5)
            dm_box.type(test_message[:20], delay=50)  # 只输入前20个字符测试
            print("✅ Message input works!")

            # 查找发送按钮（不点击）
            print("\n6️⃣ Looking for Send button...")
            send_btn_selectors = [
                'div[data-testid="dmComposerSendButton"]',
                'button[data-testid="dmComposerSendButton"]',
            ]

            send_button = None
            for selector in send_btn_selectors:
                try:
                    send_button = page.wait_for_selector(selector, timeout=3000)
                    if send_button:
                        print(f"✅ Found send button: {selector}")
                        break
                except:
                    continue

            if not send_button:
                print("❌ Could not find send button")
                return False

            print("\n" + "=" * 60)
            print("✅ All DM components found!")
            print("✅ Twitter DM sending should work")
            print("=" * 60)

            print("\n⚠️  Waiting 5 seconds before closing (you can see the test)...")
            time.sleep(5)

            return True

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            try:
                browser.close()
            except:
                pass

if __name__ == "__main__":
    success = test_twitter_dm()
    sys.exit(0 if success else 1)
