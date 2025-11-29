#!/usr/bin/env python3
"""
Twitter单条推文测试 - 简化版
"""

import sys
import os
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from twitter_poster import TwitterPoster

logging.basicConfig(level=logging.INFO)

def main():
    print("=" * 80)
    print("🐦 Twitter单条推文测试")
    print("=" * 80)

    # 简单的单条tweet内容
    simple_content = {
        'tweets': [
            '''🚀 Testing AI-powered job interview prep!

HireMeAI helps job seekers ace their interviews with:
✅ Personalized practice questions
✅ Real-time feedback
✅ Industry-specific scenarios

Try it at HireMeAI.app

#AI #JobSearch #InterviewPrep #CareerTips'''
        ],
        'total_tweets': 1
    }

    print(f"\n📝 推文内容:")
    print(f"   {simple_content['tweets'][0][:100]}...")
    print(f"   ({len(simple_content['tweets'][0])} 字符)")

    poster = TwitterPoster()

    try:
        print("\n🌐 初始化浏览器...")
        poster.setup_browser(headless=False)

        print("\n🔐 验证登录状态...")
        if poster.verify_login():
            print("   ✅ 登录成功")

            print("\n📤 发布单条推文...")
            success = poster.create_post(simple_content)

            if success:
                print("\n" + "=" * 80)
                print("✅ 推文发布成功！")
                print("=" * 80)
                return True
            else:
                print("\n" + "=" * 80)
                print("❌ 推文发布失败")
                print("=" * 80)
                return False
        else:
            print("\n❌ 登录失败")
            return False

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("\n⏸️  浏览器保持打开60秒，请检查...")
        import time
        time.sleep(60)

        print("\n🔒 关闭浏览器...")
        poster.close_browser()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
