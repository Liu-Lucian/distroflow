#!/usr/bin/env python3
"""
Quick Twitter Login & Cookie Saver
Opens browser, lets you login, saves cookies automatically
"""
import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

async def save_twitter_auth():
    """Open browser, login to Twitter, save cookies"""
    print("🔐 Twitter Authentication Setup")
    print("=" * 50)
    print("\nThis will:")
    print("1. Open a browser window")
    print("2. Navigate to Twitter login")
    print("3. Wait for you to login manually")
    print("4. Save cookies automatically")
    print("\nStarting browser...")

    async with async_playwright() as p:
        # Use persistent context to save login session
        user_data_dir = Path.home() / '.distroflow/twitter_browser'
        user_data_dir.mkdir(parents=True, exist_ok=True)

        # Launch with persistent context (saves login)
        context = await p.chromium.launch_persistent_context(
            str(user_data_dir),
            headless=False,
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            args=['--disable-blink-features=AutomationControlled']
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Go to Twitter
        print("\n📱 Opening Twitter...")
        await page.goto('https://twitter.com/login')

        print("\n✋ Please login to Twitter manually in the browser window")
        print("   (I'll wait 60 seconds for you to login...)")

        # Wait 60 seconds for user to login
        import asyncio
        await asyncio.sleep(60)

        # Get current URL to verify login
        current_url = page.url
        if 'twitter.com/home' in current_url or 'x.com/home' in current_url:
            print("\n✅ Login detected!")
        else:
            print(f"\n⚠️  Current URL: {current_url}")
            print("   If you're logged in, that's fine. Continuing...")

        # Save cookies
        cookies = await context.cookies()

        # Create auth directory
        auth_dir = Path.home() / '.distroflow'
        auth_dir.mkdir(exist_ok=True)

        # Save cookies
        auth_file = auth_dir / 'twitter_auth.json'
        auth_data = {
            'cookies': cookies,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        with open(auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)

        print(f"\n✅ Cookies saved to: {auth_file}")
        print(f"   Saved {len(cookies)} cookies")

        # Verify important cookies
        cookie_names = [c['name'] for c in cookies]
        important = ['auth_token', 'ct0']
        found_important = [name for name in important if name in cookie_names]

        if found_important:
            print(f"   Found important cookies: {', '.join(found_important)}")
        else:
            print("   ⚠️  Warning: Didn't find expected cookies (auth_token, ct0)")
            print("   This might still work, or you may need to login again")

        await context.close()

        print("\n🎉 Setup complete!")
        print("   You can now use: distroflow launch --platform twitter")
        print("   Or post threads with the Twitter platform")

if __name__ == '__main__':
    asyncio.run(save_twitter_auth())
