#!/usr/bin/env python3
"""
Twitter/X保存Cookies - 简单直接
你登录后，按回车，我保存cookies
"""

import json
from playwright.sync_api import sync_playwright
import time

def save_cookies():
    """保存Twitter cookies"""
    print("=" * 60)
    print("🔐 Twitter/X - Save Cookies (Simple)")
    print("=" * 60)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    )
    page = context.new_page()

    print("\n📱 Opening Twitter/X...")
    page.goto('https://twitter.com/login')

    print("\n" + "=" * 60)
    print("👉 LOGIN MANUALLY:")
    print("   1. Login in the browser")
    print("   2. When you're logged in and see the homepage")
    print("   3. Come back here and press ENTER")
    print("=" * 60)

    # 等待用户按回车
    input("\n⏸️  Press ENTER when you're logged in: ")

    print("\n💾 Saving cookies...")

    # 获取所有cookies
    cookies = context.cookies()

    # 保存到文件
    cookies_dict = {}
    for cookie in cookies:
        cookies_dict[cookie['name']] = cookie['value']

    # 保存简单格式
    with open('twitter_cookies.json', 'w') as f:
        json.dump(cookies_dict, f, indent=2)

    print(f"✅ Saved {len(cookies)} cookies to twitter_cookies.json")

    # 也更新platforms_auth.json
    try:
        with open('platforms_auth.json', 'r') as f:
            platforms_auth = json.load(f)
    except:
        platforms_auth = {}

    platforms_auth['twitter'] = {
        'cookies': cookies_dict
    }

    with open('platforms_auth.json', 'w') as f:
        json.dump(platforms_auth, f, indent=2)

    print("✅ Updated platforms_auth.json")

    # 也保存完整的storage_state
    storage_state = context.storage_state()
    with open('twitter_auth.json', 'w') as f:
        json.dump(storage_state, f, indent=2)

    print("✅ Saved storage_state to twitter_auth.json")

    print("\n" + "=" * 60)
    print("✅ ALL DONE!")
    print("=" * 60)
    print("\nNow you can use Twitter DM sender!")

    browser.close()
    playwright.stop()


if __name__ == "__main__":
    try:
        save_cookies()
    except KeyboardInterrupt:
        print("\n❌ Cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
