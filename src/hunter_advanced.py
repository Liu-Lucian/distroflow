"""
Hunter.io 高级实现 - 基于完整流程分析
Advanced Hunter.io Implementation
"""

import os
import re
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
from deep_profile_scraper import DeepProfileScraper
from email_pattern_guesser import EmailPatternGuesser
from email_verifier import EmailVerifier
from llm_contact_finder import LLMContactFinder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class HunterAdvanced:
    """Advanced implementation following Hunter.io complete workflow"""

    def __init__(self, auth_file: str = "auth.json", output_dir: str = "hunter_advanced"):
        self.auth_file = auth_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Initialize all components
        self.doc_parser = DocumentParser()
        self.product_brain = ProductBrain(api_provider="anthropic")
        self.contact_extractor = ContactExtractor()
        self.deep_scraper = DeepProfileScraper(contact_extractor=self.contact_extractor)
        self.email_guesser = EmailPatternGuesser()
        self.llm_finder = LLMContactFinder()

        self.scraper = None
        self.all_leads = []

    def run_pipeline(
        self,
        product_doc_path: str,
        followers_per_account: int = 100,
        max_seed_accounts: int = 10,
        deep_scrape_all: bool = True  # 关键改进：默认深度爬取所有
    ):
        """Run advanced pipeline"""
        logger.info("🚀 Hunter Advanced Pipeline Starting...")

        # Step 1-3: Basic setup (same as before)
        product_text = self.doc_parser.parse_document(product_doc_path)
        product_analysis = self.product_brain.analyze_product(product_text)
        seed_accounts = self.product_brain.find_seed_accounts(product_analysis)[:max_seed_accounts]

        # Step 4: Scrape with IMMEDIATE deep scraping
        logger.info(f"\n📊 Scraping {len(seed_accounts)} seed accounts...")
        self._scrape_with_immediate_deep_dive(seed_accounts, followers_per_account)

        # Step 5: Multi-source email enrichment
        logger.info(f"\n🔍 Multi-source email enrichment for {len(self.all_leads)} leads...")
        self._enrich_emails_multi_source()

        # Step 6: Pattern-based guessing for ALL missing emails
        logger.info("\n💡 Pattern-based email guessing...")
        self._guess_all_missing_emails()

        # Step 7: Save and report
        summary = self._save_results()
        self._print_summary(summary)

        return summary

    def _scrape_with_immediate_deep_dive(self, seed_accounts: List[str], followers_per: int):
        """
        Scrape followers and IMMEDIATELY deep dive each one
        不是先爬完再深度爬取，而是爬一个就深度爬一个
        """
        self.scraper = TwitterPlaywrightScraper(headless=True, auth_file=self.auth_file)
        self.scraper.start()
        page = self.scraper.page

        for i, account in enumerate(seed_accounts, 1):
            logger.info(f"\n📥 [{i}/{len(seed_accounts)}] Processing @{account}...")

            try:
                # Get followers list
                followers = self.scraper.get_followers(account, max_followers=followers_per, extract_emails=True)

                if not followers:
                    continue

                logger.info(f"✓ Got {len(followers)} followers, starting immediate deep dive...")

                # Immediately deep scrape each follower
                for j, follower in enumerate(followers, 1):
                    username = follower.get('username')

                    # Basic bio extraction first
                    bio_contacts = self.contact_extractor.extract_all_contacts(
                        follower.get('bio', ''),
                        follower.get('profile_url')
                    )

                    # If no email in bio, IMMEDIATELY go deep
                    if not bio_contacts.get('emails'):
                        logger.info(f"  [{j}/{len(followers)}] 🔍 No email in bio, deep diving @{username}...")

                        # Deep scrape the profile
                        deep_data = self.deep_scraper.scrape_twitter_profile_deep(page, username, timeout=20)

                        # Merge all text sources
                        all_text = '\n'.join([
                            deep_data.get('bio', ''),
                            deep_data.get('pinned_tweet', ''),
                            '\n'.join(deep_data.get('recent_tweets', [])[:5])
                        ])

                        # Re-extract contacts from all sources
                        deep_contacts = self.contact_extractor.extract_all_contacts(all_text)

                        # Update follower data
                        follower.update({
                            'bio': deep_data.get('bio') or follower.get('bio'),
                            'location': deep_data.get('location'),
                            'website': deep_data.get('website') or follower.get('website'),
                            'pinned_tweet': deep_data.get('pinned_tweet'),
                            'recent_tweets': deep_data.get('recent_tweets'),
                            'external_links': deep_data.get('external_links'),
                            'all_contacts': deep_contacts,
                            'deep_scraped': True
                        })

                        # If still no email, try external resources
                        if not deep_contacts.get('emails') and deep_data.get('external_links'):
                            self._scrape_external_resources(follower, deep_data.get('external_links', []))

                        if deep_contacts.get('emails'):
                            logger.info(f"    ✅ Found {len(deep_contacts['emails'])} email(s) after deep dive!")

                    else:
                        logger.info(f"  [{j}/{len(followers)}] ✓ @{username} has email in bio")
                        follower['all_contacts'] = bio_contacts
                        follower['deep_scraped'] = False

                    follower['scraped_from'] = account
                    self.all_leads.append(follower)

                    # Delay to avoid rate limits
                    if j % 10 == 0:
                        time.sleep(5)

            except Exception as e:
                logger.error(f"Error with @{account}: {e}")
                continue

    def _scrape_external_resources(self, follower: Dict, external_links: List[Dict]):
        """Scrape external resources (Linktree, personal websites)"""
        contacts = follower.get('all_contacts', {})

        # Use LLM to prioritize links
        prioritized = self.llm_finder.prioritize_external_resources(external_links[:5])

        for link_info in prioritized[:2]:  # Only top 2
            url = link_info.get('url')
            priority = link_info.get('priority')

            if priority != 'high':
                continue

            try:
                logger.info(f"    🔗 Scraping {url}...")

                if 'linktr.ee' in url:
                    linktree_data = self.deep_scraper.scrape_linktree(url)
                    contacts['emails'].extend(linktree_data.get('emails', []))
                else:
                    website_data = self.deep_scraper.scrape_personal_website_deep(url, max_pages=3, timeout=5)
                    contacts['emails'].extend(website_data.get('emails', []))

                # Remove duplicates
                contacts['emails'] = list(set(contacts['emails']))

                if contacts['emails']:
                    logger.info(f"      ✅ Found {len(contacts['emails'])} email(s) from external!")
                    break

            except Exception as e:
                logger.debug(f"      ⚠️ Failed to scrape {url}: {e}")

    def _enrich_emails_multi_source(self):
        """
        Multi-source email enrichment (like Hunter.io)
        尝试多种方法找邮箱：Twitter bio → 主页 → 推文 → 外部链接 → 推测
        """
        for i, lead in enumerate(self.all_leads, 1):
            has_email = bool(lead.get('all_contacts', {}).get('emails'))

            if has_email:
                continue

            logger.info(f"  [{i}/{len(self.all_leads)}] 🔍 Enriching @{lead['username']}...")

            # Method 1: Check if we missed website in bio
            bio = lead.get('bio', '')
            website = lead.get('website')

            if not website:
                # Try to extract website from bio
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', bio)
                if urls:
                    website = urls[0]
                    lead['website'] = website

            # Method 2: If has website, scrape it
            if website and not has_email:
                try:
                    logger.info(f"    🌐 Scraping website: {website}")
                    website_data = self.deep_scraper.scrape_personal_website_deep(website, max_pages=3)

                    if website_data.get('emails'):
                        lead['all_contacts']['emails'].extend(website_data['emails'])
                        lead['all_contacts']['emails'] = list(set(lead['all_contacts']['emails']))
                        logger.info(f"      ✅ Found {len(website_data['emails'])} email(s)!")
                except Exception as e:
                    logger.debug(f"      ⚠️ Website scraping failed: {e}")

            # Method 3: LLM-assisted inference
            if not lead.get('all_contacts', {}).get('emails'):
                llm_analysis = self.llm_finder.analyze_profile_for_contacts(lead)

                if llm_analysis.get('possible_emails'):
                    for email_guess in llm_analysis['possible_emails'][:1]:  # Top 1
                        if email_guess['confidence'] >= 70:
                            lead['all_contacts']['emails'].append(email_guess['email'])
                            lead['email_source'] = 'llm_inferred'
                            logger.info(f"      💡 LLM inferred: {email_guess['email']} ({email_guess['confidence']}%)")

    def _guess_all_missing_emails(self):
        """
        Pattern-based email guessing for ALL leads without emails
        """
        # First, learn patterns from found emails
        known_emails = []

        for lead in self.all_leads:
            emails = lead.get('all_contacts', {}).get('emails', [])
            name = lead.get('name', '')
            website = lead.get('website')

            if emails and name and website:
                parts = name.split()
                if len(parts) >= 2:
                    domain = self.email_guesser.extract_domain_from_website(website)
                    if domain:
                        for email in emails:
                            known_emails.append({
                                'email': email,
                                'first_name': parts[0],
                                'last_name': parts[-1],
                                'domain': domain
                            })

        # Learn patterns
        if known_emails:
            patterns = self.email_guesser.learn_patterns_from_emails(known_emails)
            logger.info(f"  ✓ Learned patterns for {len(patterns)} domains")

        # Now guess for ALL leads without emails
        guessed_count = 0

        for lead in self.all_leads:
            has_email = bool(lead.get('all_contacts', {}).get('emails'))

            if has_email:
                continue

            name = lead.get('name', '')
            website = lead.get('website')

            # Try to infer website from bio if missing
            if not website:
                bio = lead.get('bio', '')
                # Look for company mentions
                company_match = re.search(r'@([a-zA-Z0-9_-]+)', bio)
                if company_match:
                    company = company_match.group(1)
                    website = f"https://{company}.com"

            if name and website:
                parts = name.split()
                if len(parts) >= 2:
                    first = parts[0]
                    last = parts[-1]
                    domain = self.email_guesser.extract_domain_from_website(website)

                    if domain:
                        guesses = self.email_guesser.guess_email(first, last, domain)

                        if guesses:
                            # Add top 3 guesses
                            lead['guessed_emails'] = guesses[:3]
                            lead['all_contacts']['emails'] = [g['email'] for g in guesses[:1]]
                            lead['email_source'] = 'pattern_guessed'
                            guessed_count += 1

                            logger.info(f"    💡 Guessed for @{lead['username']}: {guesses[0]['email']} ({guesses[0]['confidence']}%)")

        logger.info(f"  ✓ Guessed {guessed_count} emails")

    def _save_results(self) -> Dict:
        """Save results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Calculate stats
        total = len(self.all_leads)
        with_email = sum(1 for l in self.all_leads if l.get('all_contacts', {}).get('emails'))
        email_rate = (with_email / total * 100) if total > 0 else 0

        # Save CSV
        csv_data = []
        for lead in self.all_leads:
            contacts = lead.get('all_contacts', {})
            csv_data.append({
                'username': lead.get('username'),
                'name': lead.get('name'),
                'bio': lead.get('bio'),
                'emails': ', '.join(contacts.get('emails', [])),
                'email_source': lead.get('email_source', 'found'),
                'website': lead.get('website'),
                'deep_scraped': lead.get('deep_scraped', False),
                'scraped_from': lead.get('scraped_from'),
            })

        csv_file = os.path.join(self.output_dir, f'leads_{timestamp}.csv')
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # Save JSON
        json_file = os.path.join(self.output_dir, f'leads_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_leads, f, indent=2, ensure_ascii=False)

        summary = {
            'total_leads': total,
            'leads_with_email': with_email,
            'email_rate': email_rate,
            'deep_scraped': sum(1 for l in self.all_leads if l.get('deep_scraped')),
            'guessed_emails': sum(1 for l in self.all_leads if l.get('email_source') == 'pattern_guessed'),
            'output_file': csv_file,
            'json_file': json_file
        }

        summary_file = os.path.join(self.output_dir, f'summary_{timestamp}.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def _print_summary(self, summary: Dict):
        """Print results summary"""
        logger.info("\n" + "="*60)
        logger.info("✅ Hunter Advanced Pipeline Complete!")
        logger.info("="*60)
        logger.info(f"📊 Total Leads: {summary['total_leads']}")
        logger.info(f"📧 With Emails: {summary['leads_with_email']} ({summary['email_rate']:.1f}%)")
        logger.info(f"🔍 Deep Scraped: {summary['deep_scraped']}")
        logger.info(f"💡 Guessed: {summary['guessed_emails']}")
        logger.info(f"📁 Output: {summary['output_file']}")
        logger.info("="*60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hunter_advanced.py <product_doc> [followers] [seeds]")
        sys.exit(1)

    hunter = HunterAdvanced()
    hunter.run_pipeline(
        product_doc_path=sys.argv[1],
        followers_per_account=int(sys.argv[2]) if len(sys.argv) > 2 else 100,
        max_seed_accounts=int(sys.argv[3]) if len(sys.argv) > 3 else 10,
        deep_scrape_all=True
    )
