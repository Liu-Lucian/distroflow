#!/usr/bin/env python3
"""
Reddit DM发送测试脚本 - 纯发送功能调试
"""

import json
import time
import random
from playwright.sync_api import sync_playwright

def test_reddit_dm():
    """测试Reddit DM发送"""

    # 测试用户
    test_users = [
        {
            'name': 'Test User 1',
            'username': 'spez',  # Reddit CEO (public account)
        },
    ]

    test_message = """Hey, I saw your profile and thought you might be interested in HireMeAI.

It's an AI-powered interview prep platform that helps candidates prepare better.

Would love your thoughts!"""

    print("=" * 70)
    print("🧪 Reddit DM发送测试")
    print("=" * 70)

    # 加载Reddit storage_state
    try:
        with open('reddit_auth.json', 'r') as f:
            storage_state = json.load(f)
    except FileNotFoundError:
        print("❌ reddit_auth.json not found")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 显示浏览器方便调试
            slow_mo=500,     # 放慢操作
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            storage_state='reddit_auth.json',
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1280, 'height': 720}
        )

        print("✅ Auth loaded from storage_state")

        page = context.new_page()

        for i, user in enumerate(test_users, 1):
            username = user['username']
            print(f"\n[{i}/{len(test_users)}] Testing DM to u/{username}...")

            try:
                # 步骤1: 访问用户profile
                print("   📱 Opening profile...")
                profile_url = f"https://www.reddit.com/user/{username}"
                page.goto(profile_url, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)

                # 检查是否登录
                if 'login' in page.url:
                    print("   ❌ Not logged in!")
                    continue

                # 步骤2: 查找Chat/Message按钮
                print("   🔍 Looking for Chat/Message button...")
                message_button_selectors = [
                    'button:has-text("Chat")',
                    'button:has-text("Send Message")',
                    'a:has-text("Send Message")',
                    'a[href*="/message/compose"]',
                ]

                message_button = None
                for selector in message_button_selectors:
                    try:
                        btn = page.wait_for_selector(selector, timeout=3000)
                        if btn and btn.is_visible():
                            message_button = btn
                            print(f"   ✅ Found button: {selector}")
                            break
                    except:
                        continue

                if not message_button:
                    print("   ❌ No message button found")
                    # 尝试直接访问compose URL
                    print("   ℹ️  Trying direct compose URL...")
                    compose_url = f"https://www.reddit.com/message/compose/?to={username}"
                    page.goto(compose_url, wait_until='domcontentloaded')
                    time.sleep(3)
                else:
                    # 点击Chat/Message按钮
                    print("   👆 Clicking button...")
                    message_button.click()
                    time.sleep(3)

                # 步骤3: 查找输入框（Chat或Compose模式）
                print("   🔍 Looking for input box...")

                # 先截图看看当前状态
                page.screenshot(path=f"reddit_debug_before_{i}.png")
                print(f"   📸 Screenshot saved: reddit_debug_before_{i}.png")

                input_selectors = [
                    'textarea[name="message"]',           # Chat模式
                    'textarea[name="message-content"]',   # Compose模式
                    'textarea[placeholder*="Message"]',
                    'div[contenteditable="true"]',
                    'textarea[placeholder*="Say"]',       # Chat: "Say something nice"
                ]

                input_box = None
                for selector in input_selectors:
                    try:
                        box = page.wait_for_selector(selector, timeout=3000)
                        if box and box.is_visible():
                            input_box = box
                            print(f"   ✅ Found input: {selector}")
                            break
                    except:
                        continue

                # 如果还是找不到，列出所有textarea
                if not input_box:
                    print("   ℹ️  Listing all textareas...")
                    all_textareas = page.query_selector_all('textarea')
                    for idx, ta in enumerate(all_textareas):
                        if ta.is_visible():
                            name = ta.get_attribute('name') or 'no-name'
                            placeholder = ta.get_attribute('placeholder') or 'no-placeholder'
                            print(f"      Textarea {idx}: name={name}, placeholder={placeholder}")
                            if not input_box:
                                input_box = ta

                if not input_box:
                    print("   ❌ No input box found")
                    page.screenshot(path=f"reddit_no_input_{i}.png")
                    print(f"   📸 Screenshot: reddit_no_input_{i}.png")
                    continue

                # 步骤4: 输入消息
                print("   ⌨️  Typing message...")
                try:
                    input_box.click()
                    time.sleep(random.uniform(0.5, 1.0))
                    input_box.fill(test_message)
                    time.sleep(random.uniform(0.8, 1.5))
                    print("   ✅ Message typed!")

                    # 触发input事件
                    page.evaluate('''(el) => {
                        el.dispatchEvent(new Event('input', { bubbles: true }));
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }''', input_box)
                    time.sleep(1)

                except Exception as e:
                    print(f"   ❌ Failed to type: {e}")
                    continue

                # 步骤5: 查找Send按钮（关键！）
                print("   🔍 Looking for Send button...")

                # 截图看看输入后的状态
                page.screenshot(path=f"reddit_debug_after_{i}.png")
                print(f"   📸 Screenshot saved: reddit_debug_after_{i}.png")

                # 列出所有可见按钮
                print("   ℹ️  Listing all visible buttons...")
                all_buttons = page.query_selector_all('button')
                for idx, btn in enumerate(all_buttons):
                    if btn.is_visible():
                        text = btn.inner_text() or 'no-text'
                        btn_type = btn.get_attribute('type') or 'no-type'
                        aria_label = btn.get_attribute('aria-label') or 'no-aria'
                        print(f"      Button {idx}: text='{text}', type={btn_type}, aria-label='{aria_label}'")

                send_selectors = [
                    'button[type="submit"]',
                    'button:has-text("Send")',
                    'button:has-text("send")',
                    'button[aria-label*="Send"]',
                    'button[aria-label*="send"]',
                    # Chat模式可能用图标按钮
                    'button[aria-label*="Submit"]',
                    'button svg',  # 可能是图标按钮
                ]

                send_button = None
                for selector in send_selectors:
                    try:
                        btns = page.query_selector_all(selector)
                        for btn in btns:
                            if btn.is_visible():
                                send_button = btn
                                print(f"   ✅ Found send button: {selector}")
                                break
                        if send_button:
                            break
                    except:
                        continue

                if not send_button:
                    print("   ❌ No Send button found")
                    page.screenshot(path=f"reddit_no_send_{i}.png")
                    print(f"   📸 Screenshot: reddit_no_send_{i}.png")
                    print("\n   💡 Please check the screenshot to see what buttons are available")
                    continue

                # 显示准备发送（但不实际发送）
                print("\n" + "=" * 70)
                print("✅ Message is ready to send!")
                print("=" * 70)
                print(f"To: u/{username}")
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
                # 出错时截图
                try:
                    page.screenshot(path=f"reddit_error_{i}.png")
                    print(f"   📸 Error screenshot: reddit_error_{i}.png")
                except:
                    pass

        print("\n" + "=" * 70)
        print("✅ Test complete!")
        print("=" * 70)
        print("\n⏸️  Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    test_reddit_dm()
