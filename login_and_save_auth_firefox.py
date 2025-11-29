#!/usr/bin/env python3
"""
一次性登录脚本 - Firefox 版本（更容易绕过检测）
One-time login script - Firefox version (easier to bypass detection)

使用方法 / Usage:
1. 运行此脚本 / Run this script: python login_and_save_auth_firefox.py
2. 在打开的浏览器中手动登录 Twitter / Manually login to Twitter in the opened browser
3. 登录完成后按 Enter / Press Enter after login completes
4. 登录态将保存到 auth_firefox.json / Authentication state will be saved to auth_firefox.json
"""

from playwright.sync_api import sync_playwright
import os
import time

def main():
    print("=" * 60)
    print("Twitter 登录态保存工具 (Firefox 版)")
    print("Twitter Authentication State Saver (Firefox)")
    print("=" * 60)
    print()

    # 首先安装 Firefox
    print("📦 检查 Firefox 浏览器...")
    import subprocess
    try:
        subprocess.run(["python", "-m", "playwright", "install", "firefox"],
                      capture_output=True, check=False)
    except:
        pass

    with sync_playwright() as p:
        # 使用 Firefox（Twitter 对 Firefox 的检测更宽松）
        print("🚀 启动 Firefox 浏览器...")
        browser = p.firefox.launch(
            headless=False,
            firefox_user_prefs={
                'dom.webdriver.enabled': False,
                'useAutomationExtension': False,
                'general.useragent.override': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
            }
        )

        # 创建新的浏览器上下文
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            locale='zh-CN',
            timezone_id='Asia/Shanghai'
        )

        # 创建新页面
        page = context.new_page()

        # 访问 Twitter 主页
        print("📱 打开 Twitter...")
        try:
            page.goto("https://twitter.com", timeout=60000)
            time.sleep(3)

            # 点击登录按钮
            print("🔍 查找登录按钮...")
            try:
                # 尝试找到并点击登录按钮
                login_button = page.locator('a[href="/login"], a[data-testid="loginButton"]').first
                if login_button.is_visible():
                    login_button.click()
                    time.sleep(2)
                else:
                    # 如果找不到登录按钮，直接访问登录页
                    page.goto("https://twitter.com/i/flow/login", timeout=60000)
            except:
                # 备用方案：直接访问登录页
                page.goto("https://twitter.com/i/flow/login", timeout=60000)

            time.sleep(2)

        except Exception as e:
            print(f"⚠️  警告: {e}")
            print("请在打开的浏览器中手动访问 Twitter 并登录")

        print()
        print("=" * 60)
        print("⏸️  请在打开的浏览器窗口中手动登录 Twitter")
        print("   Please manually login to Twitter in the opened browser")
        print()
        print("   提示：如果看到安全警告，请尝试：")
        print("   Tip: If you see security warning, try:")
        print("   1. 等待几秒后重试 / Wait a few seconds and retry")
        print("   2. 使用邮箱而不是用户名登录 / Use email instead of username")
        print("   3. 如果有验证码，完成验证 / Complete verification if any")
        print()
        print("   登录完成后，请回到终端按 Enter 继续...")
        print("   After login completes, return to terminal and press Enter...")
        print("=" * 60)
        print()

        # 等待用户手动登录
        input("按 Enter 继续 / Press Enter to continue: ")

        # 保存登录态到文件
        auth_file = "auth_firefox.json"
        context.storage_state(path=auth_file)

        print()
        print("=" * 60)
        print(f"✅ 登录状态已保存到 {auth_file}")
        print(f"   Authentication state saved to {auth_file}")
        print()
        print("现在你可以使用 Firefox 版本的爬虫脚本了！")
        print("Now you can use the Firefox version scraper!")
        print("=" * 60)

        # 关闭浏览器
        browser.close()

        # 验证文件是否创建成功
        if os.path.exists(auth_file):
            file_size = os.path.getsize(auth_file)
            print(f"\n📄 文件大小 / File size: {file_size} bytes")
            print(f"📍 文件位置 / File location: {os.path.abspath(auth_file)}")
            print()
            print("🎉 成功！现在运行爬虫：")
            print("   python quick_scrape_playwright.py elonmusk 50")
        else:
            print("\n⚠️  警告：auth_firefox.json 文件未创建")
            print("   Warning: auth_firefox.json file was not created")

if __name__ == "__main__":
    main()
