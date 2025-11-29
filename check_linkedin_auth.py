#!/usr/bin/env python3
"""
检查LinkedIn认证状态
Check LinkedIn Authentication Status
"""

import sys
import json
from pathlib import Path

# Add src directory to Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from playwright.sync_api import sync_playwright


def check_linkedin_cookies():
    """检查LinkedIn cookies是否有效"""
    print("\n" + "="*70)
    print("🔍 Checking LinkedIn Authentication")
    print("="*70)

    # 读取cookies
    auth_file = SCRIPT_DIR / "platforms_auth.json"
    if not auth_file.exists():
        print("❌ platforms_auth.json not found!")
        return False

    with open(auth_file, 'r') as f:
        config = json.load(f)

    linkedin_config = config.get('linkedin', {})
    cookies = linkedin_config.get('cookies', {})
    headers = linkedin_config.get('headers', {})

    print("\n📋 Current cookies found:")
    print(f"  li_at: {cookies.get('li_at', 'MISSING')[:20]}...")
    print(f"  JSESSIONID: {cookies.get('JSESSIONID', 'MISSING')[:30]}...")
    print(f"  liap: {cookies.get('liap', 'MISSING')}")

    # 测试cookies
    print("\n🧪 Testing cookies with browser...")

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)

    try:
        context = browser.new_context(
            user_agent=headers.get('User-Agent'),
            viewport={'width': 1920, 'height': 1080}
        )

        # 设置cookies
        context.add_cookies([
            {
                'name': 'li_at',
                'value': cookies['li_at'],
                'domain': '.linkedin.com',
                'path': '/'
            },
            {
                'name': 'JSESSIONID',
                'value': cookies['JSESSIONID'],
                'domain': '.www.linkedin.com',
                'path': '/'
            },
            {
                'name': 'liap',
                'value': cookies['liap'],
                'domain': '.linkedin.com',
                'path': '/'
            }
        ])

        page = context.new_page()

        # 访问LinkedIn主页
        print("  Navigating to LinkedIn...")
        page.goto("https://www.linkedin.com", timeout=60000)
        page.wait_for_timeout(3000)

        # 检查是否成功登录
        current_url = page.url
        print(f"  Current URL: {current_url}")

        if "login" in current_url or "authwall" in current_url:
            print("\n❌ Authentication FAILED - Cookies are expired or invalid")
            print("\n📝 To get new cookies:")
            print("1. Login to LinkedIn in your browser")
            print("2. Press F12 to open Developer Tools")
            print("3. Go to: Application → Cookies → linkedin.com")
            print("4. Copy these values:")
            print("   - li_at")
            print("   - JSESSIONID")
            print("   - liap")
            print("5. Update platforms_auth.json")
            print("\n⏸️  Browser will stay open for 30 seconds so you can check...")
            page.wait_for_timeout(30000)
            browser.close()
            playwright.stop()
            return False
        else:
            print("\n✅ Authentication SUCCESS - Cookies are valid!")
            print(f"✅ Logged in as: {current_url}")

            # 测试搜索功能
            print("\n🔍 Testing search functionality...")
            search_url = "https://www.linkedin.com/search/results/people/?keywords=recruiter"
            page.goto(search_url, timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)

            if "search" in page.url:
                print("✅ Search functionality works!")
            else:
                print("⚠️  Search might be restricted")

            print("\n⏸️  Browser will stay open for 10 seconds...")
            page.wait_for_timeout(10000)
            browser.close()
            playwright.stop()
            return True

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        browser.close()
        playwright.stop()
        return False


if __name__ == "__main__":
    print("🔐 LinkedIn Authentication Checker")

    success = check_linkedin_cookies()

    print("\n" + "="*70)
    if success:
        print("✅ All checks passed - LinkedIn integration is ready!")
        print("\nYou can now run:")
        print("  python3 continuous_campaign.py --product hiremeai --platform linkedin")
    else:
        print("❌ LinkedIn authentication failed - please update cookies")
        print("\nSee instructions above to get new cookies")
    print("="*70 + "\n")

    sys.exit(0 if success else 1)
