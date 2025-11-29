#!/usr/bin/env python3
"""
Twitter/X 登录并保存认证状态
使用Playwright保存storage_state用于后续自动化
"""

import json
from playwright.sync_api import sync_playwright
import time

def login_and_save():
    """登录Twitter并保存认证状态"""
    print("=" * 60)
    print("🔐 Twitter/X Login - Save Authentication")
    print("=" * 60)

    playwright = sync_playwright().start()

    # 使用Chromium
    browser = playwright.chromium.launch(
        headless=False,  # 显示浏览器，方便你登录
        args=['--disable-blink-features=AutomationControlled']
    )

    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 720}
    )

    # 添加反检测脚本
    page = context.new_page()
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
    """)

    print("\n📱 Opening Twitter/X login page...")
    page.goto('https://twitter.com/i/flow/login', wait_until='domcontentloaded')

    print("\n" + "=" * 60)
    print("👉 Please login manually in the browser window")
    print("   1. Enter your username/email and password")
    print("   2. Complete any 2FA if required")
    print("   3. Wait until you see the Twitter/X homepage")
    print("=" * 60)

    # 等待用户登录
    print("\n⏳ Waiting for you to login...")
    print("   (When you see the Twitter/X homepage, just wait a few seconds...)")

    # 等待登录完成（检测是否到达主页）
    for i in range(120):  # 最多等待2分钟
        try:
            # 检查是否已登录（看是否能找到主页的元素）
            if 'home' in page.url.lower() or page.locator('[data-testid="SideNav_AccountSwitcher_Button"]').count() > 0:
                print("\n✅ Login detected!")
                time.sleep(3)  # 多等几秒让页面稳定
                break
        except:
            pass

        time.sleep(1)
        if i % 10 == 0 and i > 0:
            print(f"   Still waiting... ({i}s elapsed)")

    # 保存认证状态
    print("\n💾 Saving authentication state...")
    storage_state = context.storage_state()

    with open('twitter_auth.json', 'w') as f:
        json.dump(storage_state, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ Authentication saved to 'twitter_auth.json'")
    print("=" * 60)

    print("\n📝 You can now use this file for automated campaigns:")
    print("   python3 run_twitter_campaign.py")

    # 关闭浏览器
    time.sleep(2)
    browser.close()
    playwright.stop()

if __name__ == "__main__":
    login_and_save()
