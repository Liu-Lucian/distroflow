"""Main lead scraping orchestration"""

from typing import List, Dict, Optional
from .keyword_extractor import KeywordExtractor
from .twitter_client import TwitterClient
from .email_finder import EmailFinder
from .outreach_engine import OutreachEngine
from .data_manager import DataManager
from .rate_limiter import rate_limiter
from tqdm import tqdm
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadScraper:
    """Orchestrate the entire lead generation pipeline"""

    def __init__(self):
        self.keyword_extractor = KeywordExtractor()
        self.twitter_client = TwitterClient()
        self.email_finder = EmailFinder()
        self.outreach_engine = OutreachEngine()
        self.data_manager = DataManager()

    def find_leads_from_product(
        self,
        product_description: str,
        target_count: int = 500,
        find_emails: bool = True,
        generate_messages: bool = False
    ) -> Dict:
        """
        Complete lead generation pipeline from product description

        Args:
            product_description: Description of your product/service
            target_count: Number of leads to find
            find_emails: Whether to find email addresses
            generate_messages: Whether to generate outreach messages

        Returns:
            Dictionary with leads, influencers, and metadata
        """
        logger.info("Starting lead generation pipeline...")

        # Step 1: Extract keywords
        logger.info("Step 1: Extracting keywords from product description...")
        keyword_data = self.keyword_extractor.extract_keywords(product_description)
        keywords = keyword_data['keywords']
        hashtags = keyword_data['hashtags']

        logger.info(f"Keywords: {keywords[:5]}...")
        logger.info(f"Hashtags: {hashtags[:3]}...")

        # Step 2: Generate search queries
        queries = self.keyword_extractor.generate_search_queries(keywords, hashtags)
        logger.info(f"Generated {len(queries)} search queries")

        # Step 3: Find influencers
        logger.info("Step 2: Finding influencers on Twitter...")
        influencers = []
        session_start = time.time()
        actions_count = 0

        for query in tqdm(queries[:10], desc="Searching influencers"):
            # Check if should take a break
            if rate_limiter.should_take_break(actions_count, time.time() - session_start):
                rate_limiter.take_break()
                session_start = time.time()  # Reset session timer
                actions_count = 0

            results = self.twitter_client.search_influencers(
                query,
                max_results=3,
                min_followers=1000
            )
            influencers.extend(results)
            actions_count += 1

        # Remove duplicates
        seen = set()
        unique_influencers = []
        for inf in influencers:
            if inf['id'] not in seen:
                unique_influencers.append(inf)
                seen.add(inf['id'])

        influencers = unique_influencers
        logger.info(f"Found {len(influencers)} unique influencers")

        if not influencers:
            logger.warning("No influencers found. Try different keywords.")
            return {
                'leads': [],
                'influencers': [],
                'keywords': keywords,
                'success': False
            }

        # Step 4: Scrape followers
        logger.info("Step 3: Scraping followers from influencers...")
        all_leads = []
        followers_per_influencer = max(1, target_count // len(influencers))

        for influencer in tqdm(influencers[:5], desc="Scraping followers"):
            # Check if should take a break
            if rate_limiter.should_take_break(actions_count, time.time() - session_start):
                rate_limiter.take_break()
                session_start = time.time()
                actions_count = 0

            logger.info(f"Scraping followers of @{influencer['username']}...")
            followers = self.twitter_client.get_followers(
                influencer['id'],
                max_followers=min(followers_per_influencer, 100)
            )

            # Add source information
            for follower in followers:
                follower['found_via'] = f"@{influencer['username']}"

            all_leads.extend(followers)
            actions_count += 1

            if len(all_leads) >= target_count:
                break

        all_leads = all_leads[:target_count]
        logger.info(f"Total leads scraped: {len(all_leads)}")

        # Step 5: Find emails (optional)
        if find_emails:
            logger.info("Step 4: Finding email addresses...")
            for lead in tqdm(all_leads, desc="Finding emails"):
                email = self.email_finder.find_email_comprehensive(lead)
                lead['email'] = email

            emails_found = sum(1 for lead in all_leads if lead.get('email'))
            logger.info(f"Found {emails_found} email addresses ({emails_found/len(all_leads)*100:.1f}%)")

        # Step 6: Generate outreach messages (optional)
        if generate_messages:
            logger.info("Step 5: Generating personalized messages...")
            for lead in tqdm(all_leads[:50], desc="Generating messages"):  # Limit to first 50 to save API costs
                try:
                    message = self.outreach_engine.generate_connection_message(
                        lead,
                        product_description,
                        tone="professional"
                    )
                    lead['outreach_message'] = message
                except Exception as e:
                    logger.error(f"Error generating message: {e}")
                    lead['outreach_message'] = None

        return {
            'leads': all_leads,
            'influencers': influencers,
            'keywords': keywords,
            'hashtags': hashtags,
            'success': True
        }

    def scrape_competitor_followers(
        self,
        competitor_username: str,
        max_followers: int = 500
    ) -> List[Dict]:
        """
        Scrape followers from a competitor account

        Args:
            competitor_username: Twitter username of competitor
            max_followers: Maximum followers to scrape

        Returns:
            List of follower dictionaries
        """
        logger.info(f"Scraping followers of @{competitor_username}...")

        # Get competitor info
        competitor = self.twitter_client.get_user_by_username(competitor_username)

        if not competitor:
            logger.error(f"Could not find user @{competitor_username}")
            return []

        logger.info(f"Found {competitor['name']} with {competitor['followers_count']} followers")

        # Scrape followers
        followers = self.twitter_client.get_followers(
            competitor['id'],
            max_followers=max_followers
        )

        logger.info(f"Scraped {len(followers)} followers")

        return followers

    def export_leads(
        self,
        campaign_data: Dict,
        format: str = 'excel',
        filename: str = None
    ) -> str:
        """
        Export leads to file

        Args:
            campaign_data: Data from find_leads_from_product
            format: 'excel', 'csv', or 'json'
            filename: Optional filename

        Returns:
            Path to exported file
        """
        leads = campaign_data.get('leads', [])

        if format == 'excel':
            return self.data_manager.export_campaign_summary(
                leads,
                campaign_data.get('influencers', []),
                campaign_data.get('keywords', []),
                filename
            )
        elif format == 'csv':
            return self.data_manager.export_to_csv(leads, filename)
        elif format == 'json':
            return self.data_manager.export_to_json(leads, filename)
        else:
            logger.error(f"Unknown format: {format}")
            return None


# Example usage
if __name__ == "__main__":
    scraper = LeadScraper()

    product = """
    AI-powered customer service automation for e-commerce businesses.
    We help online stores reduce support costs by 60% while improving
    customer satisfaction through intelligent chatbots.
    """

    # Find leads
    results = scraper.find_leads_from_product(
        product,
        target_count=50,
        find_emails=True,
        generate_messages=False
    )

    if results['success']:
        # Export to Excel
        filepath = scraper.export_leads(results, format='excel')
        print(f"\nLeads exported to: {filepath}")

        # Print summary
        print(f"\nSummary:")
        print(f"- Total leads: {len(results['leads'])}")
        print(f"- Influencers found: {len(results['influencers'])}")
        print(f"- Keywords used: {len(results['keywords'])}")
