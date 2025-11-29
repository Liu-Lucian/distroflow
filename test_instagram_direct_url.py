#!/usr/bin/env python3
"""
测试Instagram Direct URL方式发送DM
尝试直接访问 /direct/new/?q=username 或 /direct/t/thread_id
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Direct URL DM Test")
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
    browser = p.chromium.launch(headless=False, slow_mo=500)
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

    # 步骤1: 直接访问新建消息页面
    print(f"\n📱 Step 1: 访问 Instagram Direct (新建消息)...")
    page.goto('https://www.instagram.com/direct/new/', timeout=60000)
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

    # 步骤2: 在搜索框中输入用户名
    print(f"\n🔍 Step 2: 搜索用户 @{test_username}...")

    # 查找收件人搜索框
    recipient_input_selectors = [
        'input[placeholder*="搜索"]',
        'input[placeholder*="Search"]',
        'input[name="queryBox"]',
        'input[type="text"]',
    ]

    recipient_input = None
    for selector in recipient_input_selectors:
        try:
            elem = page.wait_for_selector(selector, timeout=3000)
            if elem:
                print(f"   ✅ 找到搜索框: {selector}")
                recipient_input = elem
                break
        except:
            pass

    if recipient_input:
        # 输入用户名
        print(f"   ✏️  输入: {test_username}")
        recipient_input.fill(test_username)
        time.sleep(3)

        # 查找搜索结果
        print("\n👤 Step 3: 查找搜索结果...")

        result_selectors = [
            f'div:has-text("{test_username}")',
            f'span:has-text("{test_username}")',
            'div[role="button"]',
            'div[role="listitem"]',
        ]

        for selector in result_selectors:
            elements = page.query_selector_all(selector)
            print(f"   {selector}: {len(elements)} 个")

        # 尝试点击第一个搜索结果
        try:
            # 等待搜索结果加载
            result = page.wait_for_selector('div[role="button"]', timeout=3000)
            if result:
                print("   ✅ 找到搜索结果，点击...")
                result.click()
                time.sleep(2)

                # 步骤4: 查找消息输入框
                print("\n📝 Step 4: 查找消息输入框...")

                input_selectors = [
                    'div[contenteditable="true"][role="textbox"]',
                    'div[contenteditable="true"]',
                    'textarea[placeholder*="Message"]',
                    'textarea[placeholder*="消息"]',
                ]

                for selector in input_selectors:
                    elements = page.query_selector_all(selector)
                    if elements:
                        print(f"   ✅ {selector}: {len(elements)} 个")
                        for i, elem in enumerate(elements):
                            visible = elem.is_visible()
                            print(f"      [{i+1}] Visible: {visible}")
                            if visible:
                                print(f"\n      🧪 测试输入...")
                                elem.click()
                                time.sleep(0.5)
                                elem.fill("Test DM from automation")
                                print(f"      ✅ 输入成功！")
                                break
                        break
                    else:
                        print(f"   ❌ {selector}: 0 个")

        except Exception as e:
            print(f"   ❌ 错误: {e}")

    else:
        print("   ❌ 没找到搜索框")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开60秒供检查...")
    print("=" * 60)

    time.sleep(60)

    browser.close()
    print("\n✅ 完成")
