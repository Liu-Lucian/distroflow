#!/usr/bin/env python3
"""
快速爬取脚本 - Playwright 版本（使用保存的登录态）
Quick scrape with Playwright (using saved authentication)

使用前请先运行一次：python login_and_save_auth.py
Before using, run once: python login_and_save_auth.py
"""

import sys
import os
from src.twitter_scraper_playwright import TwitterPlaywrightScraper
import pandas as pd

def main():
    if len(sys.argv) < 2:
        print("用法 / Usage: python quick_scrape_playwright.py <用户名> [数量]")
        print("示例 / Example: python quick_scrape_playwright.py elonmusk 50")
        print()
        print("⚠️  首次使用前请先运行：python login_and_save_auth.py")
        print("   Before first use, run: python login_and_save_auth.py")
        sys.exit(1)

    target_user = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 50

    # Check if auth.json exists
    if not os.path.exists("auth.json"):
        print("=" * 60)
        print("❌ 错误：找不到 auth.json 文件")
        print("   Error: auth.json file not found")
        print()
        print("请先运行以下命令保存登录状态：")
        print("Please run the following command to save login state first:")
        print()
        print("   python login_and_save_auth.py")
        print()
        print("只需要运行一次，之后就可以自动登录了！")
        print("You only need to run it once, then you can auto-login!")
        print("=" * 60)
        sys.exit(1)

    print("=" * 60)
    print("Twitter 快速爬虫 (Playwright + 保存的登录态)")
    print("Twitter Quick Scraper (Playwright + Saved Auth)")
    print("=" * 60)
    print(f"目标 / Target: @{target_user}")
    print(f"数量 / Count: {count} 粉丝 / followers")
    print("=" * 60)
    print()

    try:
        # Create scraper with saved authentication
        scraper = TwitterPlaywrightScraper(headless=False, auth_file="auth.json")
        scraper.start()

        print("🔍 开始爬取粉丝 / Starting to scrape followers...")
        print()

        followers = scraper.get_followers(
            username=target_user,
            max_followers=count,
            extract_emails=True
        )

        if followers:
            print()
            print("=" * 60)
            print(f"✓ 成功爬取 / Successfully scraped: {len(followers)} 个粉丝 / followers")
            print("=" * 60)

            # Statistics
            emails = [f for f in followers if f.get('email')]
            print(f"📧 找到邮箱 / Emails found: {len(emails)} ({len(emails)/len(followers)*100:.1f}%)")
            print()

            # Show sample followers with emails
            if emails:
                print("有邮箱的粉丝样例 / Sample followers with emails:")
                for i, f in enumerate(emails[:5], 1):
                    print(f"{i}. @{f['username']} - {f['email']}")
                print()

            # Export to CSV
            os.makedirs('exports', exist_ok=True)
            df = pd.DataFrame(followers)
            filename = f'exports/twitter_{target_user}_{count}_playwright.csv'
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✓ 数据已导出 / Data exported: {filename}")
            print()
            print("🎉 完成 / Done!")
        else:
            print("=" * 60)
            print("❌ 未获取到数据 / No data retrieved")
            print()
            print("可能的原因 / Possible reasons:")
            print("1. 登录状态已过期 / Login state expired")
            print("   解决 / Solution: 重新运行 / Re-run 'python login_and_save_auth.py'")
            print()
            print("2. 用户名不存在或账号被保护 / Username doesn't exist or account is protected")
            print("   解决 / Solution: 检查用户名拼写 / Check username spelling")
            print()
            print("3. Twitter 页面结构变化 / Twitter page structure changed")
            print("   解决 / Solution: 联系开发者更新代码 / Contact developer for code update")
            print("=" * 60)

    except FileNotFoundError as e:
        print(f"❌ 错误 / Error: {e}")
        print()
        print("请先运行 / Please run first:")
        print("   python login_and_save_auth.py")

    except KeyboardInterrupt:
        print("\n⚠️  用户中断 / User interrupted")

    except Exception as e:
        print(f"❌ 错误 / Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if 'scraper' in locals():
            scraper.close()


if __name__ == "__main__":
    main()
