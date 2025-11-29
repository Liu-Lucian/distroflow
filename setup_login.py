#!/usr/bin/env python3
"""
Twitter 登录设置 - 交互式选择
Twitter Login Setup - Interactive Selection
"""

import os
import subprocess
import sys

def print_banner():
    print("\n" + "=" * 60)
    print("🔐 Twitter 登录设置向导")
    print("   Twitter Login Setup Wizard")
    print("=" * 60)

def print_methods():
    print("\n请选择登录方法 / Please select login method:\n")

    print("1. 使用 Chrome 配置 (推荐！)")
    print("   Use Chrome Profile (Recommended!)")
    print("   ✅ 最不容易被检测 / Least likely to be detected")
    print("   ✅ 使用已保存的登录 / Uses saved login")
    print("   ⚠️  需要关闭 Chrome / Requires Chrome to be closed")
    print()

    print("2. 使用 Firefox")
    print("   Use Firefox")
    print("   ✅ Twitter 检测宽松 / Twitter is lenient")
    print("   ✅ 独立浏览器 / Independent browser")
    print("   ⚠️  需要下载 Firefox / Requires Firefox download")
    print()

    print("3. 使用 Chromium (原方案)")
    print("   Use Chromium (Original)")
    print("   ✅ 已安装 / Already installed")
    print("   ⚠️  可能被检测 / May be detected")
    print()

    print("4. 查看详细说明")
    print("   View detailed guide")
    print()

    print("5. 退出")
    print("   Exit")
    print()

def run_chrome_profile():
    print("\n" + "=" * 60)
    print("方法 1: 使用 Chrome 配置")
    print("=" * 60)
    print()
    print("⚠️  重要：请先关闭所有 Chrome 窗口！")
    print("   Important: Please close all Chrome windows first!")
    print()
    print("macOS: 按 Cmd+Q 完全退出 Chrome")
    print("或运行: killall 'Google Chrome'")
    print()

    confirm = input("Chrome 已关闭？按 Enter 继续，或输入 'n' 取消: ").strip().lower()
    if confirm == 'n':
        return

    print("\n启动 Chrome 配置登录...")
    subprocess.run([sys.executable, "login_with_chrome_profile.py"])

def run_firefox():
    print("\n" + "=" * 60)
    print("方法 2: 使用 Firefox")
    print("=" * 60)
    print()
    print("首次使用会自动下载 Firefox（约 50-100MB）")
    print("First use will download Firefox (about 50-100MB)")
    print()

    confirm = input("继续？按 Enter 继续，或输入 'n' 取消: ").strip().lower()
    if confirm == 'n':
        return

    print("\n启动 Firefox 登录...")
    subprocess.run([sys.executable, "login_and_save_auth_firefox.py"])

def run_chromium():
    print("\n" + "=" * 60)
    print("方法 3: 使用 Chromium")
    print("=" * 60)
    print()
    print("注意：可能会看到'不安全浏览器'警告")
    print("Note: You may see 'unsafe browser' warning")
    print()
    print("如果遇到问题，建议使用方法 1 或 2")
    print("If you encounter issues, try method 1 or 2")
    print()

    confirm = input("继续？按 Enter 继续，或输入 'n' 取消: ").strip().lower()
    if confirm == 'n':
        return

    print("\n启动 Chromium 登录...")
    subprocess.run([sys.executable, "login_and_save_auth.py"])

def show_guide():
    print("\n" + "=" * 60)
    print("查看详细说明")
    print("=" * 60)
    print()

    if os.path.exists("LOGIN_METHODS_CN.md"):
        with open("LOGIN_METHODS_CN.md", 'r', encoding='utf-8') as f:
            content = f.read()
            # 只显示前 50 行
            lines = content.split('\n')[:50]
            print('\n'.join(lines))
            print("\n... (更多内容请查看 LOGIN_METHODS_CN.md)")
    else:
        print("未找到 LOGIN_METHODS_CN.md 文件")

    print()
    input("按 Enter 返回 / Press Enter to return")

def check_auth_file():
    """检查是否已有登录文件"""
    if os.path.exists("auth.json"):
        file_size = os.path.getsize("auth.json")
        print("\n" + "✅" * 20)
        print("✅ 检测到已保存的登录状态！")
        print("   Found saved authentication state!")
        print(f"   文件: auth.json ({file_size} bytes)")
        print()
        print("你可以直接开始爬取：")
        print("You can start scraping directly:")
        print()
        print("   python quick_scrape_playwright.py elonmusk 50")
        print()
        print("如果登录已过期，重新运行此脚本保存新的登录状态")
        print("If login expired, re-run this script to save new auth")
        print("✅" * 20 + "\n")

def main():
    print_banner()
    check_auth_file()

    while True:
        print_methods()

        choice = input("请选择 (1-5) / Select (1-5): ").strip()

        if choice == '1':
            run_chrome_profile()
        elif choice == '2':
            run_firefox()
        elif choice == '3':
            run_chromium()
        elif choice == '4':
            show_guide()
        elif choice == '5':
            print("\n再见！Goodbye!")
            break
        else:
            print("\n❌ 无效选择，请输入 1-5")
            print("   Invalid choice, please enter 1-5")

        if choice in ['1', '2', '3']:
            # 检查是否成功创建了 auth 文件
            print("\n" + "=" * 60)
            if os.path.exists("auth.json") or os.path.exists("auth_firefox.json"):
                print("✅ 登录设置完成！")
                print("   Login setup completed!")
                print()
                print("现在你可以开始爬取了：")
                print("Now you can start scraping:")
                print()
                print("   python quick_scrape_playwright.py elonmusk 50")
                print("=" * 60)
                break
            else:
                print("⚠️  未检测到 auth 文件")
                print("   Auth file not detected")
                print()
                retry = input("是否重试？(y/n) / Retry? (y/n): ").strip().lower()
                if retry != 'y':
                    break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断 / User interrupted")
        sys.exit(0)
