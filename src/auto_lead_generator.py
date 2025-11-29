"""
自动化Lead生成器 - Automated Lead Generator
完全自动化的系统：读取产品文档 → 分析 → 找目标账号 → 爬取 → 提取联系方式
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd

from document_parser import DocumentParser
from product_brain import ProductBrain
from contact_extractor import ContactExtractor
from twitter_scraper_playwright import TwitterPlaywrightScraper

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class AutoLeadGenerator:
    """Fully automated lead generation system"""

    def __init__(
        self,
        auth_file: str = "auth.json",
        output_dir: str = "auto_leads",
        headless: bool = True
    ):
        """
        Initialize Auto Lead Generator

        Args:
            auth_file: Path to Twitter auth file
            output_dir: Directory to save results
            headless: Run browser in headless mode
        """
        self.auth_file = auth_file
        self.output_dir = output_dir
        self.headless = headless

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize components
        self.doc_parser = DocumentParser()
        self.product_brain = ProductBrain(api_provider="anthropic")
        self.contact_extractor = ContactExtractor()
        self.scraper = None

        # State
        self.product_analysis = None
        self.all_leads = []

    def run_full_pipeline(
        self,
        product_doc_path: str,
        followers_per_account: int = 100,
        max_seed_accounts: int = 10
    ) -> Dict:
        """
        Run complete automated pipeline

        Args:
            product_doc_path: Path to product document (PDF, MD, URL, etc.)
            followers_per_account: How many followers to scrape per seed account
            max_seed_accounts: Maximum number of seed accounts to process

        Returns:
            Summary dictionary
        """
        logger.info("="*60)
        logger.info("🚀 Starting Automated Lead Generation Pipeline")
        logger.info("="*60)

        start_time = time.time()

        try:
            # Step 1: Parse product document
            logger.info("\n📄 Step 1: Parsing product document...")
            product_text = self.doc_parser.parse_document(product_doc_path)
            logger.info(f"✓ Extracted {len(product_text)} characters")

            # Step 2: Analyze with AI
            logger.info("\n🧠 Step 2: Analyzing product with AI...")
            self.product_analysis = self.product_brain.analyze_product(product_text)
            self._save_analysis()
            logger.info("✓ Product analysis complete")
            logger.info(f"  - Keywords: {len(self.product_analysis['keywords'])}")
            logger.info(f"  - Target Personas: {len(self.product_analysis['target_personas'])}")
            logger.info(f"  - Industries: {len(self.product_analysis['industries'])}")

            # Step 3: Find seed accounts
            logger.info("\n🎯 Step 3: Finding seed Twitter accounts...")
            seed_accounts = self.product_brain.find_seed_accounts(self.product_analysis)
            seed_accounts = seed_accounts[:max_seed_accounts]
            logger.info(f"✓ Found {len(seed_accounts)} seed accounts")
            for acc in seed_accounts[:5]:
                logger.info(f"  - @{acc}")
            if len(seed_accounts) > 5:
                logger.info(f"  ... and {len(seed_accounts)-5} more")

            # Step 4: Scrape followers
            logger.info("\n📊 Step 4: Scraping followers from seed accounts...")
            self._scrape_all_seeds(seed_accounts, followers_per_account)

            # Step 5: Filter and score leads
            logger.info("\n🔍 Step 5: Filtering and scoring leads...")
            qualified_leads = self._filter_and_score_leads()
            logger.info(f"✓ Found {len(qualified_leads)} qualified leads")

            # Step 6: Save results
            logger.info("\n💾 Step 6: Saving results...")
            summary = self._save_results(qualified_leads)

            elapsed = time.time() - start_time
            logger.info("\n" + "="*60)
            logger.info(f"✅ Pipeline Complete! ({elapsed/60:.1f} minutes)")
            logger.info("="*60)
            logger.info(f"📊 Total Leads: {summary['total_leads']}")
            logger.info(f"📧 With Emails: {summary['leads_with_email']}")
            logger.info(f"📱 With Phones: {summary['leads_with_phone']}")
            logger.info(f"🌐 With Websites: {summary['leads_with_website']}")
            logger.info(f"⭐ High Quality: {summary['high_quality_leads']}")
            logger.info(f"📁 Output: {summary['output_file']}")
            logger.info("="*60)

            return summary

        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            raise

        finally:
            if self.scraper:
                self.scraper.close()

    def _save_analysis(self):
        """Save product analysis to file"""
        filename = os.path.join(self.output_dir, 'product_analysis.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.product_analysis, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Saved analysis to {filename}")

    def _scrape_all_seeds(self, seed_accounts: List[str], followers_per_account: int):
        """Scrape followers from all seed accounts"""
        # Initialize scraper
        self.scraper = TwitterPlaywrightScraper(
            headless=self.headless,
            auth_file=self.auth_file
        )
        self.scraper.start()

        for i, account in enumerate(seed_accounts, 1):
            logger.info(f"\n📥 [{i}/{len(seed_accounts)}] Scraping @{account}...")

            try:
                followers = self.scraper.get_followers(
                    username=account,
                    max_followers=followers_per_account,
                    extract_emails=True
                )

                if followers:
                    logger.info(f"✓ Scraped {len(followers)} followers from @{account}")

                    # Extract additional contact info
                    for j, follower in enumerate(followers, 1):
                        # Extract from bio
                        contacts = self.contact_extractor.extract_all_contacts(
                            follower.get('bio', ''),
                            follower.get('profile_url')
                        )

                        # If no email found in bio, try to scrape their website
                        if not contacts['emails'] and contacts.get('websites'):
                            logger.info(f"  [{j}/{len(followers)}] Trying website for @{follower['username']}...")

                            for website in contacts['websites'][:1]:  # Only try first website
                                try:
                                    website_contacts = self.contact_extractor.extract_from_website(website, timeout=5)

                                    if website_contacts.get('emails'):
                                        logger.info(f"  ✓ Found {len(website_contacts['emails'])} emails on website!")
                                        contacts['emails'].extend(website_contacts['emails'])
                                        contacts['email_source'] = 'website'

                                    if website_contacts.get('phones'):
                                        contacts['phones'].extend(website_contacts['phones'])

                                    # Remove duplicates
                                    contacts['emails'] = list(set(contacts['emails']))
                                    contacts['phones'] = list(set(contacts['phones']))

                                except Exception as e:
                                    logger.debug(f"  ⚠️  Website scraping failed: {e}")
                                    continue

                        # Merge contact info
                        follower['all_contacts'] = contacts
                        follower['contact_quality_score'] = self.contact_extractor.score_contact_quality(contacts)

                        # Add source info
                        follower['scraped_from'] = account
                        follower['seed_account'] = account

                        # Log progress
                        if contacts['emails']:
                            logger.info(f"  ✓ [{j}/{len(followers)}] @{follower['username']} - {len(contacts['emails'])} email(s)")

                    self.all_leads.extend(followers)
                else:
                    logger.warning(f"⚠️  No followers found for @{account}")

                # Delay between accounts (human-like)
                if i < len(seed_accounts):
                    delay = 60  # 1 minute between accounts
                    logger.info(f"⏸️  Waiting {delay}s before next account...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"❌ Error scraping @{account}: {e}")
                continue

    def _filter_and_score_leads(self) -> List[Dict]:
        """Filter and score all collected leads"""
        qualified_leads = []

        for lead in self.all_leads:
            # Calculate relevance score based on product analysis
            bio = lead.get('bio', '')
            relevance_score = self.product_brain.score_account(bio, self.product_analysis)

            # Get contact quality score
            contact_score = lead.get('contact_quality_score', 0)

            # Combined score
            total_score = (relevance_score * 0.6) + (contact_score * 0.4)

            lead['relevance_score'] = relevance_score
            lead['total_score'] = total_score

            # Filter: keep if score > 20 or has contact info
            has_contact = (
                lead.get('email') or
                lead['all_contacts'].get('emails') or
                lead['all_contacts'].get('phones') or
                lead['all_contacts'].get('websites')
            )

            if total_score > 20 or has_contact:
                qualified_leads.append(lead)

        # Sort by total score
        qualified_leads.sort(key=lambda x: x['total_score'], reverse=True)

        return qualified_leads

    def _save_results(self, leads: List[Dict]) -> Dict:
        """Save results and return summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save full data to JSON
        json_file = os.path.join(self.output_dir, f'leads_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)

        # Save to CSV (flattened)
        csv_data = []
        for lead in leads:
            row = {
                'username': lead.get('username'),
                'name': lead.get('name'),
                'bio': lead.get('bio'),
                'email': lead.get('email'),
                'profile_url': lead.get('profile_url'),
                'scraped_from': lead.get('scraped_from'),
                'relevance_score': lead.get('relevance_score', 0),
                'contact_quality_score': lead.get('contact_quality_score', 0),
                'total_score': lead.get('total_score', 0),
            }

            # Add extracted contacts
            contacts = lead.get('all_contacts', {})
            row['all_emails'] = ', '.join(contacts.get('emails', []))
            row['phones'] = ', '.join(contacts.get('phones', []))
            row['websites'] = ', '.join(contacts.get('websites', []))
            row['linkedin'] = contacts.get('social_media', {}).get('linkedin', '')
            row['github'] = contacts.get('social_media', {}).get('github', '')

            csv_data.append(row)

        csv_file = os.path.join(self.output_dir, f'leads_{timestamp}.csv')
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # Calculate summary
        summary = {
            'total_leads': len(leads),
            'leads_with_email': sum(1 for l in leads if l.get('email') or l['all_contacts'].get('emails')),
            'leads_with_phone': sum(1 for l in leads if l['all_contacts'].get('phones')),
            'leads_with_website': sum(1 for l in leads if l['all_contacts'].get('websites')),
            'high_quality_leads': sum(1 for l in leads if l.get('total_score', 0) > 50),
            'output_file': csv_file,
            'json_file': json_file,
            'timestamp': timestamp
        }

        # Save summary
        summary_file = os.path.join(self.output_dir, f'summary_{timestamp}.json')
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        return summary


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法 / Usage:")
        print("  python auto_lead_generator.py <product_doc_path> [followers_per_account] [max_seed_accounts]")
        print()
        print("示例 / Examples:")
        print("  python auto_lead_generator.py product.md")
        print("  python auto_lead_generator.py product.pdf 200 15")
        print("  python auto_lead_generator.py https://myproduct.com/about")
        sys.exit(1)

    product_doc = sys.argv[1]
    followers_per = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    max_seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    generator = AutoLeadGenerator()

    try:
        summary = generator.run_full_pipeline(
            product_doc_path=product_doc,
            followers_per_account=followers_per,
            max_seed_accounts=max_seeds
        )

        print("\n" + "🎉"*20)
        print("Automated Lead Generation Complete!")
        print("🎉"*20)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
