#!/usr/bin/env python3
"""
测试多平台集成 - Test Multi-Platform Integration
测试LinkedIn和GitHub scrapers是否正常工作
"""

import sys
from pathlib import Path

# Add src directory to Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from src.linkedin_scraper import LinkedInScraper
from src.github_scraper import GitHubScraper


def test_linkedin():
    """测试LinkedIn scraper"""
    print("\n" + "="*70)
    print("🔵 Testing LinkedIn Scraper")
    print("="*70)

    try:
        scraper = LinkedInScraper(
            auth_file=str(SCRIPT_DIR / "linkedin_auth.json")
        )
        print("✅ LinkedIn scraper initialized")

        # 测试搜索
        keywords = ["recruiter", "hiring manager"]
        print(f"\n🔍 Searching for: {', '.join(keywords)} (limit: 3)")

        users = scraper.search_users(keywords, limit=3)
        print(f"✅ Found {len(users)} users")

        # 显示用户
        for i, user in enumerate(users, 1):
            print(f"\n  {i}. {user.get('name', 'N/A')}")
            print(f"     Profile: {user.get('profile_url', 'N/A')}")
            print(f"     Headline: {user.get('headline', 'N/A')}")
            print(f"     Location: {user.get('location', 'N/A')}")

        # 测试获取详细资料
        if users:
            print(f"\n📖 Getting detailed profile for first user...")
            profile = scraper.get_user_profile(users[0]['profile_url'])

            print(f"  Name: {profile.get('name', 'N/A')}")
            print(f"  Headline: {profile.get('headline', 'N/A')}")
            print(f"  Company: {profile.get('company', 'N/A')}")
            print(f"  Location: {profile.get('location', 'N/A')}")
            print(f"  Email: {profile.get('email', 'Not found')}")

        # 关闭浏览器
        scraper._close_browser()
        print("\n✅ LinkedIn test completed")

    except Exception as e:
        print(f"\n❌ LinkedIn test failed: {e}")
        import traceback
        traceback.print_exc()


def test_github():
    """测试GitHub scraper"""
    print("\n" + "="*70)
    print("🔵 Testing GitHub Scraper")
    print("="*70)

    try:
        scraper = GitHubScraper(
            auth_file=str(SCRIPT_DIR / "platforms_auth.json")
        )
        print("✅ GitHub scraper initialized")

        # 测试搜索
        keywords = ["recruiter", "hiring"]
        print(f"\n🔍 Searching for: {', '.join(keywords)} (limit: 3)")

        users = scraper.search_users(keywords, limit=3)
        print(f"✅ Found {len(users)} users")

        # 显示用户
        for i, user in enumerate(users, 1):
            print(f"\n  {i}. @{user.get('username', 'N/A')}")
            print(f"     Profile: {user.get('profile_url', 'N/A')}")

        # 测试获取详细资料
        if users:
            print(f"\n📖 Getting detailed profile for first user...")
            profile = scraper.get_user_profile(users[0]['username'])

            print(f"  Username: @{profile.get('username', 'N/A')}")
            print(f"  Name: {profile.get('name', 'N/A')}")
            print(f"  Bio: {profile.get('bio', 'N/A')[:100]}")
            print(f"  Company: {profile.get('company', 'N/A')}")
            print(f"  Location: {profile.get('location', 'N/A')}")
            print(f"  Email: {profile.get('email', 'Not public')}")
            print(f"  Followers: {profile.get('followers_count', 0)}")
            print(f"  Public repos: {profile.get('public_repos', 0)}")

        print("\n✅ GitHub test completed")

    except Exception as e:
        print(f"\n❌ GitHub test failed: {e}")
        import traceback
        traceback.print_exc()


def test_integration():
    """测试完整集成流程"""
    print("\n" + "="*70)
    print("🔵 Testing Full Integration")
    print("="*70)

    # 测试LinkedIn的完整流程
    print("\n1️⃣  Testing LinkedIn full flow (search + profile + email)...")
    try:
        scraper = LinkedInScraper(
            auth_file=str(SCRIPT_DIR / "linkedin_auth.json")
        )

        # 使用get_leads方法（继承自base class）
        leads = scraper.get_leads(keywords=["recruiter"], limit=2)

        print(f"   ✅ Got {len(leads)} leads")
        for lead in leads:
            print(f"   - {lead.get('name', 'N/A')}: {lead.get('email', 'No email')}")

        scraper._close_browser()

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # 测试GitHub的完整流程
    print("\n2️⃣  Testing GitHub full flow (search + profile + email)...")
    try:
        scraper = GitHubScraper(
            auth_file=str(SCRIPT_DIR / "platforms_auth.json")
        )

        # 使用get_leads方法
        leads = scraper.get_leads(keywords=["interview", "hiring"], limit=2)

        print(f"   ✅ Got {len(leads)} leads")
        for lead in leads:
            print(f"   - @{lead.get('username', 'N/A')}: {lead.get('email', 'No email')}")

    except Exception as e:
        print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("\n🧪 Multi-Platform Integration Test")
    print("="*70)

    # 选择测试
    import argparse
    parser = argparse.ArgumentParser(description='Test platform scrapers')
    parser.add_argument(
        '--platform',
        choices=['linkedin', 'github', 'all'],
        default='all',
        help='Which platform to test'
    )

    args = parser.parse_args()

    if args.platform in ['linkedin', 'all']:
        test_linkedin()

    if args.platform in ['github', 'all']:
        test_github()

    if args.platform == 'all':
        test_integration()

    print("\n" + "="*70)
    print("🎉 All tests completed!")
    print("="*70)
