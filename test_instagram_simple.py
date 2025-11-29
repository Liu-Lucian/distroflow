#!/usr/bin/env python3
"""
测试简化版Instagram campaign（参照Twitter/Reddit模式）
只运行1个关键词，1-3个用户
"""

import sys
sys.path.append('src')

from run_instagram_campaign_simple import InstagramUserCollector, log

print("=" * 70)
print("🧪 Testing Instagram Simple Campaign")
print("=" * 70)

# 测试关键词
test_keyword = "jobsearch"

log(f"📱 Test keyword: #{test_keyword}")
log("")

# 创建收集器
collector = InstagramUserCollector()

try:
    # 搜索用户（只要3个用于测试）
    log("🔍 Searching users...")
    users = collector.search_users(test_keyword, limit=3)

    if not users:
        print("\n❌ No users found!")
    else:
        print(f"\n✅ Found {len(users)} users:")
        print()
        for i, user in enumerate(users, 1):
            print(f"{i}. @{user['username']}")
            print(f"   Profile: {user['profile_url']}")
            print()

        print("=" * 70)
        print("✅ Test Successful!")
        print("=" * 70)
        print("\nTo run full campaign:")
        print("  python3 run_instagram_campaign_simple.py")
        print()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    collector.cleanup()
