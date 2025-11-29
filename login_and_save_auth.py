#!/usr/bin/env python3
"""
一次性登录脚本 - 保存登录态到 auth.json
One-time login script - Save authentication state to auth.json

使用方法 / Usage:
1. 运行此脚本 / Run this script: python login_and_save_auth.py
2. 在打开的浏览器中手动登录 Twitter / Manually login to Twitter in the opened browser
3. 登录完成后按 Enter / Press Enter after login completes
4. 登录态将保存到 auth.json / Authentication state will be saved to auth.json
"""

from playwright.sync_api import sync_playwright
import os

def main():
    print("=" * 60)
    print("Twitter 登录态保存工具")
    print("Twitter Authentication State Saver")
    print("=" * 60)
    print()

    with sync_playwright() as p:
        # 启动浏览器（非无头模式，可以看到浏览器窗口）
        # Launch browser (non-headless mode so you can see the window)
        print("🚀 启动浏览器...")
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--no-sandbox'
            ]
        )

        # 创建新的浏览器上下文（模拟真实用户）
        # Create new browser context (simulate real user)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='zh-CN',
            timezone_id='Asia/Shanghai',
            permissions=['geolocation'],
            extra_http_headers={
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        )

        # 创建新页面
        # Create new page
        page = context.new_page()

        # 注入反检测脚本
        # Inject anti-detection script
        page.add_init_script("""
            // 移除 webdriver 属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            // 覆盖 plugins 和 languages
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en']
            });

            // 覆盖 chrome 属性
            window.chrome = {
                runtime: {}
            };

            // 覆盖 permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        # 访问 Twitter 登录页面
        # Go to Twitter login page
        print("📱 打开 Twitter 登录页面...")
        try:
            # 先访问主页，让浏览器看起来更真实
            page.goto("https://twitter.com", timeout=60000)
            import time
            time.sleep(2)

            # 然后跳转到登录页
            page.goto("https://twitter.com/i/flow/login", timeout=60000, wait_until='domcontentloaded')
        except Exception as e:
            print(f"⚠️  警告: {e}")
            print("尝试使用备用方法...")

        print()
        print("=" * 60)
        print("⏸️  请在打开的浏览器窗口中手动登录 Twitter")
        print("   Please manually login to Twitter in the opened browser")
        print()
        print("   登录完成后，请回到终端按 Enter 继续...")
        print("   After login completes, return to terminal and press Enter...")
        print("=" * 60)
        print()

        # 等待用户手动登录
        # Wait for user to manually login
        input("按 Enter 继续 / Press Enter to continue: ")

        # 保存登录态到文件
        # Save authentication state to file
        auth_file = "auth.json"
        context.storage_state(path=auth_file)

        print()
        print("=" * 60)
        print(f"✅ 登录状态已保存到 {auth_file}")
        print(f"   Authentication state saved to {auth_file}")
        print()
        print("现在你可以使用其他脚本自动登录，无需重复输入账号密码！")
        print("Now you can use other scripts to auto-login without re-entering credentials!")
        print("=" * 60)

        # 关闭浏览器
        # Close browser
        browser.close()

        # 验证文件是否创建成功
        # Verify file was created successfully
        if os.path.exists(auth_file):
            file_size = os.path.getsize(auth_file)
            print(f"\n📄 文件大小 / File size: {file_size} bytes")
            print(f"📍 文件位置 / File location: {os.path.abspath(auth_file)}")
        else:
            print("\n⚠️  警告：auth.json 文件未创建")
            print("   Warning: auth.json file was not created")

if __name__ == "__main__":
    main()
