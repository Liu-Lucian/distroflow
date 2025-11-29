#!/usr/bin/env python3
"""
Reddit登录并保存认证信息
手动登录后自动提取cookies
"""
from playwright.sync_api import sync_playwright
import json
import time

def save_reddit_auth():
    print("=" * 80)
    print("🔐 Reddit 登录并保存认证")
    print("=" * 80)
    print("\n步骤:")
    print("1. 将打开Reddit登录页面")
    print("2. 请手动登录")
    print("3. 登录成功后，程序自动保存cookies")
    print("4. 按Enter继续...")
    input()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720}
        )
        page = context.new_page()

        print("\n🌐 打开Reddit登录页面...")
        page.goto("https://www.reddit.com/login", wait_until="domcontentloaded")

        print("\n⏳ 请在浏览器中登录...")
        print("   登录完成后，按Enter继续...")
        input()

        # 获取cookies
        cookies = context.cookies()

        # 保存认证信息
        auth_data = {
            "cookies": cookies,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        with open('reddit_auth.json', 'w') as f:
            json.dump(auth_data, f, indent=2)

        print("\n✅ 认证信息已保存到 reddit_auth.json")
        print(f"   共保存 {len(cookies)} 个cookies")

        browser.close()

if __name__ == "__main__":
    save_reddit_auth()
