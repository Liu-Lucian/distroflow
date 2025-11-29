#!/usr/bin/env python3
"""
测试直接从profile页面点击"发消息"按钮
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Profile Message Button Test")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

test_username = "startupgrind"

with sync_playwright() as p:
    print(f"\n🚀 启动浏览器...")
    browser = p.chromium.launch(headless=False, slow_mo=800)
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

    # 步骤1: 直接访问用户profile
    print(f"\n📱 Step 1: 访问 @{test_username} profile...")
    page.goto(f'https://www.instagram.com/{test_username}/', timeout=60000)
    time.sleep(3)

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

    # 步骤2: 在profile页面直接查找"发消息"/"消息"按钮
    print("\n💬 Step 2: 在profile页面查找Message按钮...")

    # 这些是profile页面上的按钮选择器
    profile_message_selectors = [
        'div:has-text("发消息")',  # 中文 "Send Message"
        'button:has-text("发消息")',
        'div[role="button"]:has-text("发消息")',
        'div:has-text("消息")',  # 简短版 "Message"
        'button:has-text("消息")',
        'div[role="button"]:has-text("消息")',
        'div:has-text("Message")',  # 英文
        'button:has-text("Message")',
        'div[role="button"]:has-text("Message")',
    ]

    message_button = None
    for selector in profile_message_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   ✅ {selector}: {len(elements)} 个")
            for i, elem in enumerate(elements):
                try:
                    text = elem.inner_text().strip()
                    visible = elem.is_visible()
                    print(f"      [{i+1}] Text: '{text}', Visible: {visible}")
                    if visible and not message_button:
                        message_button = elem
                except:
                    pass
        else:
            print(f"   ❌ {selector}: 0 个")

    if message_button:
        print("\n🎯 找到Message按钮，尝试点击...")
        # 使用JavaScript点击
        page.evaluate('(element) => element.click()', message_button)
        time.sleep(5)

        print(f"   点击后URL: {page.url}")

        # 查找DM输入框
        print("\n📝 Step 3: 查找消息输入框...")

        input_selectors = [
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="消息"]',
            'div[aria-label*="Message"]',
            'div[aria-label*="消息"]',
        ]

        found_input = False
        for selector in input_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"   ✅ {selector}: {len(elements)} 个")
                for i, elem in enumerate(elements):
                    try:
                        visible = elem.is_visible()
                        aria_label = elem.get_attribute('aria-label')
                        placeholder = elem.get_attribute('placeholder')
                        print(f"      [{i+1}] Visible: {visible}, aria-label: {aria_label}, placeholder: {placeholder}")
                        if visible and not found_input:
                            found_input = True
                            print(f"\n      🧪 测试输入...")
                            elem.click()
                            time.sleep(0.5)
                            elem.fill("Test message from automation")
                            print(f"      ✅ 输入成功！")
                    except Exception as e:
                        print(f"      [{i+1}] 错误: {e}")
            else:
                print(f"   ❌ {selector}: 0 个")

        if not found_input:
            print("\n   ⚠️ 没找到输入框")
            print("   检查所有输入元素...")
            all_textareas = page.query_selector_all('textarea')
            all_contenteditable = page.query_selector_all('[contenteditable="true"]')
            print(f"   textareas: {len(all_textareas)} 个")
            print(f"   contenteditable: {len(all_contenteditable)} 个")

    else:
        print("\n❌ 没有找到Message按钮")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开60秒供检查...")
    print("=" * 60)

    time.sleep(60)

    browser.close()
    print("\n✅ 完成")
