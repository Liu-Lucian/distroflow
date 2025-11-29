#!/usr/bin/env python3
"""
Twitter发布测试脚本
"""

import sys
import os
import json
import logging

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from twitter_poster import TwitterPoster

logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 80)
    print("🐦 Twitter发布测试")
    print("=" * 80)

    # 读取已转换的内容
    content_file = "seo_data/social_media_posts/ai-tools-job-seekers_social.json"

    print(f"\n📄 读取内容: {content_file}")

    with open(content_file, 'r', encoding='utf-8') as f:
        all_content = json.load(f)

    twitter_content = all_content['twitter']

    print(f"\n📊 Twitter Thread信息:")
    print(f"   格式: {twitter_content.get('format')}")
    print(f"   Tweets数量: {twitter_content.get('total_tweets')}")
    print(f"\n预览第一条Tweet:")
    print(f"   {twitter_content['tweets'][0][:100]}...")

    # 创建poster
    poster = TwitterPoster()

    try:
        print("\n🌐 初始化浏览器...")
        poster.setup_browser(headless=False)

        print("\n🔐 验证登录状态...")
        if poster.verify_login():
            print("   ✅ 登录验证成功")

            print("\n📤 开始发布Twitter Thread...")
            success = poster.create_post(twitter_content)

            if success:
                print("\n" + "=" * 80)
                print("✅ Twitter发布成功！")
                print("=" * 80)
            else:
                print("\n" + "=" * 80)
                print("❌ Twitter发布失败")
                print("=" * 80)
        else:
            print("\n❌ 登录验证失败")
            print("💡 请检查 auth.json 文件")
            print("   或运行: python3 twitter_login_and_save_auth.py")

    finally:
        print("\n⏸️  浏览器将保持打开30秒，请检查结果...")
        import time
        time.sleep(30)

        print("\n🔒 关闭浏览器...")
        poster.close_browser()

        print("\n✅ 测试完成")

if __name__ == "__main__":
    main()
