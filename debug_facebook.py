#!/usr/bin/env python3
"""
Facebook Debug Script - 诊断问题
"""

import sys
sys.path.append('src')

import json
import time
from playwright.sync_api import sync_playwright

print("=" * 70)
print("🔍 Facebook Debug Script")
print("=" * 70)

# Step 1: 检查auth文件
print("\n[1/4] Checking auth file...")
try:
    with open('platforms_auth.json', 'r') as f:
        config = json.load(f)

    fb_config = config.get('facebook', {})
    cookies = fb_config.get('cookies', {})

    if not cookies:
        print("   ❌ No Facebook cookies found!")
        print("   Run: python3 facebook_login_and_save_auth.py")
        sys.exit(1)

    print(f"   ✅ Found {len(cookies)} cookies")

    # 检查关键cookies
    key_cookies = ['c_user', 'xs', 'datr']
    for key in key_cookies:
        if key in cookies:
            print(f"   ✅ {key}: present")
        else:
            print(f"   ⚠️  {key}: missing")

except FileNotFoundError:
    print("   ❌ platforms_auth.json not found!")
    print("   Run: python3 facebook_login_and_save_auth.py")
    sys.exit(1)

# Step 2: 测试浏览器启动
print("\n[2/4] Testing browser launch...")
try:
    playwright = sync_playwright().start()

    # 使用更好的反检测设置
    browser = playwright.chromium.launch(
        headless=False,  # 显示浏览器方便调试
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-setuid-sandbox',
        ]
    )

    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        locale='en-US',
        timezone_id='America/Los_Angeles',
    )

    # 隐藏webdriver特征
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    # 加载cookies
    if cookies:
        cookies_list = [
            {
                'name': name,
                'value': value,
                'domain': '.facebook.com',
                'path': '/'
            }
            for name, value in cookies.items()
        ]
        context.add_cookies(cookies_list)
        print(f"   ✅ Loaded {len(cookies_list)} cookies")

    page = context.new_page()
    print("   ✅ Browser launched successfully")

except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Step 3: 测试Facebook登录状态
print("\n[3/4] Testing Facebook login...")
try:
    print("   Visiting facebook.com...")
    page.goto('https://www.facebook.com', wait_until='domcontentloaded', timeout=30000)
    time.sleep(3)

    print(f"   Current URL: {page.url}")

    # 检查是否登录
    if 'login' in page.url.lower():
        print("   ❌ Not logged in - redirected to login page")
        print("   Please run: python3 facebook_login_and_save_auth.py")
    else:
        print("   ✅ Logged in successfully!")

        # 尝试获取用户名
        try:
            # Facebook用户名通常在这些位置
            name_selectors = [
                'span[dir="auto"]',
                'div[aria-label*="Your profile"]',
            ]

            for selector in name_selectors:
                elem = page.query_selector(selector)
                if elem:
                    text = elem.inner_text()
                    if text:
                        print(f"   👤 Logged in as: {text}")
                        break
        except:
            pass

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Step 4: 测试搜索功能
print("\n[4/4] Testing search functionality...")
try:
    test_keyword = "job"
    search_url = f"https://www.facebook.com/search/posts?q={test_keyword}"

    print(f"   Searching for: '{test_keyword}'")
    print(f"   URL: {search_url}")

    # 使用domcontentloaded而不是load，避免crash
    page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
    time.sleep(5)

    print(f"   Current URL: {page.url}")

    # 检查页面内容
    page_text = page.content()[:500]
    print(f"   Page loaded: {len(page.content())} chars")

    # 尝试查找帖子
    post_selectors = [
        'div[role="article"]',
        'a[href*="/posts/"]',
        'a[href*="/permalink/"]',
    ]

    for selector in post_selectors:
        elements = page.query_selector_all(selector)
        print(f"   Selector '{selector}': {len(elements)} elements")

except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("🔍 Debug completed!")
print("=" * 70)

print("\n💡 Please check the browser window for any issues")
print("   Press Ctrl+C to close...")

try:
    time.sleep(60)
except KeyboardInterrupt:
    pass

# 清理
try:
    browser.close()
    playwright.stop()
except:
    pass
