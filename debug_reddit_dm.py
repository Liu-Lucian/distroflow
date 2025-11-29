#!/usr/bin/env python3
"""
调试Reddit DM发送 - 自动截图并测试
"""

import json
from playwright.sync_api import sync_playwright
import time

def test_reddit_dm():
    """测试Reddit DM发送，截图每一步"""

    # 测试用户
    test_username = "test"  # 会尝试发送给这个用户（不会真的发送）

    print("=" * 70)
    print("🔍 Reddit DM Debug Tool")
    print("=" * 70)

    # 加载认证
    with open('reddit_auth.json', 'r') as f:
        storage_state = json.load(f)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,  # 显示浏览器
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            storage_state=storage_state,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 900}
        )

        page = context.new_page()

        # 添加反检测
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        print(f"\n📱 Step 1: Opening compose URL directly...")
        compose_url = f"https://www.reddit.com/message/compose/?to={test_username}"
        page.goto(compose_url, wait_until='domcontentloaded', timeout=30000)

        print("⏳ Waiting 5 seconds for page load...")
        time.sleep(5)

        # 截图1：初始页面
        page.screenshot(path="debug_reddit_dm_step1_initial.png")
        print("📸 Screenshot 1: Initial compose page")

        # 检查URL
        print(f"\n🔗 Current URL: {page.url}")

        # 检查是否登录
        if 'login' in page.url.lower():
            print("❌ Not logged in! Please run reddit_login_and_save_auth.py first")
            browser.close()
            return

        print("\n" + "=" * 70)
        print("📝 Step 2: Looking for form elements...")
        print("=" * 70)

        # 尝试找到所有可能的textarea
        all_textareas = page.query_selector_all('textarea')
        print(f"\nFound {len(all_textareas)} textarea elements total")

        for i, textarea in enumerate(all_textareas, 1):
            try:
                name = textarea.get_attribute('name') or '(no name)'
                placeholder = textarea.get_attribute('placeholder') or '(no placeholder)'
                visible = textarea.is_visible()
                print(f"\n  Textarea {i}:")
                print(f"    name: {name}")
                print(f"    placeholder: {placeholder}")
                print(f"    visible: {visible}")
            except Exception as e:
                print(f"    Error: {e}")

        # 尝试找到所有input
        all_inputs = page.query_selector_all('input[type="text"], input:not([type])')
        print(f"\n\nFound {len(all_inputs)} input elements")

        for i, inp in enumerate(all_inputs[:5], 1):  # 只看前5个
            try:
                name = inp.get_attribute('name') or '(no name)'
                placeholder = inp.get_attribute('placeholder') or '(no placeholder)'
                input_type = inp.get_attribute('type') or '(no type)'
                visible = inp.is_visible()
                print(f"\n  Input {i}:")
                print(f"    name: {name}")
                print(f"    type: {input_type}")
                print(f"    placeholder: {placeholder}")
                print(f"    visible: {visible}")
            except Exception as e:
                print(f"    Error: {e}")

        print("\n" + "=" * 70)
        print("📝 Step 3: Testing different selectors...")
        print("=" * 70)

        # 测试各种选择器
        selectors_to_test = [
            ('Subject input', [
                'input[name="to"]',
                'input[name="subject"]',
                'input[name="message-title"]',
                'input[placeholder*="subject"]',
                'input[placeholder*="Subject"]',
            ]),
            ('Message textarea', [
                'textarea[name="text"]',
                'textarea[name="message"]',
                'textarea[name="message-content"]',
                'textarea[name="body"]',
                'textarea[placeholder*="message"]',
                'textarea[placeholder*="Message"]',
                'textarea',
            ]),
        ]

        results = {}

        for field_name, selectors in selectors_to_test:
            print(f"\n{field_name}:")
            found = False
            for selector in selectors:
                try:
                    elem = page.query_selector(selector)
                    if elem:
                        visible = elem.is_visible()
                        print(f"  ✅ {selector}: Found (visible={visible})")
                        if visible and not found:
                            results[field_name] = selector
                            found = True
                    else:
                        print(f"  ❌ {selector}: Not found")
                except Exception as e:
                    print(f"  ❌ {selector}: Error - {e}")

        # 截图2：调试后
        page.screenshot(path="debug_reddit_dm_step2_analysis.png", full_page=True)
        print("\n📸 Screenshot 2: Full page after analysis")

        print("\n" + "=" * 70)
        print("✅ Best Selectors Found:")
        print("=" * 70)
        for field, selector in results.items():
            print(f"  {field}: {selector}")

        # 如果找到了message textarea，尝试填写
        if 'Message textarea' in results:
            print("\n" + "=" * 70)
            print("📝 Step 4: Testing message input...")
            print("=" * 70)

            try:
                message_box = page.query_selector(results['Message textarea'])
                if message_box and message_box.is_visible():
                    print("\n✅ Found message box, testing input...")

                    # 填写测试消息
                    test_message = "This is a test message (will NOT be sent)"

                    message_box.click()
                    time.sleep(0.5)
                    message_box.type(test_message, delay=50)
                    time.sleep(1)

                    print("✅ Successfully typed test message!")

                    # 截图3：填写后
                    page.screenshot(path="debug_reddit_dm_step3_filled.png")
                    print("📸 Screenshot 3: After typing message")

                    # 查找发送按钮
                    print("\n🔍 Looking for send button...")
                    send_selectors = [
                        'button[type="submit"]',
                        'button:has-text("Send")',
                        'button:has-text("send")',
                        'input[type="submit"]',
                    ]

                    send_button = None
                    for selector in send_selectors:
                        try:
                            btn = page.query_selector(selector)
                            if btn and btn.is_visible():
                                print(f"  ✅ Found send button: {selector}")
                                send_button = btn
                                break
                            else:
                                print(f"  ❌ {selector}: Not found or not visible")
                        except Exception as e:
                            print(f"  ❌ {selector}: Error - {e}")

                    if send_button:
                        print("\n✅ Send button found!")
                        print("⚠️  NOT clicking send button (test mode)")
                    else:
                        print("\n❌ Send button not found")

            except Exception as e:
                print(f"\n❌ Error testing input: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 70)
        print("✅ Debug Complete!")
        print("=" * 70)
        print("\nScreenshots saved:")
        print("  - debug_reddit_dm_step1_initial.png")
        print("  - debug_reddit_dm_step2_analysis.png")
        if 'Message textarea' in results:
            print("  - debug_reddit_dm_step3_filled.png")
        print("\n⏸️  Browser will stay open for 30 seconds for manual inspection...")

        time.sleep(30)

        browser.close()

if __name__ == "__main__":
    try:
        test_reddit_dm()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
