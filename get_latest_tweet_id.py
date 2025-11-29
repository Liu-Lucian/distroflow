#!/usr/bin/env python3
"""
Get the latest tweet ID from user's profile
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import json

async def get_latest_tweet():
    # Load auth
    auth_file = Path.home() / '.distroflow/twitter_auth.json'
    with open(auth_file) as f:
        auth_data = json.load(f)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        await context.add_cookies(auth_data['cookies'])
        page = await context.new_page()

        # Go to first tweet to see the thread
        print("Going to thread...")
        await page.goto('https://twitter.com/LucianLiu861650/status/1994873140179341663', timeout=30000)
        await asyncio.sleep(3)

        # Get all tweets in thread
        tweets = await page.query_selector_all('article[data-testid="tweet"]')
        print(f"\nFound {len(tweets)} tweets in thread:")

        for i, tweet in enumerate(tweets, 1):
            time_elem = await tweet.query_selector('time')
            if time_elem:
                link = await time_elem.evaluate('el => el.parentElement.href')
                tweet_id = link.split('/status/')[-1].split('?')[0]

                # Get tweet text
                text_elem = await tweet.query_selector('[data-testid="tweetText"]')
                text = ""
                if text_elem:
                    text = await text_elem.inner_text()
                    text = text[:50] + "..." if len(text) > 50 else text

                print(f"{i}. ID: {tweet_id}")
                print(f"   Text: {text}")

        if len(tweets) > 0:
            # Get last tweet ID
            last_tweet = tweets[-1]
            time_elem = await last_tweet.query_selector('time')
            if time_elem:
                link = await time_elem.evaluate('el => el.parentElement.href')
                last_id = link.split('/status/')[-1].split('?')[0]
                print(f"\n✅ Last tweet ID (continue from here): {last_id}")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(get_latest_tweet())
