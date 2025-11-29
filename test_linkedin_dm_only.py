#!/usr/bin/env python3
"""
LinkedIn DM发送测试脚本 - 纯发送功能调试
"""

import json
import time
import random
from playwright.sync_api import sync_playwright

def test_linkedin_dm():
    """测试LinkedIn DM发送"""

    # 测试用户（你可以换成任何LinkedIn profile URL）
    test_users = [
        {
            'name': 'Test User 1',
            'profile_url': 'https://www.linkedin.com/in/williamhgates/',  # Bill Gates (public profile)
        },
    ]

    test_message = """Hey, I saw your profile and thought you might be interested in HireMeAI.

It's an AI-powered interview prep platform that helps candidates prepare better.

Would love your thoughts!"""

    print("=" * 70)
    print("🧪 LinkedIn DM发送测试")
    print("=" * 70)

    # 加载LinkedIn cookies
    try:
        with open('linkedin_auth.json', 'r') as f:
            auth = json.load(f)
            cookies = auth.get('cookies', [])
    except FileNotFoundError:
        print("❌ linkedin_auth.json not found")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器方便调试
            slow_mo=500,     # 放慢操作
        )

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1280, 'height': 720}
        )

        # 加载cookies
        if cookies:
            context.add_cookies(cookies)
            print("✅ Cookies loaded")

        page = context.new_page()

        for i, user in enumerate(test_users, 1):
            print(f"\n[{i}/{len(test_users)}] Testing DM to {user['name']}...")
            print(f"   Profile: {user['profile_url']}")

            try:
                # 访问profile
                print("   📱 Opening profile...")
                page.goto(user['profile_url'], wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)

                # 检查是否登录
                if 'authwall' in page.url or 'login' in page.url:
                    print("   ❌ Not logged in!")
                    continue

                # 查找Message按钮
                print("   🔍 Looking for Message button...")
                message_button_selectors = [
                    'button:has-text("Message")',
                    'a:has-text("Message")',
                    '.artdeco-button:has-text("Message")',
                ]

                message_button = None
                for selector in message_button_selectors:
                    try:
                        btn = page.wait_for_selector(selector, timeout=3000)
                        if btn and btn.is_visible():
                            message_button = btn
                            print(f"   ✅ Found Message button: {selector}")
                            break
                    except:
                        continue

                if not message_button:
                    print("   ❌ No Message button found")
                    continue

                # 点击Message按钮
                print("   👆 Clicking Message button...")
                message_button.click()
                time.sleep(2)

                # 查找输入框
                print("   🔍 Looking for input box...")
                input_selectors = [
                    'div[contenteditable="true"]',
                    'div.msg-form__contenteditable',
                    'div.msg-form__msg-content-container',
                ]

                input_box = None
                for selector in input_selectors:
                    try:
                        box = page.wait_for_selector(selector, timeout=5000, state='visible')
                        if box:
                            input_box = box
                            print(f"   ✅ Found input box: {selector}")
                            break
                    except:
                        continue

                if not input_box:
                    print("   ❌ No input box found")
                    # 截图调试
                    page.screenshot(path=f"linkedin_debug_{i}.png")
                    print(f"   📸 Screenshot saved: linkedin_debug_{i}.png")
                    continue

                # 输入消息
                print("   ⌨️  Typing message...")
                try:
                    # 滚动到视图
                    input_box.scroll_into_view_if_needed()
                    time.sleep(0.3)

                    # 点击激活（force=True避免遮挡）
                    input_box.click(force=True)
                    time.sleep(random.uniform(0.5, 1.0))

                    # 填写消息
                    input_box.fill(test_message)
                    time.sleep(random.uniform(0.8, 1.5))

                    print("   ✅ Message typed successfully!")

                except Exception as e:
                    print(f"   ❌ Failed to type: {e}")
                    # 尝试重试
                    print("   🔄 Retrying...")
                    try:
                        fresh_input = page.wait_for_selector(input_selectors[0], timeout=5000)
                        if fresh_input and fresh_input.is_visible():
                            fresh_input.click(force=True)
                            time.sleep(0.5)
                            fresh_input.fill(test_message)
                            time.sleep(1)
                            print("   ✅ Retry succeeded!")
                        else:
                            raise Exception("Cannot find input on retry")
                    except Exception as e2:
                        print(f"   ❌ Retry failed: {e2}")
                        page.screenshot(path=f"linkedin_error_{i}.png")
                        print(f"   📸 Error screenshot: linkedin_error_{i}.png")
                        continue

                # 查找Send按钮
                print("   🔍 Looking for Send button...")
                send_selectors = [
                    'button:has-text("Send")',
                    'button[type="submit"]',
                    'button[aria-label*="Send"]',
                ]

                send_button = None
                for selector in send_selectors:
                    try:
                        btn = page.query_selector(selector)
                        if btn and btn.is_enabled():
                            send_button = btn
                            print(f"   ✅ Found Send button: {selector}")
                            break
                    except:
                        continue

                if not send_button:
                    print("   ❌ No Send button found")
                    page.screenshot(path=f"linkedin_no_send_{i}.png")
                    print(f"   📸 Screenshot: linkedin_no_send_{i}.png")
                    continue

                # 显示准备发送（但不实际发送，避免骚扰测试用户）
                print("\n" + "=" * 70)
                print("✅ Message is ready to send!")
                print("=" * 70)
                print(f"To: {user['name']}")
                print(f"Message: {test_message[:50]}...")
                print("\n⏭️  Skipping actual send (test mode)")
                print("   (To actually send, uncomment send_button.click() in code)")

                # 测试模式：不实际发送
                # send_button.click()
                # print("   ✅ Message sent!")
                # time.sleep(2)

            except Exception as e:
                print(f"   ❌ Error: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 70)
        print("✅ Test complete!")
        print("=" * 70)
        print("\n⏸️  Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    test_linkedin_dm()
