#!/usr/bin/env python3
"""
LinkedIn Login and Save Authentication
LinkedIn登录并保存认证状态

这个脚本会打开浏览器让你手动登录LinkedIn，然后保存整个session状态
"""

import json
from playwright.sync_api import sync_playwright
import time

def login_and_save():
    """手动登录LinkedIn并保存认证状态"""
    print("\n" + "="*70)
    print("🔵 LinkedIn Authentication Setup")
    print("="*70)
    print("\n这个工具会：")
    print("1. 打开LinkedIn登录页面")
    print("2. 让你手动登录")
    print("3. 保存你的登录状态到 linkedin_auth.json")
    print("\n⚠️  重要：登录后不要关闭浏览器，等待程序自动保存！")
    print("\n按 Enter 继续...")
    input()

    with sync_playwright() as p:
        print("\n🚀 启动浏览器...")

        # 启动浏览器（可见模式）
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-automation',
                '--no-sandbox'
            ]
        )

        # 创建context
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 创建page
        page = context.new_page()

        # 注入反检测脚本
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            window.chrome = {
                runtime: {}
            };
        """)

        print("✅ 浏览器已启动")
        print("\n🌐 正在打开LinkedIn登录页面...")

        # 打开LinkedIn
        page.goto("https://www.linkedin.com/login")

        print("\n" + "="*70)
        print("👉 请在浏览器中完成以下步骤：")
        print("="*70)
        print("1. 输入你的LinkedIn邮箱和密码")
        print("2. 点击'登录'")
        print("3. 如果有两步验证，完成验证")
        print("4. 等待进入LinkedIn主页")
        print("5. 看到主页后，回到这里按 Enter")
        print("="*70)

        # 等待用户完成登录
        input("\n✅ 登录完成后，按 Enter 继续...")

        # 检查是否真的登录了
        current_url = page.url
        print(f"\n当前URL: {current_url}")

        if "feed" in current_url or "mynetwork" in current_url or current_url == "https://www.linkedin.com/":
            print("✅ 看起来已经登录成功！")
        else:
            print("⚠️  可能还没有完全登录，但我们继续尝试保存...")

        # 保存认证状态
        print("\n💾 正在保存认证状态...")

        try:
            # 保存整个storage state
            storage_state = context.storage_state()

            # 保存到文件
            with open('linkedin_auth.json', 'w') as f:
                json.dump(storage_state, f, indent=2)

            print("✅ 认证状态已保存到: linkedin_auth.json")

            # 显示一些统计
            cookies_count = len(storage_state.get('cookies', []))
            print(f"📊 保存了 {cookies_count} 个cookies")

            # 测试一下
            print("\n🧪 测试认证是否有效...")
            page.goto("https://www.linkedin.com/feed/", timeout=30000)
            time.sleep(2)

            if "feed" in page.url or "mynetwork" in page.url:
                print("✅ 认证测试成功！")
                print("\n🎉 设置完成！你现在可以使用LinkedIn scraper了")
                print("\n运行以下命令测试：")
                print("  python3 test_platforms.py --platform linkedin")
            else:
                print("⚠️  认证可能有问题，请重新运行此脚本")

        except Exception as e:
            print(f"❌ 保存失败: {e}")
            print("请重新运行此脚本")

        print("\n按 Enter 关闭浏览器...")
        input()

        browser.close()

        print("\n" + "="*70)
        print("✅ 完成！")
        print("="*70)


if __name__ == "__main__":
    try:
        login_and_save()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
