#!/usr/bin/env python3
"""
测试LinkedIn搜索功能
"""

import sys
sys.path.append('src')

from linkedin_scraper import LinkedInScraper

print("=" * 70)
print("🔍 LinkedIn Search Test")
print("=" * 70)

# 测试关键词
test_keywords = ["hiring manager", "recruiter", "job interview"]

print(f"\n📝 搜索关键词: {', '.join(test_keywords)}")
print(f"🎯 目标: 找到5个用户\n")

scraper = LinkedInScraper("linkedin_auth.json")

try:
    users = scraper.search_users(test_keywords, limit=5)

    print(f"\n" + "=" * 70)
    print(f"📊 搜索结果: 找到 {len(users)} 个用户")
    print("=" * 70)

    if users:
        for i, user in enumerate(users, 1):
            print(f"\n[{i}] {user.get('name')}")
            print(f"    职位: {user.get('headline', 'N/A')}")
            print(f"    地点: {user.get('location', 'N/A')}")
            print(f"    主页: {user.get('profile_url', 'N/A')[:80]}...")
    else:
        print("\n⚠️  未找到用户")
        print("\n💡 可能的原因:")
        print("   1. LinkedIn登录已过期 → 运行: python3 linkedin_login_and_save_auth.py")
        print("   2. 搜索选择器需要更新（LinkedIn经常改DOM结构）")
        print("   3. LinkedIn检测到自动化行为")
        print("\n📁 调试文件:")
        print("   - linkedin_search_debug.png (截图)")
        print("   - linkedin_search_debug.html (HTML)")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    scraper._close_browser()

print("\n✅ 测试完成")
