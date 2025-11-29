#!/usr/bin/env python3
"""
Email Template Preview Tool
生成HTML预览文件，让你可以在浏览器中查看邮件效果
"""

import sys
from src.email_campaign_manager import EmailCampaignManager

def create_preview():
    """Create HTML preview of email templates"""

    # Initialize manager
    manager = EmailCampaignManager()

    # Sample lead data
    sample_lead = {
        'email': 'sample@example.com',
        'name': 'John Doe',
        'username': 'johndoe',
        'scraped_from': 'ycombinator'
    }

    # Get promo codes from config
    initial_promo = manager.config['promo_codes']['initial']['code']
    followup_promo = manager.config['promo_codes']['followup']['code']

    print("📧 生成邮件模板预览...\n")

    # Create initial email
    initial_msg = manager.create_initial_email(sample_lead, initial_promo)

    # Extract HTML content
    initial_html = None
    for part in initial_msg.walk():
        if part.get_content_type() == 'text/html':
            initial_html = part.get_payload(decode=True).decode('utf-8')
            break

    # Save initial email preview
    with open('email_preview_initial.html', 'w', encoding='utf-8') as f:
        f.write(initial_html)

    print("✅ 初始邮件预览已保存: email_preview_initial.html")
    print(f"   主题: {initial_msg['Subject']}")
    print(f"   优惠码: {initial_promo}\n")

    # Create followup email
    followup_msg = manager.create_followup_email(sample_lead, followup_promo, 1)

    # Extract HTML content
    followup_html = None
    for part in followup_msg.walk():
        if part.get_content_type() == 'text/html':
            followup_html = part.get_payload(decode=True).decode('utf-8')
            break

    # Save followup email preview
    with open('email_preview_followup.html', 'w', encoding='utf-8') as f:
        f.write(followup_html)

    print("✅ 跟进邮件预览已保存: email_preview_followup.html")
    print(f"   主题: {followup_msg['Subject']}")
    print(f"   优惠码: {followup_promo}\n")

    print("="*60)
    print("🌐 在浏览器中打开预览文件：\n")
    print("   初始邮件:")
    print("   open email_preview_initial.html\n")
    print("   跟进邮件:")
    print("   open email_preview_followup.html\n")
    print("="*60)

if __name__ == "__main__":
    try:
        create_preview()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
