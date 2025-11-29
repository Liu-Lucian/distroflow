"""
Hunter风格Lead生成器 - Hunter-Style Lead Generator
深度爬取 + 模式推断 + SMTP验证 + LLM辅助
Deep crawling + Pattern inference + SMTP verification + LLM assistance
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
from deep_profile_scraper import DeepProfileScraper
from email_pattern_guesser import EmailPatternGuesser
from email_verifier import EmailVerifier
from llm_contact_finder import LLMContactFinder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class HunterStyleLeadGenerator:
    """Advanced lead generation with Hunter.io-style deep discovery"""

    def __init__(
        self,
        auth_file: str = "auth.json",
        output_dir: str = "hunter_leads",
        headless: bool = True,
        enable_deep_scraping: bool = True,
        enable_email_guessing: bool = True,
        enable_smtp_verification: bool = False,  # Can be slow
        enable_llm_assistance: bool = True
    ):
        """
        Initialize Hunter-Style Lead Generator

        Args:
            auth_file: Twitter auth file
            output_dir: Output directory
            headless: Run browser in headless mode
            enable_deep_scraping: Enable deep profile scraping
            enable_email_guessing: Enable email pattern guessing
            enable_smtp_verification: Enable SMTP verification (slow)
            enable_llm_assistance: Enable LLM-assisted discovery
        """
        self.auth_file = auth_file
        self.output_dir = output_dir
        self.headless = headless

        # Feature flags
        self.enable_deep_scraping = enable_deep_scraping
        self.enable_email_guessing = enable_email_guessing
        self.enable_smtp_verification = enable_smtp_verification
        self.enable_llm_assistance = enable_llm_assistance

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize components
        self.doc_parser = DocumentParser()
        self.product_brain = ProductBrain(api_provider="anthropic")
        self.contact_extractor = ContactExtractor()
        self.deep_scraper = DeepProfileScraper(contact_extractor=self.contact_extractor)
        self.email_guesser = EmailPatternGuesser()
        self.email_verifier = EmailVerifier() if enable_smtp_verification else None
        self.llm_finder = LLMContactFinder() if enable_llm_assistance else None

        self.scraper = None
        self.product_analysis = None
        self.all_leads = []

    def run_full_pipeline(
        self,
        product_doc_path: str,
        followers_per_account: int = 100,
        max_seed_accounts: int = 10,
        deep_scrape_limit: int = 50  # Only deep scrape top N leads
    ) -> Dict:
        """
        Run complete Hunter-style pipeline

        Args:
            product_doc_path: Path to product document
            followers_per_account: Followers per seed account
            max_seed_accounts: Max seed accounts
            deep_scrape_limit: Max profiles to deep scrape

        Returns:
            Summary dictionary
        """
        logger.info("="*60)
        logger.info("🚀 Starting Hunter-Style Lead Generation Pipeline")
        logger.info("="*60)
        logger.info(f"Deep Scraping: {self.enable_deep_scraping}")
        logger.info(f"Email Guessing: {self.enable_email_guessing}")
        logger.info(f"SMTP Verification: {self.enable_smtp_verification}")
        logger.info(f"LLM Assistance: {self.enable_llm_assistance}")
        logger.info("="*60)

        start_time = time.time()

        try:
            # Step 1: Parse product document
            logger.info("\n📄 Step 1: Parsing product document...")
            product_text = self.doc_parser.parse_document(product_doc_path)
            logger.info(f"✓ Extracted {len(product_text)} characters")

            # Step 2: AI Analysis
            logger.info("\n🧠 Step 2: Analyzing product with AI...")
            self.product_analysis = self.product_brain.analyze_product(product_text)
            self._save_analysis()
            logger.info("✓ Product analysis complete")

            # Step 3: Find seed accounts
            logger.info("\n🎯 Step 3: Finding seed Twitter accounts...")
            seed_accounts = self.product_brain.find_seed_accounts(self.product_analysis)
            seed_accounts = seed_accounts[:max_seed_accounts]
            logger.info(f"✓ Found {len(seed_accounts)} seed accounts")
            for acc in seed_accounts[:5]:
                logger.info(f"  - @{acc}")

            # Step 4: Scrape followers (BASIC first pass)
            logger.info("\n📊 Step 4: Scraping followers (basic pass)...")
            self._scrape_all_seeds_basic(seed_accounts, followers_per_account)

            # Step 5: Deep scraping (DEEP dive into promising leads)
            if self.enable_deep_scraping:
                logger.info(f"\n🔍 Step 5: Deep scraping top {deep_scrape_limit} leads...")
                self._deep_scrape_promising_leads(deep_scrape_limit)

            # Step 6: Email pattern learning and guessing
            if self.enable_email_guessing:
                logger.info("\n💡 Step 6: Email pattern learning and guessing...")
                self._learn_and_guess_emails()

            # Step 7: SMTP verification (optional, slow)
            if self.enable_smtp_verification:
                logger.info("\n📧 Step 7: SMTP email verification...")
                self._verify_emails()

            # Step 8: Filter and score
            logger.info("\n🔍 Step 8: Filtering and scoring leads...")
            qualified_leads = self._filter_and_score_leads()
            logger.info(f"✓ Found {len(qualified_leads)} qualified leads")

            # Step 9: Save results
            logger.info("\n💾 Step 9: Saving results...")
            summary = self._save_results(qualified_leads)

            elapsed = time.time() - start_time
            logger.info("\n" + "="*60)
            logger.info(f"✅ Pipeline Complete! ({elapsed/60:.1f} minutes)")
            logger.info("="*60)
            logger.info(f"📊 Total Leads: {summary['total_leads']}")
            logger.info(f"📧 With Emails: {summary['leads_with_email']} ({summary['email_rate']:.1f}%)")
            logger.info(f"✅ Verified Emails: {summary.get('verified_emails', 0)}")
            logger.info(f"💡 Guessed Emails: {summary.get('guessed_emails', 0)}")
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

    def _scrape_all_seeds_basic(self, seed_accounts: List[str], followers_per_account: int):
        """Basic scraping (just bio, no deep dive)"""
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

                    # Basic contact extraction from bio
                    for follower in followers:
                        contacts = self.contact_extractor.extract_all_contacts(
                            follower.get('bio', ''),
                            follower.get('profile_url')
                        )

                        follower['all_contacts'] = contacts
                        follower['contact_quality_score'] = self.contact_extractor.score_contact_quality(contacts)
                        follower['scraped_from'] = account
                        follower['deep_scraped'] = False  # Not yet

                    self.all_leads.extend(followers)

                # Delay between accounts
                if i < len(seed_accounts):
                    delay = 60
                    logger.info(f"⏸️  Waiting {delay}s before next account...")
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"❌ Error scraping @{account}: {e}")
                continue

    def _deep_scrape_promising_leads(self, limit: int):
        """Deep scrape the most promising leads"""
        # Sort leads by contact quality
        sorted_leads = sorted(
            self.all_leads,
            key=lambda x: x.get('contact_quality_score', 0),
            reverse=True
        )

        # Get top N leads that don't already have emails
        leads_to_deep_scrape = [
            lead for lead in sorted_leads
            if not lead.get('all_contacts', {}).get('emails')
        ][:limit]

        logger.info(f"  Deep scraping {len(leads_to_deep_scrape)} leads without emails...")

        page = self.scraper.page

        for i, lead in enumerate(leads_to_deep_scrape, 1):
            username = lead.get('username')
            logger.info(f"\n  🔍 [{i}/{len(leads_to_deep_scrape)}] Deep scraping @{username}...")

            try:
                # Deep scrape profile
                deep_data = self.deep_scraper.scrape_twitter_profile_deep(page, username, timeout=30)

                # Update lead with deep data
                lead['bio'] = deep_data.get('bio') or lead.get('bio')
                lead['location'] = deep_data.get('location')
                lead['website'] = deep_data.get('website') or lead.get('website')
                lead['pinned_tweet'] = deep_data.get('pinned_tweet')
                lead['recent_tweets'] = deep_data.get('recent_tweets')
                lead['external_links'] = deep_data.get('external_links')
                lead['deep_scraped'] = True

                # Re-extract contacts from all text
                all_text = (deep_data.get('bio', '') + '\n' +
                           deep_data.get('pinned_tweet', '') + '\n' +
                           '\n'.join(deep_data.get('recent_tweets', [])))

                contacts = self.contact_extractor.extract_all_contacts(all_text)
                lead['all_contacts'] = contacts

                # Scrape external resources (Linktree, personal website, etc.)
                external_links = deep_data.get('external_links', [])

                if external_links and self.enable_llm_assistance:
                    # Use LLM to prioritize which links to scrape
                    prioritized = self.llm_finder.prioritize_external_resources(external_links)

                    for link_info in prioritized[:3]:  # Top 3 only
                        if link_info.get('priority') == 'high':
                            url = link_info.get('url')
                            logger.info(f"    🔗 Scraping high-priority link: {url}")

                            try:
                                if 'linktr.ee' in url:
                                    linktree_data = self.deep_scraper.scrape_linktree(url)
                                    contacts['emails'].extend(linktree_data.get('emails', []))
                                    contacts['phones'].extend(linktree_data.get('phones', []))
                                else:
                                    website_data = self.deep_scraper.scrape_personal_website_deep(url, max_pages=3)
                                    contacts['emails'].extend(website_data.get('emails', []))
                                    contacts['phones'].extend(website_data.get('phones', []))

                                # Remove duplicates
                                contacts['emails'] = list(set(contacts['emails']))
                                contacts['phones'] = list(set(contacts['phones']))

                                if contacts['emails']:
                                    logger.info(f"      ✓ Found {len(contacts['emails'])} emails!")

                            except Exception as e:
                                logger.debug(f"      ⚠️  Error scraping {url}: {e}")

                # Update contact quality score
                lead['contact_quality_score'] = self.contact_extractor.score_contact_quality(contacts)

                # Small delay
                time.sleep(2)

            except Exception as e:
                logger.warning(f"    ⚠️  Error deep scraping @{username}: {e}")
                continue

    def _learn_and_guess_emails(self):
        """Learn email patterns and guess missing emails"""
        logger.info("  Learning email patterns from found emails...")

        # Collect known emails with names and domains
        known_emails = []

        for lead in self.all_leads:
            emails = lead.get('all_contacts', {}).get('emails', [])
            name = lead.get('name', '')
            website = lead.get('website')

            if emails and name and website:
                parts = name.split()
                if len(parts) >= 2:
                    first_name = parts[0]
                    last_name = parts[-1]
                    domain = self.email_guesser.extract_domain_from_website(website)

                    if domain:
                        for email in emails:
                            known_emails.append({
                                'email': email,
                                'first_name': first_name,
                                'last_name': last_name,
                                'domain': domain
                            })

        # Learn patterns
        patterns = self.email_guesser.learn_patterns_from_emails(known_emails)
        logger.info(f"  ✓ Learned patterns for {len(patterns)} domains")

        # Guess emails for leads without emails
        guessed_count = 0

        for lead in self.all_leads:
            has_email = bool(lead.get('all_contacts', {}).get('emails'))

            if not has_email:
                name = lead.get('name', '')
                website = lead.get('website')

                if name and website:
                    parts = name.split()
                    if len(parts) >= 2:
                        first_name = parts[0]
                        last_name = parts[-1]
                        domain = self.email_guesser.extract_domain_from_website(website)

                        if domain:
                            guesses = self.email_guesser.guess_email(first_name, last_name, domain)

                            if guesses:
                                lead['guessed_emails'] = guesses
                                # Add top guess to contacts
                                top_guess = guesses[0]
                                lead['all_contacts']['emails'] = [top_guess['email']]
                                lead['email_source'] = 'guessed'
                                guessed_count += 1

                                logger.info(f"    💡 Guessed email for @{lead['username']}: {top_guess['email']} ({top_guess['confidence']}%)")

        logger.info(f"  ✓ Guessed {guessed_count} emails")

    def _verify_emails(self):
        """Verify emails via SMTP"""
        if not self.email_verifier:
            return

        logger.info("  Verifying emails via SMTP (this may take a while)...")

        emails_to_verify = []

        for lead in self.all_leads:
            emails = lead.get('all_contacts', {}).get('emails', [])
            for email in emails:
                if email and '@' in email:
                    emails_to_verify.append((email, lead))

        logger.info(f"  Found {len(emails_to_verify)} emails to verify...")

        # Verify in batches
        batch_size = 10
        verified_count = 0

        for i in range(0, len(emails_to_verify), batch_size):
            batch = emails_to_verify[i:i+batch_size]
            batch_emails = [email for email, _ in batch]

            results = self.email_verifier.verify_batch(batch_emails, max_workers=3)

            for (email, lead), result in zip(batch, results):
                if 'email_verification' not in lead:
                    lead['email_verification'] = {}

                lead['email_verification'][email] = result

                if result.get('deliverable'):
                    verified_count += 1

            # Delay between batches
            time.sleep(5)

        logger.info(f"  ✓ Verified {verified_count}/{len(emails_to_verify)} emails as deliverable")

    def _filter_and_score_leads(self) -> List[Dict]:
        """Filter and score all collected leads"""
        qualified_leads = []

        for lead in self.all_leads:
            # Calculate relevance score
            bio = lead.get('bio', '')
            relevance_score = self.product_brain.score_account(bio, self.product_analysis)

            # Get contact quality score
            contact_score = lead.get('contact_quality_score', 0)

            # Boost score if deep scraped
            if lead.get('deep_scraped'):
                contact_score = min(contact_score + 20, 100)

            # Boost score if email verified
            if lead.get('email_verification'):
                for email, verification in lead.get('email_verification', {}).items():
                    if verification.get('deliverable'):
                        contact_score = min(contact_score + 30, 100)
                        break

            # Combined score
            total_score = (relevance_score * 0.6) + (contact_score * 0.4)

            lead['relevance_score'] = relevance_score
            lead['total_score'] = total_score

            # Filter
            has_contact = bool(
                lead.get('all_contacts', {}).get('emails') or
                lead.get('all_contacts', {}).get('phones') or
                lead.get('all_contacts', {}).get('websites')
            )

            if total_score > 20 or has_contact:
                qualified_leads.append(lead)

        # Sort by total score
        qualified_leads.sort(key=lambda x: x['total_score'], reverse=True)

        return qualified_leads

    def _save_analysis(self):
        """Save product analysis"""
        filename = os.path.join(self.output_dir, 'product_analysis.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.product_analysis, f, indent=2, ensure_ascii=False)

    def _save_results(self, leads: List[Dict]) -> Dict:
        """Save results and return summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save JSON
        json_file = os.path.join(self.output_dir, f'leads_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)

        # Save CSV
        csv_data = []
        for lead in leads:
            contacts = lead.get('all_contacts', {})

            row = {
                'username': lead.get('username'),
                'name': lead.get('name'),
                'bio': lead.get('bio'),
                'location': lead.get('location'),
                'profile_url': lead.get('profile_url'),
                'website': lead.get('website'),
                'scraped_from': lead.get('scraped_from'),
                'deep_scraped': lead.get('deep_scraped', False),
                'relevance_score': lead.get('relevance_score', 0),
                'contact_quality_score': lead.get('contact_quality_score', 0),
                'total_score': lead.get('total_score', 0),
                'emails': ', '.join(contacts.get('emails', [])),
                'email_source': lead.get('email_source', 'found'),
                'phones': ', '.join(contacts.get('phones', [])),
                'websites': ', '.join(contacts.get('websites', [])),
                'linkedin': contacts.get('social_media', {}).get('linkedin', ''),
                'github': contacts.get('social_media', {}).get('github', ''),
            }

            # Add verification status
            if lead.get('email_verification'):
                verified = any(v.get('deliverable') for v in lead['email_verification'].values())
                row['email_verified'] = verified
            else:
                row['email_verified'] = False

            csv_data.append(row)

        csv_file = os.path.join(self.output_dir, f'leads_{timestamp}.csv')
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # Calculate summary
        total_with_email = sum(1 for l in leads if l.get('all_contacts', {}).get('emails'))
        email_rate = (total_with_email / len(leads) * 100) if leads else 0

        summary = {
            'total_leads': len(leads),
            'leads_with_email': total_with_email,
            'email_rate': email_rate,
            'leads_with_phone': sum(1 for l in leads if l['all_contacts'].get('phones')),
            'leads_with_website': sum(1 for l in leads if l['all_contacts'].get('websites')),
            'high_quality_leads': sum(1 for l in leads if l.get('total_score', 0) > 50),
            'deep_scraped': sum(1 for l in leads if l.get('deep_scraped')),
            'guessed_emails': sum(1 for l in leads if l.get('email_source') == 'guessed'),
            'verified_emails': sum(1 for l in leads if l.get('email_verification') and any(v.get('deliverable') for v in l['email_verification'].values())),
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
        print("  python hunter_style_lead_generator.py <product_doc> [followers] [seeds] [deep_limit]")
        print()
        print("示例 / Examples:")
        print("  python hunter_style_lead_generator.py saas_product_optimized.md")
        print("  python hunter_style_lead_generator.py product.md 100 10 50")
        sys.exit(1)

    product_doc = sys.argv[1]
    followers = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    seeds = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    deep_limit = int(sys.argv[4]) if len(sys.argv) > 4 else 50

    generator = HunterStyleLeadGenerator(
        enable_deep_scraping=True,
        enable_email_guessing=True,
        enable_smtp_verification=False,  # Set to True if you want verification
        enable_llm_assistance=True
    )

    try:
        summary = generator.run_full_pipeline(
            product_doc_path=product_doc,
            followers_per_account=followers,
            max_seed_accounts=seeds,
            deep_scrape_limit=deep_limit
        )

        print("\n" + "🎉"*20)
        print("Hunter-Style Lead Generation Complete!")
        print("🎉"*20)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
