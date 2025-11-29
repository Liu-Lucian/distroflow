#!/usr/bin/env python3
"""
MarketingMind AI - Main CLI Interface
AI-powered lead generation and social media automation
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.lead_scraper import LeadScraper
from src.twitter_client import TwitterClient
from src.config import config
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_config():
    """Validate that required configuration is present"""
    if not config.validate():
        logger.error("Missing required API keys!")
        logger.error("Please set up your .env file with:")
        logger.error("- ANTHROPIC_API_KEY or OPENAI_API_KEY")
        logger.error("- TWITTER_ACCESS_TOKEN")
        logger.error("- TWITTER_ACCESS_TOKEN_SECRET")
        logger.error("\nSee .env.example for a template")
        return False
    return True


def cmd_find_leads(args):
    """Find leads based on product description"""
    if not validate_config():
        return

    product_description = args.product

    # If product description is a file path, read it
    if Path(product_description).exists():
        with open(product_description, 'r') as f:
            product_description = f.read()

    logger.info("Starting lead generation campaign...")
    logger.info(f"Target: {args.count} leads")
    logger.info(f"Product: {product_description[:100]}...")

    scraper = LeadScraper()

    results = scraper.find_leads_from_product(
        product_description,
        target_count=args.count,
        find_emails=args.find_emails,
        generate_messages=args.generate_messages
    )

    if results['success']:
        # Export results
        export_format = args.format or 'excel'
        filepath = scraper.export_leads(results, format=export_format)

        logger.info("\n" + "="*50)
        logger.info("CAMPAIGN COMPLETED SUCCESSFULLY!")
        logger.info("="*50)
        logger.info(f"Total leads found: {len(results['leads'])}")
        logger.info(f"Influencers analyzed: {len(results['influencers'])}")
        logger.info(f"Keywords used: {', '.join(results['keywords'][:5])}...")

        if args.find_emails:
            emails_found = sum(1 for lead in results['leads'] if lead.get('email'))
            logger.info(f"Emails found: {emails_found} ({emails_found/len(results['leads'])*100:.1f}%)")

        logger.info(f"\nData exported to: {filepath}")
        logger.info("="*50)
    else:
        logger.error("Campaign failed. Check logs for details.")


def cmd_analyze_competitor(args):
    """Analyze competitor's followers"""
    if not validate_config():
        return

    logger.info(f"Analyzing competitor: @{args.username}")

    scraper = LeadScraper()
    followers = scraper.scrape_competitor_followers(
        args.username,
        max_followers=args.count
    )

    if followers:
        # Export
        from src.data_manager import DataManager
        manager = DataManager()

        export_format = args.format or 'excel'
        if export_format == 'excel':
            filepath = manager.export_to_excel(followers, f"competitor_{args.username}.xlsx")
        elif export_format == 'csv':
            filepath = manager.export_to_csv(followers, f"competitor_{args.username}.csv")
        else:
            filepath = manager.export_to_json(followers, f"competitor_{args.username}.json")

        logger.info("\n" + "="*50)
        logger.info("ANALYSIS COMPLETED!")
        logger.info("="*50)
        logger.info(f"Total followers scraped: {len(followers)}")
        logger.info(f"Data exported to: {filepath}")
        logger.info("="*50)


def cmd_grow(args):
    """Social media growth automation"""
    if not validate_config():
        return

    logger.info(f"Starting growth automation targeting: @{args.target}")
    logger.warning("Make sure you comply with Twitter's Terms of Service!")

    client = TwitterClient()

    # Get target user
    target_user = client.get_user_by_username(args.target)
    if not target_user:
        logger.error(f"Could not find user @{args.target}")
        return

    logger.info(f"Found target: {target_user['name']} ({target_user['followers_count']} followers)")

    # Get followers
    logger.info(f"Fetching followers to engage with...")
    followers = client.get_followers(target_user['id'], max_followers=args.count)

    logger.info(f"Processing {len(followers)} followers...")

    followed_count = 0
    for follower in followers[:args.count]:
        if args.follow:
            success = client.follow_user(follower['id'])
            if success:
                followed_count += 1

        if args.engage:
            # Get their recent tweets and like them
            tweets = client.get_user_tweets(follower['id'], max_results=1)
            if tweets:
                client.like_tweet(tweets[0]['id'])

        if followed_count >= args.count:
            break

    logger.info("\n" + "="*50)
    logger.info("GROWTH AUTOMATION COMPLETED!")
    logger.info("="*50)
    logger.info(f"Followed: {followed_count} users")
    logger.info("="*50)


