#!/usr/bin/env python3
"""
Quick test script for email campaign system
Tests configuration and SMTP connection before running campaigns
"""

import json
import os
import sys
import smtplib
from email.mime.text import MIMEText

def check_config_file():
    """Check if email_config.json exists"""
    if not os.path.exists('email_config.json'):
        print("❌ email_config.json not found!")
        print("\n📋 Quick setup:")
        print("   1. Copy the example file:")
        print("      cp email_config.example.json email_config.json")
        print("\n   2. Edit email_config.json and update:")
        print("      - smtp.username (your Gmail)")
        print("      - smtp.password (Gmail app password)")
        print("      - smtp.from_name (your name)")
        print("      - campaign.product_name (your product)")
        print("\n   3. Get Gmail app password:")
        print("      Visit: https://myaccount.google.com/apppasswords")
        return False

    print("✅ email_config.json found")
    return True

def load_config():
    """Load and validate configuration"""
    try:
        with open('email_config.json', 'r') as f:
            config = json.load(f)

        # Check required fields
        required = [
            ('smtp.username', config.get('smtp', {}).get('username')),
            ('smtp.password', config.get('smtp', {}).get('password')),
            ('smtp.from_email', config.get('smtp', {}).get('from_email')),
            ('campaign.product_name', config.get('campaign', {}).get('product_name')),
        ]

        missing = [field for field, value in required if not value or value.startswith('your-')]

        if missing:
            print(f"❌ Missing or invalid configuration:")
            for field in missing:
                print(f"   - {field}")
            return None

        print("✅ Configuration valid")
        return config

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in email_config.json: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def test_smtp_connection(config):
    """Test SMTP connection"""
    print("\n🔌 Testing SMTP connection...")

    smtp_config = config['smtp']

    try:
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_config['username'], smtp_config['password'])
        server.quit()

        print("✅ SMTP connection successful!")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP authentication failed!")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure you're using an App Password, not your Gmail password")
        print("   2. Enable 2-Step Verification first:")
        print("      https://myaccount.google.com/security")
        print("   3. Generate App Password:")
        print("      https://myaccount.google.com/apppasswords")
        return False

    except Exception as e:
        print(f"❌ SMTP connection failed: {e}")
        return False

def test_send_email(config):
    """Send a test email"""
    test_mode = config.get('test_mode', {})

    if not test_mode.get('enabled'):
        print("\n⚠️  Test mode is disabled!")
        print("   Enable test mode in email_config.json before testing:")
        print('   "test_mode": { "enabled": true, ... }')
        return False

    test_email = test_mode.get('test_email', 'liu.lucian6@gmail.com')

    print(f"\n📧 Sending test email to {test_email}...")

    response = input(f"   Send test email? (y/n): ")
    if response.lower() != 'y':
        print("   Cancelled")
        return False

    try:
        smtp_config = config['smtp']
        campaign_config = config['campaign']

        # Create test email
        msg = MIMEText("This is a test email from MarketingMind AI.\n\nIf you receive this, your SMTP configuration is working correctly!")
        msg['Subject'] = f"Test Email - {campaign_config['product_name']}"
        msg['From'] = f"{smtp_config['from_name']} <{smtp_config['from_email']}>"
        msg['To'] = test_email

        # Send
        server = smtplib.SMTP(smtp_config['host'], smtp_config['port'], timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_config['username'], smtp_config['password'])
        server.send_message(msg)
        server.quit()

        print(f"✅ Test email sent to {test_email}!")
        print(f"\n📬 Check your inbox at {test_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

def main():
    print("="*60)
    print("🧪 Email Campaign System - Configuration Test")
    print("="*60)

    # Step 1: Check config file exists
    if not check_config_file():
        sys.exit(1)

    # Step 2: Load and validate config
    config = load_config()
    if not config:
        sys.exit(1)

    # Step 3: Test SMTP connection
    if not test_smtp_connection(config):
        sys.exit(1)

    # Step 4: Optionally send test email
    test_send_email(config)

    print("\n" + "="*60)
    print("✅ Configuration test complete!")
    print("="*60)
    print("\n🚀 Next steps:")
    print("   1. Run a test campaign:")
    print("      python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1")
    print("\n   2. Check campaign statistics:")
    print("      python src/email_campaign_manager.py --stats")
    print("\n   3. Test follow-up system:")
    print("      python src/email_campaign_manager.py --check-followups")
    print("\n📖 Full guide: QUICK_START_CAMPAIGN.md")

if __name__ == "__main__":
    main()
