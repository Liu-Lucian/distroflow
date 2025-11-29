#!/usr/bin/env python3
"""
Continue Twitter Thread - Post remaining tweets as replies
"""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Last posted tweet ID (tweet #7)
LAST_TWEET_ID = "1994878295239004472"
FIRST_TWEET_ID = "1994873140179341663"  # Keep for reference

async def continue_thread(thread_file):
    """Post remaining tweets in thread"""
    # Load thread
    print(f"📖 Loading thread from: {thread_file}")
    with open(thread_file) as f:
        thread_data = json.load(f)

    tweets = thread_data['tweets'][7:]  # Skip first 7 tweets (already posted)
    print(f"   Found {len(tweets)} remaining tweets to post")
    print(f"   Starting from tweet #8\n")

    # Load authentication
    auth_file = Path.home() / '.distroflow/twitter_auth.json'
    if not auth_file.exists():
        print("❌ No authentication found!")
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
        page = await context.new_page()

        # Close any popups that might appear
        print("🔧 Checking for popups...")
        try:
            # Wait a moment for page to load
            await asyncio.sleep(2)

            # Look for "Got it" or close buttons
            got_it = await page.query_selector('button:has-text("Got it")')
            if got_it:
                await got_it.click()
                print("   Closed popup")
                await asyncio.sleep(1)
        except:
            pass

        print("=" * 60)
        print("📝 POSTING REMAINING TWEETS")
        print("=" * 60 + "\n")

        previous_tweet_id = LAST_TWEET_ID

        for i, tweet in enumerate(tweets, 8):  # Start from 8
            print(f"\n🐦 Tweet {i}/11")
            print("-" * 60)
            print(f"Text: {tweet['text'][:80]}...")

            try:
                # Go to previous tweet to reply
                tweet_url = f"https://twitter.com/LucianLiu861650/status/{previous_tweet_id}"
                print(f"   Opening: {tweet_url}")
                await page.goto(tweet_url, timeout=30000)
                await asyncio.sleep(2)

                # Close any popups first
                try:
                    got_it = await page.query_selector('button:has-text("Got it")')
                    if got_it:
                        await got_it.click()
                        await asyncio.sleep(1)
                except:
                    pass

                # Click reply button
                print("   Clicking reply...")
                reply_button = await page.wait_for_selector('[data-testid="reply"]', timeout=10000)
                await reply_button.click()
                await asyncio.sleep(2)

                # Find compose box
                compose_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
                await compose_box.click()
                await asyncio.sleep(0.5)

                # Type tweet
                print(f"   ✍️  Typing...")
                await compose_box.type(tweet['text'], delay=15)
                await asyncio.sleep(1)

                # Click reply button
                print(f"   📤 Posting reply...")
                post_button = await page.wait_for_selector('[data-testid="tweetButton"]', timeout=5000)
                await post_button.click()
                await asyncio.sleep(4)

                # Get new tweet ID from URL
                await page.wait_for_load_state('networkidle', timeout=10000)
                current_url = page.url

                if '/status/' in current_url:
                    # Extract the newest tweet ID (should be the reply we just posted)
                    # Look for our reply in the thread
                    await asyncio.sleep(2)

                    # Try to find the tweet we just posted by looking for the text
                    tweets_on_page = await page.query_selector_all('article[data-testid="tweet"]')

                    new_tweet_id = None
                    for tweet_elem in tweets_on_page:
                        tweet_text_elem = await tweet_elem.query_selector('[data-testid="tweetText"]')
                        if tweet_text_elem:
                            text_content = await tweet_text_elem.inner_text()
                            # Check if this is our tweet (first 50 chars match)
                            if text_content[:50] == tweet['text'][:50]:
                                # Found our tweet, get its ID from the link
                                time_elem = await tweet_elem.query_selector('time')
                                if time_elem:
                                    link = await time_elem.evaluate('el => el.parentElement.href')
                                    if '/status/' in link:
                                        new_tweet_id = link.split('/status/')[-1].split('?')[0]
                                        break

                    if new_tweet_id:
                        previous_tweet_id = new_tweet_id
                        print(f"   ✅ Posted! ID: {new_tweet_id}")
                    else:
                        print(f"   ⚠️  Posted but couldn't get ID, using fallback method")
                        # Fallback: wait a bit and try current URL
                        await asyncio.sleep(2)
                        current_url = page.url
                        if '/status/' in current_url:
                            new_id = current_url.split('/status/')[-1].split('?')[0]
                            if new_id != previous_tweet_id:
                                previous_tweet_id = new_id
                                print(f"   ✅ Got ID from URL: {new_id}")

                # Wait before next tweet
                if i < 11:
                    wait_time = 5
                    print(f"   ⏳ Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                print(f"   ❌ Error: {e}")
                print(f"   Continuing anyway...")
                await asyncio.sleep(3)

        print("\n" + "=" * 60)
        print("🎉 THREAD COMPLETE!")
        print("=" * 60)
        print(f"\n🔗 Thread URL: https://twitter.com/LucianLiu861650/status/{FIRST_TWEET_ID}")
        print("\n💡 Next steps:")
        print("   1. Pin the thread to your profile")
        print("   2. Share on LinkedIn")
        print("   3. Reply to every comment!")

        print("\n⏳ Browser will close in 15 seconds...")
        await asyncio.sleep(15)

        await browser.close()
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 continue_thread.py <thread_file.json>")
        sys.exit(1)

    thread_file = sys.argv[1]
    success = asyncio.run(continue_thread(thread_file))
    sys.exit(0 if success else 1)