def cmd_generate_message(args):
    """Generate personalized outreach message"""
    if not validate_config():
        return

    from src.outreach_engine import OutreachEngine

    engine = OutreachEngine()

    lead_data = {
        'name': args.name,
        'username': args.username,
        'description': args.bio or ''
    }

    product = args.product
    if Path(product).exists():
        with open(product, 'r') as f:
            product = f.read()

    if args.type == 'connection':
        message = engine.generate_connection_message(lead_data, product, args.tone)
        print("\nConnection Message:")
        print("-" * 50)
        print(message)
        print("-" * 50)
        print(f"Length: {len(message)} characters")

    elif args.type == 'dm':
        message = engine.generate_intro_dm(lead_data, product)
        print("\nIntro DM:")
        print("-" * 50)
        print(message)
        print("-" * 50)

    elif args.type == 'email':
        email = engine.generate_email(lead_data, product)
        print("\nEmail:")
        print("-" * 50)
        print(f"Subject: {email['subject']}")
        print()
        print(email['body'])
        print("-" * 50)


def main():
    parser = argparse.ArgumentParser(
        description='MarketingMind AI - AI-powered lead generation and social media automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find 500 leads for your product
  %(prog)s find-leads --product "Your product description" --count 500

  # Analyze competitor followers
  %(prog)s analyze-competitor --username competitor_handle --count 1000

  # Grow your social media
  %(prog)s grow --target competitor_handle --follow --engage --count 100

  # Generate personalized message
  %(prog)s generate-message --name "John Doe" --username johndoe --product "Your product" --type dm
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Find leads command
    parser_find = subparsers.add_parser('find-leads', help='Find leads based on product description')
    parser_find.add_argument('--product', required=True, help='Product description or path to file')
    parser_find.add_argument('--count', type=int, default=500, help='Number of leads to find (default: 500)')
    parser_find.add_argument('--find-emails', action='store_true', help='Find email addresses')
    parser_find.add_argument('--generate-messages', action='store_true', help='Generate outreach messages')
    parser_find.add_argument('--format', choices=['excel', 'csv', 'json'], help='Export format')
    parser_find.set_defaults(func=cmd_find_leads)

    # Analyze competitor command
    parser_competitor = subparsers.add_parser('analyze-competitor', help='Analyze competitor followers')
    parser_competitor.add_argument('--username', required=True, help='Competitor Twitter username')
    parser_competitor.add_argument('--count', type=int, default=500, help='Number of followers to scrape')
    parser_competitor.add_argument('--format', choices=['excel', 'csv', 'json'], help='Export format')
    parser_competitor.set_defaults(func=cmd_analyze_competitor)

    # Grow command
    parser_grow = subparsers.add_parser('grow', help='Social media growth automation')
    parser_grow.add_argument('--target', required=True, help='Target account to get followers from')
    parser_grow.add_argument('--follow', action='store_true', help='Auto-follow users')
    parser_grow.add_argument('--engage', action='store_true', help='Auto-like tweets')
    parser_grow.add_argument('--count', type=int, default=50, help='Number of users to process')
    parser_grow.set_defaults(func=cmd_grow)

    # Generate message command
    parser_msg = subparsers.add_parser('generate-message', help='Generate personalized outreach message')
    parser_msg.add_argument('--name', required=True, help='Lead name')
    parser_msg.add_argument('--username', required=True, help='Lead Twitter username')
    parser_msg.add_argument('--bio', help='Lead bio/description')
    parser_msg.add_argument('--product', required=True, help='Product description or path to file')
    parser_msg.add_argument('--type', choices=['connection', 'dm', 'email'], default='dm', help='Message type')
    parser_msg.add_argument('--tone', choices=['professional', 'casual', 'friendly'], default='professional', help='Message tone')
    parser_msg.set_defaults(func=cmd_generate_message)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run the command
    args.func(args)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
