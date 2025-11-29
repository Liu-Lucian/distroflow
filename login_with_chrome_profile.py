#!/usr/bin/env python3
"""
使用你自己的 Chrome 配置登录 Twitter
Use your own Chrome profile to login to Twitter

这个方法使用你日常使用的 Chrome 浏览器配置（包含已保存的登录信息）
This method uses your daily Chrome browser profile (with saved login info)

优点：
- 不会被 Twitter 检测为自动化工具
- 使用你已经登录的账号
- 不需要重复输入密码
"""

from playwright.sync_api import sync_playwright
import os
import time
import subprocess

def get_chrome_user_data_dir():
    """获取 Chrome 用户数据目录"""
    # macOS 默认路径
    mac_path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    if os.path.exists(mac_path):
        return mac_path

    # 如果找不到，提示用户
    print("⚠️  未找到 Chrome 用户数据目录")
    print("请输入你的 Chrome 用户数据目录路径：")
    custom_path = input("路径: ").strip()
    return custom_path if os.path.exists(custom_path) else None

def main():
    print("=" * 60)
    print("使用 Chrome 配置保存 Twitter 登录态")
    print("Save Twitter Auth Using Chrome Profile")
    print("=" * 60)
    print()

    # 重要提示
    print("⚠️  重要提示 / Important Notes:")
    print("1. 请确保 Chrome 已经关闭 / Make sure Chrome is closed")
    print("2. 如果 Chrome 正在运行，请先关闭 / Close Chrome if it's running")
    print()

    input("确认 Chrome 已关闭后按 Enter / Press Enter after closing Chrome: ")

    # 获取 Chrome 用户数据目录
    user_data_dir = get_chrome_user_data_dir()

    if not user_data_dir:
        print("❌ 无法找到 Chrome 用户数据目录")
        return

    print(f"✓ 找到 Chrome 配置: {user_data_dir}")
    print()

    with sync_playwright() as p:
        print("🚀 启动 Chrome（使用你的配置）...")

        try:
            # 使用用户的 Chrome 配置启动
            context = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                channel="chrome",  # 使用系统安装的 Chrome
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-first-run',
                    '--no-default-browser-check'
                ],
                viewport={'width': 1920, 'height': 1080}
            )

            page = context.pages[0] if context.pages else context.new_page()

            print("📱 打开 Twitter...")
            page.goto("https://twitter.com/home", timeout=60000)

            time.sleep(3)

            # 检查是否已登录
            print("🔍 检查登录状态...")

            if "login" in page.url.lower() or "i/flow" in page.url.lower():
                print()
                print("=" * 60)
                print("⚠️  检测到未登录状态")
                print("   Not logged in detected")
                print()
                print("请在打开的浏览器中登录 Twitter")
                print("Please login to Twitter in the opened browser")
                print()
                print("登录完成后按 Enter 继续...")
                print("Press Enter after login completes...")
                print("=" * 60)
                input()
            else:
                print("✓ 检测到已登录状态！")
                print()
                print("如果你想使用其他账号，请在浏览器中切换账号")
                print("然后按 Enter 继续...")
                print()
                input("按 Enter 保存登录态 / Press Enter to save auth: ")

            # 保存登录态
            auth_file = "auth.json"
            context.storage_state(path=auth_file)

            print()
            print("=" * 60)
            print(f"✅ 登录状态已保存到 {auth_file}")
            print()
            print("🎉 完成！现在你可以运行爬虫了：")
            print("   python quick_scrape_playwright.py elonmusk 50")
            print("=" * 60)

            # 关闭浏览器
            context.close()

            # 验证文件
            if os.path.exists(auth_file):
                file_size = os.path.getsize(auth_file)
                print(f"\n📄 文件大小: {file_size} bytes")
                print(f"📍 文件位置: {os.path.abspath(auth_file)}")

        except Exception as e:
            print(f"\n❌ 错误: {e}")
            print()
            print("可能的原因：")
            print("1. Chrome 仍在运行 - 请关闭 Chrome 后重试")
            print("2. 权限问题 - 请确保有访问 Chrome 配置的权限")
            print()
            print("请尝试其他方法：")
            print("   python login_and_save_auth_firefox.py")

if __name__ == "__main__":
    main()
