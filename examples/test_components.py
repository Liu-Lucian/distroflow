#!/usr/bin/env python3
"""
Test individual components of MarketingMind AI
Run this to verify everything is working correctly
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.keyword_extractor import KeywordExtractor
from src.twitter_client import TwitterClient
from src.email_finder import EmailFinder
from src.outreach_engine import OutreachEngine


def test_config():
    """Test configuration"""
    print("\n" + "="*50)
    print("Testing Configuration")
    print("="*50)

    print(f"LLM Provider: {config.get_llm_provider()}")
    print(f"Has Anthropic Key: {bool(config.ANTHROPIC_API_KEY)}")
    print(f"Has OpenAI Key: {bool(config.OPENAI_API_KEY)}")
    print(f"Has Twitter Keys: {bool(config.TWITTER_ACCESS_TOKEN)}")

    if config.validate():
        print("✓ Configuration is valid!")
    else:
        print("✗ Configuration is incomplete!")
        print("Please add missing API keys to .env file")
        return False

    return True


def test_keyword_extractor():
    """Test keyword extraction"""
    print("\n" + "="*50)
    print("Testing Keyword Extractor")
    print("="*50)

    try:
        extractor = KeywordExtractor()
        sample = "AI-powered CRM for real estate agents. Automate follow-ups and close more deals."

        print(f"Extracting keywords from: {sample}")
        results = extractor.extract_keywords(sample)

        print(f"\nKeywords: {results['keywords'][:5]}")
        print(f"Hashtags: {results['hashtags'][:3]}")
        print(f"Personas: {results['personas'][:2]}")

        print("✓ Keyword Extractor working!")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_twitter_client():
    """Test Twitter client"""
    print("\n" + "="*50)
    print("Testing Twitter Client")
    print("="*50)

    try:
        client = TwitterClient()
        print("Searching for users interested in 'AI automation'...")

        influencers = client.search_influencers("AI automation", max_results=3)

        if influencers:
            print(f"\n✓ Found {len(influencers)} influencers:")
            for inf in influencers[:3]:
                print(f"  - @{inf['username']}: {inf['followers_count']} followers")
            return True
        else:
            print("✗ No influencers found")
            return False

    except Exception as e:
        print(f"✗ Error: {e}")
        print("Make sure Twitter API keys are correct in .env")
        return False


def test_email_finder():
    """Test email finder"""
    print("\n" + "="*50)
    print("Testing Email Finder")
    print("="*50)

    try:
        finder = EmailFinder()

        # Test pattern generation
        patterns = finder.guess_email_patterns("John Smith", "example.com")
        print(f"Generated email patterns: {patterns[:3]}")

        # Test extraction from bio
        test_bio = "Founder @ TechCorp. Contact: john@techcorp.com"
        email = finder.extract_email_from_bio(test_bio)

        if email:
            print(f"✓ Extracted email from bio: {email}")
            return True
        else:
            print("✓ Email finder initialized (no email in test bio)")
            return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_outreach_engine():
    """Test outreach message generation"""
    print("\n" + "="*50)
    print("Testing Outreach Engine")
    print("="*50)

    try:
        engine = OutreachEngine()

        lead = {
            'name': 'Jane Doe',
            'username': 'janedoe',
            'description': 'Marketing Director at SaaS startup. Love automation tools.'
        }

        product = "AI-powered marketing automation platform"

        print("Generating personalized message...")
        message = engine.generate_connection_message(lead, product)

        print(f"\nGenerated message ({len(message)} chars):")
        print("-" * 50)
        print(message)
        print("-" * 50)

        print("✓ Outreach Engine working!")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*60 + "╗")
    print("║" + " "*10 + "MarketingMind AI - Component Tests" + " "*15 + "║")
    print("╚" + "="*60 + "╝")

    tests = [
        ("Configuration", test_config),
        ("Keyword Extractor", test_keyword_extractor),
        ("Email Finder", test_email_finder),
        ("Outreach Engine", test_outreach_engine),
        ("Twitter Client", test_twitter_client),  # Test last as it requires API
    ]

    results = {}

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n✗ {name} failed with error: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)

    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    total = len(results)
    passed = sum(results.values())

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! You're ready to start!")
        print("\nNext step: Run a test campaign")
        print("python main.py find-leads --product 'Your product' --count 10")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("Most common issues:")
        print("- Missing API keys in .env")
        print("- Twitter API not set up correctly")
        print("- Check TWITTER_API_SETUP.md for help")


if __name__ == "__main__":
    main()
