#!/usr/bin/env python3
"""
Quick Email Send Test
直接测试邮件发送功能（不需要Twitter抓取）
"""

import sys
from src.email_campaign_manager import EmailCampaignManager

def main():
    print("="*60)
    print("📧 HireMe AI Email Campaign - Send Test")
    print("="*60)

    # Initialize campaign manager
    try:
        manager = EmailCampaignManager()
        print("\n✅ Email campaign manager initialized")
    except Exception as e:
        print(f"\n❌ Failed to initialize: {e}")
        return

    # Create sample lead data
    sample_leads = [
        {
            'email': 'test1@example.com',
            'name': 'John Doe',
            'username': 'johndoe',
            'scraped_from': 'ycombinator',
            'all_contacts': {
                'emails': ['test1@example.com']
            }
        },
        {
            'email': 'test2@example.com',
            'name': 'Jane Smith',
            'username': 'janesmith',
            'scraped_from': 'techcrunch',
            'all_contacts': {
                'emails': ['test2@example.com']
            }
        },
        {
            'email': 'test3@example.com',
            'name': 'Bob Johnson',
            'username': 'bobjohnson',
            'scraped_from': 'startups',
            'all_contacts': {
                'emails': ['test3@example.com']
            }
        }
    ]

    print(f"\n📋 Sample leads created: {len(sample_leads)}")
    print(f"   Test mode: {'ON' if manager.config['test_mode']['enabled'] else 'OFF'}")

    if manager.config['test_mode']['enabled']:
        test_email = manager.config['test_mode']['test_email']
        print(f"   All emails will be sent to: {test_email}")

    # Ask for confirmation
    print(f"\n⚠️  This will send {len(sample_leads)} test emails")
    response = input("Continue? (y/n): ")

    if response.lower() != 'y':
        print("\n❌ Test cancelled")
        return

    # Send emails
    print("\n🚀 Starting email campaign...\n")
    try:
        manager.start_campaign(sample_leads)

        print("\n" + "="*60)
        print("✅ TEST COMPLETE!")
        print("="*60)

        # Show next steps
        print("\n📋 Next Steps:")
        print("   1. Check your test email inbox:")
        if manager.config['test_mode']['enabled']:
            print(f"      {manager.config['test_mode']['test_email']}")
        print("\n   2. View campaign statistics:")
        print("      python src/email_campaign_manager.py --stats")
        print("\n   3. Check database:")
        print("      sqlite3 campaign_tracking.db \"SELECT email, name, status, sent_at FROM campaigns\"")

    except Exception as e:
        print(f"\n❌ Error during campaign: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
