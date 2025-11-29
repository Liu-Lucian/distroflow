#!/usr/bin/env python3
"""快速测试爬虫 / Quick test scraper"""

from src.twitter_scraper import TwitterWebScraper
import pandas as pd

print("="*60)
print("Twitter Web Scraper - Quick Test")
print("="*60)
print()

# 创建爬虫（显示浏览器）
print("1. 初始化爬虫...")
scraper = TwitterWebScraper(headless=False)  # 显示浏览器

try:
    # 爬取少量粉丝测试
    print("2. 爬取 @elonmusk 的前10个粉丝...")
    print()
    
    followers = scraper.get_followers(
        username="elonmusk",
        max_followers=10,
        extract_emails=True
    )
    
    print()
    print("="*60)
    print(f"✓ 成功爬取 {len(followers)} 个粉丝")
    print("="*60)
    print()
    
    # 显示结果
    for i, f in enumerate(followers, 1):
        print(f"{i}. @{f['username']}")
        print(f"   姓名: {f['name']}")
        if f.get('email'):
            print(f"   📧 邮箱: {f['email']}")
        print(f"   简介: {f['bio'][:60]}...")
        print()
    
    # 统计
    if followers:
        emails = [f for f in followers if f.get('email')]
        print(f"邮箱提取率: {len(emails)}/{len(followers)} ({len(emails)/len(followers)*100:.1f}%)")
    else:
        print("⚠️  没有爬取到粉丝数据")
        print("\n可能的原因:")
        print("1. Twitter页面结构已更新")
        print("2. 需要登录才能访问")
        print("3. 网络连接问题")
        print("\n建议:")
        print("• 检查浏览器窗口是否正常打开")
        print("• 尝试手动访问 https://twitter.com/elonmusk/followers")
        print("• 如果需要登录，请更新代码添加登录功能")
    print()
    
    # 导出
    if followers:
        df = pd.DataFrame(followers)
        df.to_csv('test_followers.csv', index=False, encoding='utf-8-sig')
        print("✓ 数据已导出到: test_followers.csv")
        print()
        print("测试成功！🎉")
    else:
        print("❌ 测试未能获取数据，请查看上方的建议")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    scraper.close()
    print("\n完成！")
