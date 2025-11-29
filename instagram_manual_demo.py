#!/usr/bin/env python3
"""
Instagram DM手动演示 - 请手动执行流程，程序记录步骤
"""

import json
from playwright.sync_api import sync_playwright
import time

print("=" * 60)
print("📋 Instagram DM Manual Demo")
print("=" * 60)
print("\n你将手动演示正确的流程：")
print("1. 搜索关键词")
print("2. 点击帖子/视频")
print("3. 点击用户头像")
print("4. 点击Message按钮")
print("5. 输入消息")
print("\n程序会记录每一步的页面结构\n")

# 加载Instagram认证
with open('platforms_auth.json', 'r') as f:
    platforms = json.load(f)

sessionid = platforms.get('instagram', {}).get('sessionid', '')

if not sessionid:
    print("❌ No Instagram sessionid found")
    exit(1)

test_username = input("请输入要测试的Instagram用户名 (不带@): ").strip()

with sync_playwright() as p:
    print("\n🚀 启动浏览器...")
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

    # 访问主页
    print("\n📱 访问Instagram主页...")
    page.goto('https://www.instagram.com/', timeout=60000)
    time.sleep(2)

    if 'login' in page.url:
        print("❌ 未登录")
        browser.close()
        exit(1)

    print("✅ 已登录")

    # 步骤1: 搜索
    input("\n按Enter后，请手动：\n1. 点击搜索图标\n2. 搜索: " + test_username + "\n按Enter继续...")

    print("\n🔎 当前页面URL:", page.url)
    print("分析搜索结果...")

    # 查找搜索结果
    result_selectors = [
        f'a[href="/{test_username}/"]',
        'a[href*="' + test_username + '"]',
        'div[role="button"]',
    ]

    for selector in result_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   找到 {len(elements)} 个: {selector}")

    # 步骤2: 点击用户profile
    input("\n按Enter后，请手动点击搜索结果中的用户...按Enter继续...")

    print("\n👤 当前页面URL:", page.url)
    print("分析profile页面...")

    # 查找帖子
    post_selectors = [
        'article a[href*="/p/"]',
        'article a[href*="/reel/"]',
        'a[href*="/p/"]',
        'a[href*="/reel/"]',
    ]

    for selector in post_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   找到 {len(elements)} 个帖子: {selector}")
            if len(elements) > 0:
                # 打印第一个帖子的href
                try:
                    href = elements[0].get_attribute('href')
                    print(f"      第一个帖子: {href}")
                except:
                    pass

    # 步骤3: 点击帖子
    input("\n按Enter后，请手动点击第一个帖子...按Enter继续...")

    print("\n📸 当前页面URL:", page.url)
    print("分析帖子页面...")

    # 查找帖子中的用户链接
    user_link_selectors = [
        f'a[href="/{test_username}/"]',
        'header a',
        'h2 a',
    ]

    for selector in user_link_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   找到 {len(elements)} 个用户链接: {selector}")

    # 步骤4: 点击用户头像/名字
    input("\n按Enter后，请手动点击帖子中的用户名或头像...按Enter继续...")

    print("\n👤 当前页面URL:", page.url)
    print("分析用户页面...")

    # 查找Message按钮
    message_button_selectors = [
        'div[role="button"]:has-text("消息")',
        'div[role="button"]:has-text("Message")',
        'button:has-text("消息")',
        'button:has-text("Message")',
    ]

    for selector in message_button_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   找到 {len(elements)} 个Message按钮: {selector}")
            if len(elements) > 0:
                try:
                    text = elements[0].inner_text()
                    print(f"      按钮文本: '{text}'")
                except:
                    pass

    # 步骤5: 点击Message按钮
    input("\n按Enter后，请手动点击Message按钮...按Enter继续...")

    print("\n💬 当前页面URL:", page.url)
    print("分析消息页面...")

    # 查找消息输入框
    input_selectors = [
        'textarea[placeholder*="消息"]',
        'textarea[placeholder*="Message"]',
        'div[contenteditable="true"]',
        'textarea',
    ]

    for selector in input_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   找到 {len(elements)} 个输入框: {selector}")
            if len(elements) > 0:
                try:
                    placeholder = elements[0].get_attribute('placeholder')
                    aria_label = elements[0].get_attribute('aria-label')
                    tag = elements[0].evaluate('el => el.tagName')
                    print(f"      Tag: {tag}, Placeholder: {placeholder}, Aria: {aria_label}")
                except:
                    pass

    # 查找发送按钮
    send_selectors = [
        'button:has-text("发送")',
        'button:has-text("Send")',
        'div[role="button"]:has-text("发送")',
        'div[role="button"]:has-text("Send")',
    ]

    for selector in send_selectors:
        elements = page.query_selector_all(selector)
        if elements:
            print(f"   找到 {len(elements)} 个Send按钮: {selector}")

    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    print("\n浏览器将保持打开60秒供你检查...")

    time.sleep(60)

    browser.close()
    print("\n✅ 完成")
