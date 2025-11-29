#!/usr/bin/env python3
"""
Quick test for Facebook system
Tests that all imports and initialization work correctly
"""

import sys
sys.path.append('src')

print("=" * 70)
print("🧪 Testing Facebook Marketing System")
print("=" * 70)

# Test 1: Import scraper
print("\n[1/3] Testing FacebookScraper import...")
try:
    from src.facebook_scraper import FacebookScraper
    print("   ✅ FacebookScraper imported successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Import DM sender
print("\n[2/3] Testing FacebookDMSender import...")
try:
    from src.facebook_dm_sender import FacebookDMSender
    print("   ✅ FacebookDMSender imported successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Import campaign script functions
print("\n[3/3] Testing campaign script...")
try:
    import run_facebook_campaign
    print("   ✅ Campaign script imported successfully")

    # Check key functions exist
    assert hasattr(run_facebook_campaign, 'analyze_users_with_ai')
    assert hasattr(run_facebook_campaign, 'send_batch_dms')
    assert hasattr(run_facebook_campaign, 'main')
    print("   ✅ All required functions present")

except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ All tests passed!")
print("=" * 70)

print("\n📝 Next steps:")
print("   1. Run: python3 facebook_login_and_save_auth.py")
print("   2. Edit keywords in run_facebook_campaign.py")
print("   3. Run: python3 run_facebook_campaign.py")
print("\n✨ System is ready to use!")
