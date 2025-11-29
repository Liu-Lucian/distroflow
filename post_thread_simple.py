#!/usr/bin/env python3
"""
Simple Twitter Thread Poster - Use saved cookies directly
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

async def post_thread(thread_file):
    """Post entire thread"""
    # Load thread
    print(f"📖 Loading thread from: {thread_file}")
    with open(thread_file) as f:
        thread_data = json.load(f)

    tweets = thread_data['tweets']
    print(f"   Found {len(tweets)} tweets in thread")
    print(f"   Title: {thread_data.get('thread_title', 'Untitled')}\n")

    # Load authentication
    auth_file = Path.home() / '.distroflow/twitter_auth.json'
    if not auth_file.exists():
        print("❌ No authentication found!")
        print(f"   Run: python3 quick_twitter_login.py")
        return False

    with open(auth_file) as f:
        auth_data = json.load(f)

    async with async_playwright() as p:
        # Launch browser
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(
            headless=False,
            args=['--start-maximized', '--disable-blink-features=AutomationControlled']
        )

        context = await browser.new_context(
            viewport={'width': 1400, 'height': 900},
            user_agent=auth_data.get('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        )

        # Add cookies
        await context.add_cookies(auth_data['cookies'])
        print(f"✅ Loaded {len(auth_data['cookies'])} cookies")

        page = await context.new_page()

        # Go to Twitter
        print("🌐 Going to Twitter...\n")
        await page.goto('https://twitter.com/home', timeout=60000)
        await asyncio.sleep(3)

        # Verify logged in
        try:
            await page.wait_for_selector('[data-testid="SideNav_AccountSwitcher_Button"]', timeout=5000)
            print("✅ Logged in successfully!\n")
        except:
            print("⚠️  Could not verify login, but continuing...\n")

        # Post each tweet
        print("=" * 60)
        print("📝 POSTING THREAD")
        print("=" * 60 + "\n")

        previous_tweet_id = None

        for i, tweet in enumerate(tweets, 1):
            print(f"\n🐦 Tweet {i}/{len(tweets)}")
            print("-" * 60)
            print(f"Text: {tweet['text'][:80]}...")

            try:
                if previous_tweet_id:
                    # Reply to previous tweet
                    tweet_url = f"https://twitter.com/i/status/{previous_tweet_id}"
                    print(f"   Opening: {tweet_url}")
                    await page.goto(tweet_url, timeout=30000)
                    await asyncio.sleep(2)

                    # Click reply
                    reply_button = await page.query_selector('[data-testid="reply"]')
                    if reply_button:
                        await reply_button.click()
                        await asyncio.sleep(1)
                else:
                    # First tweet - use compose box on home
                    if i > 1:  # Go back to home if not first tweet
                        await page.goto('https://twitter.com/home', timeout=30000)
                        await asyncio.sleep(2)

                # Find compose box
                compose_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
                await compose_box.click()
                await asyncio.sleep(0.5)

                # Type tweet
                print(f"   ✍️  Typing...")
                await compose_box.type(tweet['text'], delay=20)
                await asyncio.sleep(1)

                # Click post button
                print(f"   📤 Posting...")
                post_button = await page.query_selector('[data-testid="tweetButtonInline"]')
                if not post_button:
                    post_button = await page.query_selector('[data-testid="tweetButton"]')

                if post_button:
                    await post_button.click()
                    await asyncio.sleep(3)

                    # Get tweet ID from URL
                    current_url = page.url
                    if '/status/' in current_url:
                        tweet_id = current_url.split('/status/')[-1].split('?')[0]
                        previous_tweet_id = tweet_id
                        print(f"   ✅ Posted! ID: {tweet_id}")
                    else:
                        print(f"   ⚠️  Posted but couldn't get ID")
                        previous_tweet_id = "unknown"

                    # Wait before next tweet
                    if i < len(tweets):
                        wait_time = 5
                        print(f"   ⏳ Waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"   ❌ Error: {e}")
                print(f"   Continuing...")

        print("\n" + "=" * 60)
        print("🎉 THREAD COMPLETE!")
        print("=" * 60)

        if previous_tweet_id and previous_tweet_id != "unknown":
            print(f"\n🔗 Thread URL: https://twitter.com/LucianLiu861650/status/{previous_tweet_id}")

        print("\n⏳ Browser will close in 10 seconds...")
        await asyncio.sleep(10)

        await browser.close()
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 post_thread_simple.py <thread_file.json>")
        sys.exit(1)

    thread_file = sys.argv[1]
    if not Path(thread_file).exists():
        print(f"❌ Thread file not found: {thread_file}")
        sys.exit(1)

    success = asyncio.run(post_thread(thread_file))
    sys.exit(0 if success else 1)
