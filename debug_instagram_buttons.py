#!/usr/bin/env python3
"""
Instagram按钮探测脚本 - 找出Message按钮的真实选择器
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright

# 加载认证
with open('platforms_auth.json', 'r') as f:
    config = json.load(f)
sessionid = config.get('instagram', {}).get('sessionid', '')

print("=" * 70)
print("🔍 Instagram Button Detection Script")
print("=" * 70)

# 测试用户名
try:
    with open('instagram_qualified_users.json', 'r') as f:
        users = json.load(f)
    test_user = users[0]['username'].lstrip('@') if users else input("Enter test username: ")
except:
    test_user = input("Enter test username: ")

print(f"📱 Test user: @{test_user}")
print()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        viewport={'width': 1280, 'height': 720}
    )

    if sessionid:
        context.add_cookies([{
            'name': 'sessionid',
            'value': sessionid,
            'domain': '.instagram.com',
            'path': '/'
        }])

    page = context.new_page()

    # 访问用户profile
    print(f"📱 Going to profile...")
    page.goto(f'https://www.instagram.com/{test_user}/', timeout=30000)
    time.sleep(3)

    # 关闭弹窗
    try:
        not_now = page.query_selector('button:has-text("Not Now")')
        if not_now:
            not_now.click()
            time.sleep(1)
    except:
        pass

    print("\n" + "=" * 70)
    print("🔍 ANALYZING PAGE BUTTONS")
    print("=" * 70)

    # 1. 查找所有button元素
    print("\n1️⃣  ALL <button> ELEMENTS:")
    buttons = page.query_selector_all('button')
    print(f"   Found {len(buttons)} button elements\n")

    for i, btn in enumerate(buttons):
        if btn.is_visible():
            text = btn.inner_text().strip() if btn.inner_text() else ""
            aria_label = btn.get_attribute('aria-label') or ""
            role = btn.get_attribute('role') or ""
            print(f"   [{i}] Button:")
            print(f"       Text: '{text}'")
            print(f"       aria-label: '{aria_label}'")
            print(f"       role: '{role}'")
            print()

    # 2. 查找所有role="button"的div
    print("\n2️⃣  ALL <div role='button'> ELEMENTS:")
    div_buttons = page.query_selector_all('div[role="button"]')
    print(f"   Found {len(div_buttons)} div button elements\n")

    for i, btn in enumerate(div_buttons):
        if btn.is_visible():
            text = btn.inner_text().strip() if btn.inner_text() else ""
            aria_label = btn.get_attribute('aria-label') or ""
            print(f"   [{i}] Div Button:")
            print(f"       Text: '{text}'")
            print(f"       aria-label: '{aria_label}'")
            print()

    # 3. 查找所有a标签
    print("\n3️⃣  ALL <a> LINKS (might contain message link):")
    links = page.query_selector_all('a')
    print(f"   Found {len(links)} link elements\n")

    for i, link in enumerate(links):
        if link.is_visible():
            href = link.get_attribute('href') or ""
            text = link.inner_text().strip() if link.inner_text() else ""
            if 'direct' in href or 'message' in text.lower() or 'Message' in text:
                print(f"   [{i}] Link (possibly message-related):")
                print(f"       href: '{href}'")
                print(f"       Text: '{text}'")
                print()

    # 4. 检查是否已经关注
    print("\n4️⃣  FOLLOW STATUS:")
    following_indicators = [
        'button:has-text("Following")',
        'button:has-text("已关注")',
        'div:has-text("Following")',
    ]

    is_following = False
    for selector in following_indicators:
        try:
            elem = page.query_selector(selector)
            if elem:
                print(f"   ✅ Already following (found: {selector})")
                is_following = True
                break
        except:
            continue

    if not is_following:
        print("   ℹ️  Not following yet")

    # 5. 截图
    print("\n📸 Taking screenshot...")
    page.screenshot(path='instagram_profile_buttons.png', full_page=True)
    print("   Saved to: instagram_profile_buttons.png")

    print("\n" + "=" * 70)
    print("🎯 SUGGESTED SELECTORS:")
    print("=" * 70)
    print("\n   Look for buttons containing these keywords:")
    print("   - 'Message' / '发消息' / '訊息'")
    print("   - href containing '/direct/'")
    print("   - aria-label containing 'message'")
    print("\n   Check the screenshot and the output above!")
    print("=" * 70)

    input("\n\n👆 Review the output above, then press Enter to close...")
    browser.close()
