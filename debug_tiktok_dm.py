#!/usr/bin/env python3
"""
调试TikTok DM页面结构
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 TikTok DM Debugger")
print("=" * 60)

# 加载TikTok认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

tiktok_config = platforms.get('tiktok', {})
sessionid = tiktok_config.get('sessionid', '')

if not sessionid:
    print("❌ No TikTok sessionid found")
    exit(1)

print("✅ Found TikTok sessionid")

test_username = 'garyvee'

with sync_playwright() as p:
    print(f"\n🚀 启动浏览器，访问 @{test_username}...")
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 900}
    )

    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.tiktok.com',
        'path': '/'
    }])

    page = context.new_page()

    # 访问用户profile
    print(f"\n📱 访问 @{test_username} 的TikTok profile...")
    page.goto(f'https://www.tiktok.com/@{test_username}', timeout=60000)
    time.sleep(3)

    print(f"当前URL: {page.url}")

    # 查找Message按钮
    print("\n🔎 查找Message按钮...")
    message_button_selectors = [
        'button:has-text("消息")',  # 中文
        'button:has-text("Message")',  # 英文
        'button[data-e2e="message-button"]',
        'div[data-e2e="message-button"]',
    ]

    message_button = None
    for selector in message_button_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   ✅ {selector}: {len(elements)} 个")
            message_button = elements[0]
            break
        else:
            print(f"   ❌ {selector}: 0 个")

    if message_button:
        print("\n💬 点击Message按钮...")
        message_button.click()
        time.sleep(3)

        print(f"点击后URL: {page.url}")

        # 查找消息输入框
        print("\n🔎 查找消息输入框...")
        input_selectors = [
            'div[contenteditable="true"][data-e2e="message-input"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="message"]',
            'div[contenteditable="true"]',
            'textarea',
            'input[type="text"]',
        ]

        for selector in input_selectors:
            elements = page.query_selector_all(selector)
            count = len(elements)
            print(f"   {selector}: {count} 个")

            if count > 0:
                elem = elements[0]
                try:
                    placeholder = elem.get_attribute('placeholder')
                    data_e2e = elem.get_attribute('data-e2e')
                    tag = elem.evaluate('el => el.tagName')
                    print(f"      Tag: {tag}, Placeholder: {placeholder}, data-e2e: {data_e2e}")
                except Exception as e:
                    print(f"      无法获取属性: {e}")

        # 查找Send按钮
        print("\n🔎 查找Send按钮...")
        send_selectors = [
            'button[data-e2e="message-send-button"]',
            'button:has-text("Send")',
            'button[type="submit"]',
        ]

        for selector in send_selectors:
            elements = page.query_selector_all(selector)
            print(f"   {selector}: {len(elements)} 个")

    else:
        print("\n❌ 没有找到Message按钮")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开60秒，你可以手动查看")
    print("=" * 60)

    time.sleep(60)

    browser.close()
    print("\n✅ 完成")
