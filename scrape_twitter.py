#!/usr/bin/env python3
"""
简单的Twitter粉丝爬虫脚本
Simple script to scrape Twitter followers
"""

import sys
import argparse
from src.twitter_scraper import TwitterWebScraper
import pandas as pd
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description='爬取Twitter粉丝并提取邮箱 / Scrape Twitter followers and extract emails',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 Examples:
  # 爬取某个用户的100个粉丝
  python scrape_twitter.py elonmusk --count 100

  # 爬取并显示浏览器窗口（调试用）
  python scrape_twitter.py elonmusk --count 50 --show-browser

  # 爬取并只提取有邮箱的粉丝
  python scrape_twitter.py elonmusk --count 200 --emails-only
        """
    )

    parser.add_argument(
        'username',
        help='要爬取粉丝的Twitter用户名 (Username to scrape followers from)'
    )

    parser.add_argument(
        '--count',
        type=int,
        default=100,
        help='要爬取的粉丝数量 (Number of followers to scrape, default: 100)'
    )

    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='显示浏览器窗口 (Show browser window for debugging)'
    )

    parser.add_argument(
        '--emails-only',
        action='store_true',
        help='只保存有邮箱的粉丝 (Only save followers with emails)'
    )

    parser.add_argument(
        '--output',
        default=None,
        help='输出文件名 (Output filename, default: auto-generated)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Twitter Follower Scraper / Twitter粉丝爬虫")
    print("=" * 60)
    print(f"Target: @{args.username}")
    print(f"Count: {args.count} followers")
    print("=" * 60)
    print()

    # 创建爬虫
    scraper = TwitterWebScraper(headless=not args.show_browser)

    try:
        # 爬取粉丝
        print("🔍 开始爬取粉丝... / Starting to scrape followers...")
        print()

        followers = scraper.get_followers(
            username=args.username,
            max_followers=args.count,
            extract_emails=True
        )

        if not followers:
            print("❌ 没有爬取到任何粉丝 / No followers scraped")
            return

        # 只保留有邮箱的（如果指定）
        if args.emails_only:
            original_count = len(followers)
            followers = [f for f in followers if f.get('email')]
            print(f"\n📧 筛选出有邮箱的粉丝: {len(followers)}/{original_count}")

        # 统计
        emails_found = sum(1 for f in followers if f.get('email'))

        print()
        print("=" * 60)
        print("结果 / Results")
        print("=" * 60)
        print(f"✓ 爬取粉丝数 / Followers scraped: {len(followers)}")
        print(f"✓ 找到邮箱数 / Emails found: {emails_found} ({emails_found/len(followers)*100:.1f}%)")
        print("=" * 60)
        print()

        # 显示前5个（带邮箱的）
        print("前几个结果 / Sample results:")
        print("-" * 60)

        sample = [f for f in followers if f.get('email')][:5]
        if not sample:
            sample = followers[:5]

        for i, follower in enumerate(sample, 1):
            print(f"\n{i}. @{follower['username']}")
            print(f"   姓名 Name: {follower['name']}")
            if follower.get('email'):
                print(f"   📧 邮箱 Email: {follower['email']}")
            if follower.get('bio'):
                bio_preview = follower['bio'][:80] + '...' if len(follower['bio']) > 80 else follower['bio']
                print(f"   简介 Bio: {bio_preview}")

        print()
        print("-" * 60)

        # 导出数据
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"exports/twitter_{args.username}_followers_{timestamp}.csv"
        else:
            output_file = args.output

        # 确保exports目录存在
        import os
        os.makedirs('exports', exist_ok=True)

        # 导出到CSV
        df = pd.DataFrame(followers)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        print()
        print(f"✓ 数据已导出 / Data exported to: {output_file}")
        print()

        # 显示Excel预览提示
        print("提示 / Tips:")
        print("• 使用Excel打开CSV文件查看完整数据")
        print("• Use Excel to open the CSV file for better viewing")
        print("• 邮箱可以直接用于邮件营销")
        print("• Emails can be used directly for email marketing")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断 / User interrupted")

    except Exception as e:
        print(f"\n❌ 错误 / Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        scraper.close()
        print("\n✓ 完成 / Done!")


if __name__ == "__main__":
    main()
