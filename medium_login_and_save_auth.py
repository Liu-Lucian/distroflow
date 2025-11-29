#!/usr/bin/env python3
"""
Medium 登录并保存认证信息
手动登录后自动保存 cookies 到 medium_auth.json
"""

import sys
sys.path.insert(0, 'src')

from playwright.sync_api import sync_playwright
import json
import time

def save_medium_auth():
    """手动登录Medium并保存cookies"""
    print("🌐 启动浏览器...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720}
        )

        page = context.new_page()

        try:
            print("\n📍 步骤:")
            print("1. 浏览器将打开 Medium 首页")
            print("2. 请手动点击 Sign In 并完成登录")
            print("3. 登录成功后，会自动检测并保存")
            print("\n" + "="*60)

            # 访问 Medium
            print("\n🌐 正在访问 Medium...")
            page.goto("https://medium.com/", wait_until="domcontentloaded")
            time.sleep(3)

            print("\n⏳ 等待登录...")
            print("   请在浏览器中手动登录 Medium")
            print("   （使用 Google/Email/Twitter 任意方式）")

            # 等待登录完成的标志
            # Medium 登录后会有用户头像或 "Write" 按钮
            login_indicators = [
                'img[alt*="avatar"]',
                'button:has-text("Write")',
                'a[href*="/me/"]',
                'div[data-testid="headerAvatar"]'
            ]

            logged_in = False
            max_wait = 300  # 最多等待5分钟
            start_time = time.time()

            while not logged_in and (time.time() - start_time) < max_wait:
                for selector in login_indicators:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            logged_in = True
                            print("\n✅ 检测到登录成功！")
                            break
                    except:
                        pass

                if not logged_in:
                    time.sleep(2)

            if not logged_in:
                print("\n⚠️  超时未检测到登录，但仍会尝试保存 cookies")

            # 等待一下确保 cookies 完全设置
            time.sleep(3)

            # 获取 cookies
            print("\n🔑 提取 cookies...")
            cookies = context.cookies()

            if not cookies:
                print("❌ 未获取到任何 cookies，请确保已登录")
                input("\n按 Enter 关闭...")
                return False

            # 保存到文件
            auth_data = {
                "cookies": cookies,
                "saved_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }

            with open("medium_auth.json", "w") as f:
                json.dump(auth_data, f, indent=2)

            print(f"\n✅ 认证信息已保存!")
            print(f"   文件: medium_auth.json")
            print(f"   Cookies 数量: {len(cookies)}")

            # 验证关键 cookie
            important_cookies = ['uid', 'sid', '_aauser']
            found_cookies = [c['name'] for c in cookies if c['name'] in important_cookies]
            if found_cookies:
                print(f"   关键 cookies: {', '.join(found_cookies)}")

            print("\n" + "="*60)
            print("✅ 设置完成！现在可以运行自动发布脚本了")
            print("\n下一步:")
            print("  python3 medium_daily_auto_post.py")
            print("="*60)

            input("\n按 Enter 关闭浏览器...")
            return True

        except Exception as e:
            print(f"\n❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\n按 Enter 关闭...")
            return False
        finally:
            browser.close()

if __name__ == "__main__":
    save_medium_auth()
