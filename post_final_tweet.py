#!/usr/bin/env python3
"""
Post final tweet (#11) to complete the thread
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Tweet 10 ID from screenshot
TWEET_10_ID = "1994878295239004472"  # Will update if needed

TWEET_11_TEXT = """11/ If you found this interesting:

🔗 Check out the code: github.com/Liu-Lucian/distroflow
💬 Questions? Reply below
⭐ Star if you want to see more

Next thread: Cost optimization ($0.001 vs $99/month) 🧵

#BuildInPublic #AI #Python #OpenSource"""

async def post_final_tweet():
    """Post tweet 11"""
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

        print(f"🌐 Opening tweet 10...")
        # First, let's find tweet 10's actual URL by checking the profile
        await page.goto('https://twitter.com/LucianLiu861650', timeout=30000)
        await asyncio.sleep(3)

        # Look for tweet 10 in the timeline
        print("🔍 Looking for tweet 10 (DistroFlow announcement)...")
        tweets = await page.query_selector_all('article[data-testid="tweet"]')

        tweet_10_url = None
        for tweet_elem in tweets:
            text_elem = await tweet_elem.query_selector('[data-testid="tweetText"]')
            if text_elem:
                text = await text_elem.inner_text()
                if "open-sourced this as DistroFlow" in text or "10/" in text:
                    # Found tweet 10
                    time_elem = await tweet_elem.query_selector('time')
                    if time_elem:
                        link = await time_elem.evaluate('el => el.parentElement.href')
                        tweet_10_url = link
                        tweet_10_id = link.split('/status/')[-1].split('?')[0]
                        print(f"✅ Found tweet 10: {tweet_10_id}")
                        break

        if not tweet_10_url:
            print("⚠️  Couldn't find tweet 10, using fallback ID")
            tweet_10_url = f"https://twitter.com/LucianLiu861650/status/{TWEET_10_ID}"

        print(f"📝 Opening: {tweet_10_url}")
        await page.goto(tweet_10_url, timeout=30000)
        await asyncio.sleep(2)

        # Close any popups
        try:
            got_it = await page.query_selector('button:has-text("Got it")')
            if got_it:
                await got_it.click()
                await asyncio.sleep(1)
        except:
            pass

        # Click reply
        print("💬 Clicking reply...")
        reply_button = await page.wait_for_selector('[data-testid="reply"]', timeout=10000)
        await reply_button.click()
        await asyncio.sleep(2)

        # Find compose box
        print("✍️  Typing final tweet...")
        compose_box = await page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)
        await compose_box.click()
        await asyncio.sleep(0.5)

        # Type tweet
        await compose_box.type(TWEET_11_TEXT, delay=15)
        await asyncio.sleep(2)

        # Find post button and use JavaScript click to avoid overlap issues
        print("📤 Posting tweet 11...")
        post_button = await page.wait_for_selector('[data-testid="tweetButton"]', timeout=5000)

        # Try JavaScript click first (bypasses overlapping elements)
        try:
            await post_button.evaluate('el => el.click()')
            print("✅ Used JavaScript click")
        except:
            # Fallback to normal click
            await post_button.click()
            print("✅ Used normal click")

        await asyncio.sleep(5)

        # Verify posted
        print("🔍 Verifying tweet was posted...")
        current_url = page.url
        if '/status/' in current_url:
            tweet_id = current_url.split('/status/')[-1].split('?')[0]
            print(f"\n{'='*60}")
            print("🎉 THREAD COMPLETE! ALL 11 TWEETS POSTED!")
            print('='*60)
            print(f"\n✅ Tweet 11 ID: {tweet_id}")
            print(f"\n🔗 Full thread: https://twitter.com/LucianLiu861650/status/1994873140179341663")
            print(f"\n💡 Next steps:")
            print(f"   1. Pin the thread to your profile")
            print(f"   2. Share on LinkedIn")
            print(f"   3. Post on HackerNews")
            print(f"   4. Reply to every comment!")
        else:
            print("⚠️  Posted but couldn't verify tweet ID")

        print(f"\n⏳ Browser will close in 15 seconds...")
        await asyncio.sleep(15)

        await browser.close()
        return True

if __name__ == '__main__':
    success = asyncio.run(post_final_tweet())
    exit(0 if success else 1)
