#!/usr/bin/env python3
"""
TikTok登录并保存认证信息
用法：运行脚本，手动登录TikTok，脚本会自动保存sessionid
"""

import json
import time
from playwright.sync_api import sync_playwright

print("=" * 70)
print("🎵 TikTok Login & Save Authentication")
print("=" * 70)

print("\n📝 Instructions:")
print("   1. A browser will open")
print("   2. Log in to TikTok manually")
print("   3. Once logged in, wait 5 seconds")
print("   4. Script will automatically save your sessionid")
print("\n")

with sync_playwright() as p:
    # 打开浏览器（非无头模式，可以看到界面）
    browser = p.chromium.launch(
        headless=False,
        slow_mo=500
    )

    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )

    page = context.new_page()

    print("🌐 Opening TikTok login page...")
    page.goto('https://www.tiktok.com/login', timeout=30000)

    print("\n⏳ Waiting for you to log in...")
    print("   (Please log in manually in the browser)")
    print("   (Script will continue after you're logged in)\n")

    # 等待用户登录（检测URL变化或主页元素）
    logged_in = False
    for i in range(60):  # 最多等待5分钟
        try:
            # 检查是否已经登录（URL不再是登录页面）
            current_url = page.url
            if '/login' not in current_url:
                print(f"✅ Detected login! Current URL: {current_url}")
                logged_in = True
                break

            # 或者检查是否有用户头像元素
            avatar = page.query_selector('[data-e2e="nav-user-avatar"]')
            if avatar:
                print("✅ Detected user avatar!")
                logged_in = True
                break

        except:
            pass

        time.sleep(5)
        if (i + 1) % 6 == 0:  # 每30秒提示一次
            print(f"   Still waiting... ({(i + 1) * 5} seconds elapsed)")

    if not logged_in:
        print("\n⚠️  Timeout waiting for login")
        print("   Please make sure you complete the login process")
        browser.close()
        exit(1)

    print("\n⏳ Waiting 5 more seconds for cookies to settle...")
    time.sleep(5)

    # 获取cookies
    cookies = context.cookies()

    # 查找sessionid
    sessionid = None
    for cookie in cookies:
        if cookie['name'] == 'sessionid':
            sessionid = cookie['value']
            break

    if not sessionid:
        print("\n❌ Could not find sessionid cookie")
        print("   Available cookies:")
        for cookie in cookies:
            print(f"      - {cookie['name']}")
        print("\n💡 Tips:")
        print("   1. Make sure you're fully logged in")
        print("   2. Try refreshing the page after login")
        print("   3. Check if TikTok requires additional verification")
        browser.close()
        exit(1)

    print(f"\n✅ Found sessionid!")
    print(f"   Length: {len(sessionid)} characters")
    print(f"   Preview: {sessionid[:20]}...")

    # 加载现有配置
    try:
        with open('platforms_auth.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}

    # 更新TikTok配置
    if 'tiktok' not in config:
        config['tiktok'] = {}

    config['tiktok']['sessionid'] = sessionid

    # 保存配置
    with open('platforms_auth.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("\n✅ Saved to platforms_auth.json!")
    print("\n📝 Updated config:")
    print(f"   tiktok.sessionid: {sessionid[:20]}...{sessionid[-10:]}")

    print("\n🎯 Next steps:")
    print("   1. Run: ./start_tiktok_campaign.sh")
    print("   2. The system will use your new login session")

    print("\n⏸  Keeping browser open for 10 seconds...")
    print("   (You can close it manually or wait)\n")
    time.sleep(10)

    browser.close()

print("\n✅ Done!")
