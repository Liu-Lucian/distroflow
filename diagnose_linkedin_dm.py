#!/usr/bin/env python3
"""
LinkedIn DM 诊断脚本 - 截图分析输入框问题
"""
import json
import time
from playwright.sync_api import sync_playwright

# 测试用户（从qualified users中选一个）
TEST_USER_URL = "https://www.linkedin.com/in/carpenternancy"

def diagnose_dm_issue():
    """诊断DM发送问题"""

    # 加载认证
    with open('linkedin_auth.json', 'r') as f:
        storage_state = json.load(f)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,  # 可见模式
            args=['--disable-blink-features=AutomationControlled']
        )

        context = browser.new_context(
            storage_state=storage_state,
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

        page = context.new_page()

        print(f"🔍 Testing DM to: {TEST_USER_URL}")

        # 访问用户页面
        page.goto(TEST_USER_URL, timeout=30000)
        time.sleep(3)

        # 截图1: 用户profile页面
        page.screenshot(path='debug_linkedin_profile.png')
        print("📸 Screenshot 1: Profile page saved")

        # 查找并点击Message按钮
        print("\n🔍 Looking for Message button...")
        message_btn_selectors = [
            'button:has-text("Message")',
            'a:has-text("Message")',
            'button[aria-label*="Message"]',
        ]

        message_btn = None
        for selector in message_btn_selectors:
            try:
                btn = page.wait_for_selector(selector, timeout=5000)
                if btn and btn.is_visible():
                    message_btn = btn
                    print(f"✅ Found Message button with selector: {selector}")
                    break
            except:
                continue

        if not message_btn:
            print("❌ No Message button found!")
            browser.close()
            return

        # 点击Message按钮
        print("🖱️ Clicking Message button...")
        message_btn.click()
        time.sleep(5)  # 等待足够长时间让消息框完全加载

        # 截图2: 点击Message后
        page.screenshot(path='debug_linkedin_message_clicked.png')
        print("📸 Screenshot 2: After clicking Message saved")

        # 尝试查找输入框
        print("\n🔍 Looking for message input...")
        input_selectors = [
            'div[contenteditable="true"]',
            'div[role="textbox"]',
            'div.msg-form__contenteditable',
            'div.msg-form__contenteditable p',
            'textarea[placeholder*="message"]',
            '.msg-form__msg-content-container div[contenteditable]',
            '[data-placeholder*="message"]',
        ]

        found_inputs = []
        for selector in input_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    for elem in elements:
                        if elem.is_visible():
                            found_inputs.append({
                                'selector': selector,
                                'count': len(elements),
                                'visible': True
                            })
                            print(f"✅ Found {len(elements)} visible element(s) with: {selector}")
                            break
            except Exception as e:
                print(f"❌ Selector failed: {selector} - {e}")

        if not found_inputs:
            print("\n⚠️  No input found with any selector!")
            print("📋 Saving page HTML for analysis...")
            with open('debug_linkedin_message_page.html', 'w') as f:
                f.write(page.content())
            print("💾 HTML saved to debug_linkedin_message_page.html")
        else:
            print(f"\n✅ Found {len(found_inputs)} input selectors")

        # 截图3: 最终状态
        page.screenshot(path='debug_linkedin_final.png')
        print("📸 Screenshot 3: Final state saved")

        print("\n⏸️  Pausing for 30 seconds for manual inspection...")
        time.sleep(30)

        browser.close()

        print("\n📊 Diagnosis complete!")
        print("📁 Files saved:")
        print("   - debug_linkedin_profile.png")
        print("   - debug_linkedin_message_clicked.png")
        print("   - debug_linkedin_final.png")
        if not found_inputs:
            print("   - debug_linkedin_message_page.html")

if __name__ == "__main__":
    diagnose_dm_issue()
