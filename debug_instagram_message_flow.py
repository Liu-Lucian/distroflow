#!/usr/bin/env python3
"""
调试Instagram Message按钮点击后的流程
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("🔍 Instagram Message Button Click Debugger")
print("=" * 60)

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

test_username = "startupgrind"  # 测试用户

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

    # 步骤1: 访问用户profile
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

    # 步骤2: 滚动并点击第一个帖子
    print("\n📸 Step 2: 滚动并点击第一个帖子...")
    page.evaluate("window.scrollTo(0, 500)")
    time.sleep(2)

    posts = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
    print(f"   找到 {len(posts)} 个帖子")

    if posts:
        first_post = posts[0]
        href = first_post.get_attribute('href')
        print(f"   点击帖子: {href}")
        page.evaluate('(element) => element.click()', first_post)
        time.sleep(4)

        print(f"   点击后URL: {page.url}")

        # 步骤3: 查找所有可能的Message按钮
        print("\n💬 Step 3: 查找所有Message按钮...")

        message_selectors = [
            'div[role="button"]:has-text("消息")',
            'a:has-text("消息")',
            'button:has-text("消息")',
            'div[role="button"]:has-text("Message")',
            'a:has-text("Message")',
            'button:has-text("Message")',
        ]

        all_message_buttons = []
        for selector in message_selectors:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"   ✅ {selector}: {len(elements)} 个")
                for i, elem in enumerate(elements):
                    try:
                        text = elem.inner_text()
                        visible = elem.is_visible()
                        print(f"      [{i+1}] Text: '{text}', Visible: {visible}")
                        if visible:
                            all_message_buttons.append((selector, elem, i))
                    except:
                        pass
            else:
                print(f"   ❌ {selector}: 0 个")

        if all_message_buttons:
            print(f"\n🎯 找到 {len(all_message_buttons)} 个可见的Message按钮")
            print("   选择第一个可见按钮点击...")

            selector, button, idx = all_message_buttons[0]
            print(f"   点击: {selector} (index {idx})")
            # 使用JavaScript点击避免overlay问题
            page.evaluate('(element) => element.click()', button)
            time.sleep(5)

            print(f"\n   点击后URL: {page.url}")

            # 步骤4: 查找消息输入框
            print("\n📝 Step 4: 查找消息输入框...")

            input_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[contenteditable="true"]',
                'textarea[placeholder*="Message"]',
                'textarea[placeholder*="消息"]',
                'div[aria-label*="Message"]',
                'div[aria-label*="消息"]',
            ]

            for selector in input_selectors:
                elements = page.query_selector_all(selector)
                count = len(elements)
                print(f"   {selector}: {count} 个")

                if count > 0:
                    for i, elem in enumerate(elements[:3]):
                        try:
                            visible = elem.is_visible()
                            aria_label = elem.get_attribute('aria-label')
                            placeholder = elem.get_attribute('placeholder')
                            print(f"      [{i+1}] Visible: {visible}, aria-label: {aria_label}, placeholder: {placeholder}")
                        except Exception as e:
                            print(f"      [{i+1}] 无法获取属性: {e}")

            # Debug: 查找所有输入元素
            print("\n🔍 Debug: 所有输入元素...")
            all_textareas = page.query_selector_all('textarea')
            all_contenteditable = page.query_selector_all('[contenteditable="true"]')
            all_inputs = page.query_selector_all('input[type="text"]')

            print(f"   textareas: {len(all_textareas)} 个")
            for i, ta in enumerate(all_textareas):
                try:
                    placeholder = ta.get_attribute('placeholder')
                    aria_label = ta.get_attribute('aria-label')
                    visible = ta.is_visible()
                    print(f"      [{i+1}] placeholder: {placeholder}, aria-label: {aria_label}, visible: {visible}")
                except Exception as e:
                    print(f"      [{i+1}] 无法获取属性: {e}")

            print(f"   contenteditable: {len(all_contenteditable)} 个")
            print(f"   text inputs: {len(all_inputs)} 个")

            # 检查是否出现了登录提示或其他弹窗
            print("\n🔍 检查是否有弹窗或错误...")
            modals = page.query_selector_all('[role="dialog"]')
            print(f"   找到 {len(modals)} 个dialog弹窗")

            # 检查页面上的所有按钮文本
            print("\n🔍 页面上的所有按钮...")
            all_buttons = page.query_selector_all('button, div[role="button"], a[role="button"]')
            print(f"   找到 {len(all_buttons)} 个按钮")
            for i, btn in enumerate(all_buttons[:10]):  # 只显示前10个
                try:
                    text = btn.inner_text().strip()
                    if text and len(text) < 30:
                        print(f"      [{i+1}] {text}")
                except:
                    pass

        else:
            print("\n❌ 没有找到可见的Message按钮")

    else:
        print("   ❌ 没找到帖子")

    print("\n" + "=" * 60)
    print("⏸️  浏览器将保持打开90秒供检查...")
    print("=" * 60)

    time.sleep(90)

    browser.close()
    print("\n✅ 完成")
