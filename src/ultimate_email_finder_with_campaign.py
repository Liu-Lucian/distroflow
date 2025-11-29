"""
Ultimate Email Finder with Automated Campaign
完整流程：
1. 抓取Twitter leads
2. 验证邮箱
3. 自动发送介绍邮件
4. 追踪转化
5. 24小时后自动跟进
"""

import sys
import logging
from ultimate_email_finder import UltimateEmailFinder
from email_campaign_manager import EmailCampaignManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ultimate_email_finder_with_campaign.py <product_doc> [followers] [seeds]")
        print("\nExample:")
        print("  python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 20 2")
        print("\nThis will:")
        print("  1. Find leads from Twitter")
        print("  2. Verify email addresses")
        print("  3. Send introduction emails with 20% discount code")
        print("  4. Track conversions")
        print("  5. Auto-follow-up after 24 hours with 30% discount")
        sys.exit(1)

    product_doc = sys.argv[1]
    followers_per = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    max_seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    logger.info("="*60)
    logger.info("🚀 Ultimate Email Finder + Campaign System")
    logger.info("="*60)

    # Step 1: Find leads
    logger.info("\n📊 STEP 1: Finding leads from Twitter...")
    finder = UltimateEmailFinder(
        enable_email_verification=True,  # Enable verification
        smtp_timeout=10
    )

    summary = finder.run(
        product_doc=product_doc,
        followers_per=followers_per,
        max_seeds=max_seeds
    )

    logger.info(f"\n✅ Found {summary['leads_with_email']} leads with verified emails")

    # Step 2: Start email campaign
    if summary['leads_with_email'] > 0:
        logger.info("\n📧 STEP 2: Starting email campaign...")

        # Ask for confirmation
        response = input(f"\nSend emails to {summary['leads_with_email']} leads? (y/n): ")

        if response.lower() == 'y':
            # Initialize campaign manager
            campaign_manager = EmailCampaignManager()

            # Get leads with emails
            leads_with_emails = [
                lead for lead in finder.all_leads
                if lead.get('all_contacts', {}).get('emails')
            ]

            # Start campaign
            campaign_manager.start_campaign(leads_with_emails)

            logger.info("\n" + "="*60)
            logger.info("✅ CAMPAIGN STARTED!")
            logger.info("="*60)
            logger.info("\n📋 Next Steps:")
            logger.info("   1. Monitor conversions in campaign_tracking.db")
            logger.info("   2. Run follow-ups in 24 hours:")
            logger.info("      python src/email_campaign_manager.py --check-followups")
            logger.info("   3. Check statistics:")
            logger.info("      python src/email_campaign_manager.py --stats")
            logger.info("\n💡 Tip: Set up a cron job to auto-check follow-ups:")
            logger.info("   0 */6 * * * cd /path/to/project && python src/email_campaign_manager.py --check-followups")

        else:
            logger.info("\n❌ Campaign cancelled")
    else:
        logger.info("\n⚠️  No leads with emails found. Cannot start campaign.")


if __name__ == "__main__":
    main()
