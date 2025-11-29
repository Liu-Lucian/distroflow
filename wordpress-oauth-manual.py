#!/usr/bin/env python3
"""
WordPress OAuth Manual Flow
手动完成 WordPress OAuth 认证流程
"""

import requests
import json
import webbrowser
from urllib.parse import urlparse, parse_qs

# Configuration
HUB_URL = "http://localhost:3000/api"
TOKEN_FILE = "/Users/l.u.c/my-app/MarketingMind AI/.marketingmind/hub-config.json"

def load_token():
    """Load JWT token from config"""
    with open(TOKEN_FILE, 'r') as f:
        config = json.load(f)
        return config['token']

def get_auth_url():
    """Get WordPress authorization URL"""
    token = load_token()

    response = requests.get(
        f"{HUB_URL}/platforms/wordpress/auth-url",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        data = response.json()
        return data['authUrl'], data['state']
    else:
        print(f"Error getting auth URL: {response.text}")
        return None, None

def complete_oauth(code, state):
    """Complete OAuth by calling the callback endpoint"""
    callback_url = f"{HUB_URL}/platforms/wordpress/callback"
    params = {
        'code': code,
        'state': state
    }

    response = requests.get(callback_url, params=params)

    if response.status_code in [200, 302]:
        print("\n✅ OAuth completed successfully!")
        return True
    else:
        print(f"\n❌ OAuth failed: {response.status_code}")
        print(response.text)
        return False

def check_connection():
    """Check if WordPress is connected"""
    token = load_token()

    response = requests.get(
        f"{HUB_URL}/platforms/connections",
        headers={"Authorization": f"Bearer {token}"}
    )

    if response.status_code == 200:
        connections = response.json()['connections']
        wp_conn = next((c for c in connections if c['platform'] == 'wordpress'), None)

        if wp_conn:
            print("\n✅ WordPress connected!")
            print(f"   Username: {wp_conn['metadata'].get('username')}")
            print(f"   Display name: {wp_conn['metadata'].get('display_name')}")
            return True
        else:
            print("\n❌ WordPress not connected")
            return False
    else:
        print(f"Error checking connections: {response.text}")
        return False

def main():
    print("=" * 60)
    print("WordPress OAuth Manual Flow")
    print("=" * 60)

    # Step 1: Get authorization URL
    print("\n📋 Step 1: Getting authorization URL...")
    auth_url, state = get_auth_url()

    if not auth_url:
        print("❌ Failed to get authorization URL")
        return

    print(f"✓ Auth URL obtained")
    print(f"✓ State: {state[:20]}...")

    # Step 2: Open browser
    print("\n🌐 Step 2: Opening browser for authorization...")
    print(f"\nURL: {auth_url}\n")

    # Try to open in default browser
    try:
        webbrowser.open(auth_url)
        print("✓ Browser opened")
    except:
        print("⚠️  Could not open browser automatically")

    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("=" * 60)
    print("1. A browser window should have opened with WordPress.com")
    print("2. If not, copy the URL above and paste it in your browser")
    print("3. Login to WordPress.com")
    print("4. Click 'Authorize' to grant access")
    print("5. You will be redirected to a URL like:")
    print("   http://localhost:3000/api/platforms/wordpress/callback?code=...")
    print("6. Copy the ENTIRE redirect URL and paste it below")
    print("=" * 60)

    # Step 3: Get the redirect URL from user
    print("\n📝 Step 3: After authorization, paste the redirect URL:")
    redirect_url = input("Redirect URL: ").strip()

    if not redirect_url:
        print("❌ No URL provided")
        return

    # Parse the URL to extract code and state
    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)

    code = params.get('code', [None])[0]
    returned_state = params.get('state', [None])[0]

    if not code:
        print("❌ No authorization code found in URL")
        return

    print(f"\n✓ Authorization code: {code[:20]}...")
    print(f"✓ State: {returned_state[:20] if returned_state else 'None'}...")

    # Step 4: Complete OAuth
    print("\n🔐 Step 4: Completing OAuth flow...")
    success = complete_oauth(code, state)

    if not success:
        return

    # Step 5: Verify connection
    print("\n✓ Step 5: Verifying connection...")
    check_connection()

    print("\n" + "=" * 60)
    print("✅ Done! You can now use:")
    print("   marketingmind hub connections")
    print("   marketingmind blog-quick \"topic\" --now")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
