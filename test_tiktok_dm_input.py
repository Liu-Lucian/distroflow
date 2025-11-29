#!/usr/bin/env python3
"""
测试TikTok DM输入框选择器
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright

print("=" * 70)
print("🔍 TikTok DM Input Selector Finder")
print("=" * 70)

# 加载认证
with open('platforms_auth.json', 'r') as f:
    auth = json.load(f)
    sessionid = auth['tiktok']['sessionid']

# 测试用户（从qualified users中获取）
TEST_USER = "sebastian Ogene"  # 或者改成实际的用户名

print(f"\n👤 测试用户: @{TEST_USER}")
print(f"🎯 目标: 找到消息输入框的选择器\n")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        slow_mo=1000,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    context.add_cookies([{
        'name': 'sessionid',
        'value': sessionid,
        'domain': '.tiktok.com',
        'path': '/'
    }])

    page = context.new_page()

    # 访问用户主页
    username_clean = TEST_USER.replace('@', '').strip()
    profile_url = f"https://www.tiktok.com/@{username_clean}"

    print(f"📱 访问主页: {profile_url}")
    page.goto(profile_url, timeout=30000)
    time.sleep(3)

    # 点击Message按钮
    print("💬 查找并点击Message按钮...")
    message_selectors = [
        'button[data-e2e="message-button"]',
        'button:has-text("Message")',
        'button:has-text("消息")',
        '[aria-label*="Message"]',
        'button[class*="message"]',
    ]

    message_button = None
    for selector in message_selectors:
        try:
            btn = page.wait_for_selector(selector, timeout=2000)
            if btn:
                message_button = btn
                print(f"   ✅ 找到Message按钮: {selector}")
                break
        except:
            continue

    if message_button:
        message_button.click()
        print("   ✅ 已点击Message按钮")
        time.sleep(4)  # 等待消息窗口打开

        # 尝试查找输入框
        print("\n🔍 尝试查找输入框...")

        input_selectors = [
            # 常见输入框选择器
            'textarea[data-e2e="dm-input"]',
            'textarea[placeholder*="Message"]',
            'textarea[placeholder*="消息"]',
            'div[contenteditable="true"]',
            'textarea',
            'input[type="text"]',
            '[role="textbox"]',
            'div[class*="input"]',
            'div[class*="message-input"]',
        ]

        found_inputs = []
        for selector in input_selectors:
            try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"   ✅ '{selector}': {len(elements)} 个元素")
                    for i, elem in enumerate(elements):
                        # 检查是否可见
                        is_visible = elem.is_visible()
                        placeholder = elem.get_attribute('placeholder') or ''
                        class_name = elem.get_attribute('class') or ''

                        print(f"      [{i}] 可见={is_visible}, placeholder='{placeholder[:30]}'")
                        print(f"          class='{class_name[:50]}'")

                        if is_visible:
                            found_inputs.append({
                                'selector': selector,
                                'index': i,
                                'placeholder': placeholder,
                                'class': class_name
                            })
            except Exception as e:
                pass

        if found_inputs:
            print(f"\n✅ 找到 {len(found_inputs)} 个可见的输入框")
            print("\n推荐使用以下选择器:")
            for inp in found_inputs[:3]:  # 显示前3个
                print(f"   - {inp['selector']}")
        else:
            print("\n❌ 未找到可见的输入框")
            print("\n💡 手动检查:")
            print("   1. 浏览器窗口应该显示TikTok消息界面")
            print("   2. 右键点击输入框 → Inspect")
            print("   3. 查看HTML属性（class, id, data-e2e等）")
            print("   4. 更新 tiktok_dm_sender_optimized.py 中的 input_selectors")

        print("\n⏸  浏览器保持打开60秒供手动检查...")
        print("   (你可以手动测试输入框)\n")
        time.sleep(60)
    else:
        print("❌ 未找到Message按钮")

    browser.close()

print("\n✅ 完成")
