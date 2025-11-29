#!/usr/bin/env python3
"""
Hacker News 登录并保存认证信息
手动登录后自动提取 cookies
"""
from playwright.sync_api import sync_playwright
import json
import time

def login_and_save():
    print("=" * 80)
    print("🔐 Hacker News 登录和认证保存")
    print("=" * 80)
    print()
    print("步骤:")
    print("1. 浏览器将打开 Hacker News 登录页面")
    print("2. 请手动登录你的 HN 账号")
    print("3. 登录成功后，脚本会自动提取并保存 cookies")
    print()
    input("按 Enter 继续...")

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 打开 HN 登录页面
    print("\n🌐 打开 Hacker News 登录页面...")
    page.goto("https://news.ycombinator.com/login", wait_until="domcontentloaded")

    print("\n⏳ 请在浏览器中完成以下操作:")
    print("   1. 输入用户名和密码")
    print("   2. 点击 'login' 按钮")
    print("   3. 等待页面跳转到首页")
    print()
    print("   完成后回到终端...")

    # 等待用户手动登录
    input("\n✅ 登录完成后，按 Enter 继续保存 cookies...")

    # 提取 cookies
    print("\n📥 提取 cookies...")
    cookies = context.cookies()

    if not cookies:
        print("❌ 未找到 cookies，登录可能失败")
        browser.close()
        playwright.stop()
        return

    # 保存到文件
    auth_data = {
        'cookies': cookies,
        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open('hackernews_auth.json', 'w') as f:
        json.dump(auth_data, f, indent=2)

    print(f"   ✅ 已保存 {len(cookies)} 个 cookies")
    print(f"   📄 文件: hackernews_auth.json")

    # 验证登录状态
    print("\n🔍 验证登录状态...")
    page.goto("https://news.ycombinator.com", wait_until="domcontentloaded")
    time.sleep(2)

    user_link = page.query_selector('a[href^="user?id="]')
    if user_link:
        username = user_link.inner_text()
        print(f"   ✅ 登录验证成功！用户名: {username}")
    else:
        print("   ⚠️  无法验证登录状态（可能仍然有效）")

    print("\n" + "=" * 80)
    print("✅ 认证保存完成！")
    print("=" * 80)
    print("\n现在可以运行:")
    print("  python3 hackernews_auto_reply.py")
    print()

    time.sleep(3)
    browser.close()
    playwright.stop()


if __name__ == "__main__":
    login_and_save()
