#!/usr/bin/env python3
"""
测试所有平台集成
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR / "src"))

from src.github_scraper import GitHubScraper
from src.hackernews_scraper import HackerNewsScraper
from src.producthunt_scraper import ProductHuntScraper

print("\n" + "="*70)
print("🧪 MULTI-PLATFORM TEST")
print("="*70)

# Test GitHub
print("\n1️⃣  Testing GitHub...")
try:
    github = GitHubScraper(auth_file=str(SCRIPT_DIR / "platforms_auth.json"))
    users = github.search_users(["developer", "software engineer"], limit=3)
    print(f"   ✅ Found {len(users)} GitHub users")
    if users:
        print(f"   Example: @{users[0].get('username', 'N/A')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Hacker News
print("\n2️⃣  Testing Hacker News...")
try:
    hn = HackerNewsScraper()
    users = hn.search_users(["startup", "founder"], limit=3)
    print(f"   ✅ Found {len(users)} Hacker News users")
    if users:
        print(f"   Example: {users[0].get('username', 'N/A')} (karma: {users[0].get('karma', 0)})")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test Product Hunt
print("\n3️⃣  Testing Product Hunt...")
try:
    ph = ProductHuntScraper(auth_file=str(SCRIPT_DIR / "platforms_auth.json"))
    users = ph.search_users(["maker", "startup"], limit=3)
    print(f"   ✅ Found {len(users)} Product Hunt users")
    if users:
        print(f"   Example: @{users[0].get('username', 'N/A')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("🎉 All platform tests completed!")
print("="*70)
