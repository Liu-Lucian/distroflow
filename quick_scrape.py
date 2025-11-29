#!/usr/bin/env python3
"""
快速爬取脚本 - 自动登录版本
Quick scrape with auto-login
"""

import sys
from src.twitter_scraper import TwitterWebScraper
import pandas as pd

if len(sys.argv) < 2:
    print("用法: python quick_scrape.py <用户名> [数量]")
    print("示例: python quick_scrape.py elonmusk 50")
    sys.exit(1)

target_user = sys.argv[1]
count = int(sys.argv[2]) if len(sys.argv) > 2 else 50

print("=" * 60)
print("Twitter 快速爬虫 (自动登录)")
print("=" * 60)
print(f"目标: @{target_user}")
print(f"数量: {count} 粉丝")
print("=" * 60)
print()

# 创建爬虫（自动登录）
scraper = TwitterWebScraper(headless=False, auto_login=True)

try:
    print("🔍 开始爬取粉丝...")
    followers = scraper.get_followers(
        username=target_user,
        max_followers=count,
        extract_emails=True
    )
    
    if followers:
        print()
        print("=" * 60)
        print(f"✓ 成功爬取 {len(followers)} 个粉丝")
        print("=" * 60)
        
        # 统计邮箱
        emails = [f for f in followers if f.get('email')]
        print(f"📧 找到邮箱: {len(emails)} ({len(emails)/len(followers)*100:.1f}%)")
        print()
        
        # 显示前几个有邮箱的
        if emails:
            print("有邮箱的粉丝样例:")
            for i, f in enumerate(emails[:5], 1):
                print(f"{i}. @{f['username']} - {f['email']}")
            print()
        
        # 导出
        df = pd.DataFrame(followers)
        filename = f'exports/twitter_{target_user}_{count}.csv'
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✓ 数据已导出: {filename}")
        print()
        print("🎉 完成!")
    else:
        print("❌ 未获取到数据")

except KeyboardInterrupt:
    print("\n⚠️  用户中断")
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    scraper.close()
