"""
终极邮箱发现系统 - Ultimate Email Finder
解决核心问题：网站提取 + 多源数据 + 智能推断
"""

import os
import re
import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse

from document_parser import DocumentParser
from product_brain import ProductBrain
from contact_extractor import ContactExtractor
from twitter_scraper_playwright import TwitterPlaywrightScraper
from email_pattern_guesser import EmailPatternGuesser
from llm_contact_finder import LLMContactFinder
from email_verifier_v2 import EmailVerifierV2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class UltimateEmailFinder:
    """Ultimate email finder with aggressive website extraction and multi-source enrichment"""

    def __init__(self, auth_file: str = "auth.json", output_dir: str = "ultimate_leads",
                 enable_email_verification: bool = False, smtp_timeout: int = 10):
        self.auth_file = auth_file
        self.output_dir = output_dir
        self.enable_email_verification = enable_email_verification
        os.makedirs(output_dir, exist_ok=True)

        self.doc_parser = DocumentParser()
        self.product_brain = ProductBrain(api_provider="anthropic")
        self.contact_extractor = ContactExtractor()
        self.email_guesser = EmailPatternGuesser()
        self.llm_finder = LLMContactFinder()

        # Initialize email verifier (optional)
        if enable_email_verification:
            self.email_verifier = EmailVerifierV2(enable_smtp=True, timeout=smtp_timeout)
            logger.info("✅ Email verification enabled (SMTP checks active)")
        else:
            self.email_verifier = None
            logger.info("ℹ️  Email verification disabled (faster but less accurate)")

        self.scraper = None
        self.all_leads = []

    def run(self, product_doc: str, followers_per: int = 100, max_seeds: int = 10):
        """Run ultimate email finding pipeline"""
        logger.info("🚀 Ultimate Email Finder Starting...")

        # Basic setup
        product_text = self.doc_parser.parse_document(product_doc)
        product_analysis = self.product_brain.analyze_product(product_text)
        seed_accounts = self.product_brain.find_seed_accounts(product_analysis)[:max_seeds]

        logger.info(f"\n📊 Scraping {len(seed_accounts)} seed accounts...")

        # Initialize scraper
        self.scraper = TwitterPlaywrightScraper(headless=True, auth_file=self.auth_file)
        self.scraper.start()
        page = self.scraper.page

        # Scrape with AGGRESSIVE website extraction
        for i, account in enumerate(seed_accounts, 1):
            logger.info(f"\n📥 [{i}/{len(seed_accounts)}] @{account}...")

            try:
                followers = self.scraper.get_followers(account, max_followers=followers_per, extract_emails=True)

                for j, follower in enumerate(followers, 1):
                    username = follower['username']
                    logger.info(f"\n  [{j}/{len(followers)}] Processing @{username}...")

                    # STEP 1: Extract ALL possible URLs from bio
                    bio = follower.get('bio', '')
                    profile_url = follower.get('profile_url', '')

                    # Extract URLs with multiple patterns
                    websites = self._extract_all_urls(bio)

                    # STEP 1.5: Resolve short URLs (t.co, bit.ly, etc)
                    if websites:
                        logger.info(f"    🔗 Found {len(websites)} URL(s) in bio, resolving short links...")
                        resolved_websites = []
                        for url in websites:
                            if 't.co' in url or 'bit.ly' in url or 'tinyurl.com' in url:
                                resolved = self._resolve_short_url(url)
                                if resolved:
                                    resolved_websites.append(resolved)
                                    logger.info(f"      ✅ Resolved: {url} → {resolved}")
                                else:
                                    logger.info(f"      ⚠️  Failed to resolve: {url} (skipping)")
                                    # DON'T keep t.co if can't resolve - it's useless for email guessing
                            else:
                                resolved_websites.append(url)
                        websites = resolved_websites

                    if not websites:
                        logger.info(f"    🔍 No URL in bio, visiting profile page...")

                        # Visit the user's profile page to extract website
                        try:
                            page.goto(profile_url, wait_until='domcontentloaded', timeout=10000)
                            time.sleep(2)

                            # Try to find website link element
                            website_selectors = [
                                'a[href*="http"][data-testid*="ProfileHeaderCard"]',
                                'a[href*="http"]:has-text("http")',
                                'a[rel="noopener"][target="_blank"]',
                            ]

                            for selector in website_selectors:
                                try:
                                    link_elem = page.query_selector(selector)
                                    if link_elem:
                                        href = link_elem.get_attribute('href')
                                        if href and 'twitter.com' not in href and 'x.com' not in href:
                                            websites.append(href)
                                            logger.info(f"      ✅ Found website in profile: {href}")
                                            break
                                except:
                                    continue

                        except Exception as e:
                            logger.debug(f"      ⚠️ Error visiting profile: {e}")

                    # STEP 2: If still no website, extract from tweets
                    if not websites:
                        logger.info(f"    🔍 Extracting URLs from recent tweets...")

                        try:
                            # Get recent tweets
                            page.goto(profile_url, wait_until='domcontentloaded', timeout=10000)
                            time.sleep(2)

                            # Scroll to load tweets
                            for _ in range(3):
                                page.evaluate('window.scrollBy(0, 500)')
                                time.sleep(0.5)

                            # Extract tweet text
                            tweet_elements = page.query_selector_all('[data-testid="tweet"]')
                            tweets = []
                            for elem in tweet_elements[:10]:
                                try:
                                    text = elem.inner_text()
                                    tweets.append(text)
                                except:
                                    continue

                            # Extract URLs from tweets
                            all_tweet_text = ' '.join(tweets)
                            tweet_urls = self._extract_all_urls(all_tweet_text)

                            if tweet_urls:
                                websites.extend(tweet_urls)
                                logger.info(f"      ✅ Found {len(tweet_urls)} URL(s) in tweets")

                        except Exception as e:
                            logger.debug(f"      ⚠️ Error extracting from tweets: {e}")

                    # STEP 3: Infer website from username/bio
                    if not websites:
                        logger.info(f"    💡 Inferring website from username/bio...")
                        inferred_site = self._infer_website(username, bio)
                        if inferred_site:
                            websites.append(inferred_site)
                            logger.info(f"      ✅ Inferred website: {inferred_site}")

                    # Update follower data
                    follower['websites_found'] = websites
                    follower['website'] = websites[0] if websites else None

                    # STEP 4: Extract emails from bio/tweets
                    contacts = self.contact_extractor.extract_all_contacts(bio)

                    # STEP 5: If has website, scrape it aggressively
                    if websites and not contacts.get('emails'):
                        logger.info(f"    🌐 Scraping websites for emails...")
                        for site in websites[:2]:  # Top 2
                            try:
                                # Enhanced website scraping with contact page discovery
                                emails = self._scrape_website_aggressive(site)
                                if emails:
                                    contacts['emails'].extend(emails)
                                    logger.info(f"      ✅ Found {len(emails)} email(s) from {site}")
                                    break
                            except Exception as e:
                                logger.debug(f"      ⚠️ Failed to scrape {site}: {e}")

                    # STEP 6: If still no email, use pattern guessing
                    if not contacts.get('emails'):
                        name = follower.get('name', '')
                        if name and len(name.split()) >= 2 and follower.get('website'):
                            domain = self.email_guesser.extract_domain_from_website(follower['website'])
                            if domain:
                                guesses = self.email_guesser.guess_email(
                                    name.split()[0],
                                    name.split()[-1],
                                    domain
                                )
                                if guesses:
                                    contacts['emails'] = [guesses[0]['email']]
                                    follower['email_source'] = 'pattern_guessed'
                                    logger.info(f"      💡 Guessed: {guesses[0]['email']}")

                    # STEP 7: LLM-based inference for company email
                    if not contacts.get('emails') and (follower.get('website') or bio):
                        logger.info(f"    🤖 Using LLM to infer email...")
                        llm_result = self.llm_finder.analyze_profile_for_contacts({
                            'username': username,
                            'name': follower.get('name', ''),
                            'bio': bio,
                            'website': follower.get('website'),
                        })

                        if llm_result.get('possible_emails'):
                            top_email = llm_result['possible_emails'][0]
                            if top_email['confidence'] >= 60:
                                contacts['emails'] = [top_email['email']]
                                follower['email_source'] = 'llm_inferred'
                                logger.info(f"      🤖 LLM inferred: {top_email['email']}")

                    follower['all_contacts'] = contacts
                    follower['scraped_from'] = account
                    self.all_leads.append(follower)

                    # Summary log
                    status = "✅ EMAIL" if contacts.get('emails') else "❌ NO EMAIL"
                    website_status = f"📍 {len(websites)} websites" if websites else "⚠️ No website"
                    logger.info(f"    {status} | {website_status}")

            except Exception as e:
                logger.error(f"Error with @{account}: {e}")
                continue

        # Email verification (optional)
        if self.enable_email_verification and self.all_leads:
            logger.info("\n🔍 Verifying emails...")
            self._verify_all_emails()

        # Save and report
        summary = self._save_results()
        self._print_summary(summary)
        return summary

    def _extract_all_urls(self, text: str) -> List[str]:
        """Extract ALL URLs from text with multiple patterns"""
        urls = []

        # Pattern 1: Standard URLs
        standard = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
        urls.extend(standard)

        # Pattern 2: URLs without protocol
        no_protocol = re.findall(r'(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?', text)
        urls.extend([f"https://{url}" if not url.startswith('http') else url for url in no_protocol])

        # Pattern 3: Domain mentions (like "visit example.com")
        domain_mentions = re.findall(r'\b([a-zA-Z0-9-]+\.(com|io|net|org|ai|co))\b', text)
        urls.extend([f"https://{d[0]}" for d in domain_mentions])

        # Clean and deduplicate
        cleaned = []
        for url in urls:
            # Clean trailing punctuation
            url = url.rstrip('.,;:!?)')

            # Skip Twitter/X URLs (but KEEP t.co for expansion)
            if 'twitter.com' in url or 'x.com' in url:
                if 't.co' not in url:  # Only skip if NOT t.co
                    continue

            if url not in cleaned:
                cleaned.append(url)

        return cleaned

    def _resolve_short_url(self, short_url: str) -> Optional[str]:
        """Resolve short URL (t.co, bit.ly, etc) to final destination"""
        try:
            import requests
            # Follow redirects and get final URL
            resp = requests.head(short_url, allow_redirects=True, timeout=5)
            final_url = resp.url

            # Filter out unwanted destinations
            unwanted_domains = [
                'twitter.com', 'x.com',  # Twitter itself
                'youtube.com', 'youtu.be',  # YouTube (not company website)
                'instagram.com', 'facebook.com',  # Social media
                'linkedin.com',  # LinkedIn (separate system)
                'medium.com',  # Blog platform
            ]

            for domain in unwanted_domains:
                if domain in final_url:
                    logger.debug(f"      Filtered out {domain} from {short_url}")
                    return None

            # Check for newsletter/login pages (not useful for contact)
            unwanted_patterns = ['/newsletter', '/subscribe', '/login', '/signup', 'account.']
            for pattern in unwanted_patterns:
                if pattern in final_url.lower():
                    logger.debug(f"      Filtered out {pattern} page from {short_url}")
                    return None

            logger.debug(f"      Resolved {short_url} → {final_url}")
            return final_url
        except Exception as e:
            logger.debug(f"      Failed to resolve {short_url}: {e}")
            return None

    def _infer_website(self, username: str, bio: str) -> Optional[str]:
        """Infer website from username or bio mentions"""
        # Look for company mentions
        patterns = [
            rf'\b{username}\.(?:com|io|ai|co|net|org)\b',  # username.com
            r'@([a-zA-Z0-9_-]+)(?:\s|$)',  # @company mentions
            r'(?:founder|ceo|cto).*?(?:of|at)\s+([a-zA-Z0-9]+)',  # "CEO of CompanyName"
        ]

        for pattern in patterns:
            match = re.search(pattern, bio, re.IGNORECASE)
            if match:
                domain = match.group(1) if match.lastindex else match.group(0)
                domain = domain.replace('@', '').strip()

                # Try common TLDs
                for tld in ['.com', '.io', '.ai', '.co']:
                    potential = f"https://{domain}{tld}"
                    # Quick check if URL is reachable
                    try:
                        import requests
                        resp = requests.head(potential, timeout=3)
                        if resp.status_code < 400:
                            return potential
                    except:
                        continue

        return None

    def _scrape_website_aggressive(self, url: str) -> List[str]:
        """Aggressively scrape website for emails"""
        emails = set()

        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

            # Try main page
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                page_text = soup.get_text()
                page_emails = self.contact_extractor.extract_emails(page_text)
                emails.update(page_emails)

            # If no emails, try contact pages
            if not emails:
                base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
                contact_paths = ['/contact', '/about', '/team', '/contact-us', '/reach-us', '/get-in-touch']

                for path in contact_paths:
                    try:
                        contact_url = base_url + path
                        resp = requests.get(contact_url, headers=headers, timeout=5)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.content, 'html.parser')
                            page_text = soup.get_text()
                            page_emails = self.contact_extractor.extract_emails(page_text)
                            if page_emails:
                                emails.update(page_emails)
                                break
                    except:
                        continue

        except Exception as e:
            logger.debug(f"Error scraping {url}: {e}")

        return list(emails)

    def _verify_all_emails(self):
        """Verify all collected emails"""
        if not self.email_verifier:
            return

        # Collect all unique emails
        all_emails = []
        for lead in self.all_leads:
            emails = lead.get('all_contacts', {}).get('emails', [])
            all_emails.extend(emails)

        if not all_emails:
            logger.info("  No emails to verify")
            return

        unique_emails = list(set(all_emails))
        logger.info(f"  Verifying {len(unique_emails)} unique emails...")

        # Verify in batch
        verification_results = self.email_verifier.verify_emails_batch(
            unique_emails,
            max_workers=3  # Limit concurrency to avoid rate limiting
        )

        # Create lookup dict
        verification_map = {r.email: r for r in verification_results}

        # Update leads with verification results
        verified_count = 0
        invalid_count = 0
        unknown_count = 0

        for lead in self.all_leads:
            emails = lead.get('all_contacts', {}).get('emails', [])
            if not emails:
                continue

            verified_emails = []
            for email in emails:
                result = verification_map.get(email.lower())
                if result:
                    # Store verification result
                    if 'email_verification' not in lead:
                        lead['email_verification'] = {}

                    lead['email_verification'][email] = {
                        'status': result.status,
                        'confidence': result.confidence_score,
                        'is_disposable': result.is_disposable,
                        'is_free_provider': result.is_free_provider,
                        'mx_servers': result.mx_servers[:2] if result.mx_servers else []
                    }

                    # Only keep valid/unknown emails (filter out invalid)
                    if result.status in ['valid', 'unknown']:
                        verified_emails.append(email)
                        if result.status == 'valid':
                            verified_count += 1
                        else:
                            unknown_count += 1
                    else:
                        invalid_count += 1
                        logger.info(f"  ❌ Filtered out invalid: {email} (confidence: {result.confidence_score}%)")
                else:
                    # No verification result, keep email
                    verified_emails.append(email)

            # Update lead with verified emails
            lead['all_contacts']['emails'] = verified_emails
            lead['all_contacts']['emails_verified'] = len(verified_emails)

        logger.info(f"\n  📊 Verification Summary:")
        logger.info(f"     ✅ Valid: {verified_count}")
        logger.info(f"     ❓ Unknown: {unknown_count}")
        logger.info(f"     ❌ Invalid (filtered): {invalid_count}")

    def _save_results(self) -> Dict:
        """Save results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Stats
        total = len(self.all_leads)
        with_email = sum(1 for l in self.all_leads if l.get('all_contacts', {}).get('emails'))
        with_website = sum(1 for l in self.all_leads if l.get('website'))

        # CSV
        csv_data = []
        for lead in self.all_leads:
            contacts = lead.get('all_contacts', {})
            emails = contacts.get('emails', [])

            # Get verification info for first email (if available)
            email_status = ''
            email_confidence = ''
            if emails and 'email_verification' in lead:
                first_email = emails[0]
                verification = lead['email_verification'].get(first_email, {})
                email_status = verification.get('status', '')
                email_confidence = verification.get('confidence', '')

            csv_data.append({
                'username': lead.get('username'),
                'name': lead.get('name'),
                'bio': lead.get('bio'),
                'website': lead.get('website'),
                'websites_found': ', '.join(lead.get('websites_found', [])),
                'emails': ', '.join(emails),
                'email_source': lead.get('email_source', 'found'),
                'email_status': email_status,  # valid/invalid/unknown
                'email_confidence': email_confidence,  # 0-100
                'scraped_from': lead.get('scraped_from'),
            })

        csv_file = os.path.join(self.output_dir, f'leads_{timestamp}.csv')
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')

        # JSON
        json_file = os.path.join(self.output_dir, f'leads_{timestamp}.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_leads, f, indent=2, ensure_ascii=False)

        summary = {
            'total_leads': total,
            'leads_with_email': with_email,
            'email_rate': (with_email / total * 100) if total > 0 else 0,
            'leads_with_website': with_website,
            'website_discovery_rate': (with_website / total * 100) if total > 0 else 0,
            'output_file': csv_file,
        }

        summary_file = os.path.join(self.output_dir, f'summary_{timestamp}.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

    def _print_summary(self, summary: Dict):
        """Print summary"""
        logger.info("\n" + "="*60)
        logger.info("✅ Ultimate Email Finder Complete!")
        logger.info("="*60)
        logger.info(f"📊 Total Leads: {summary['total_leads']}")
        logger.info(f"📧 With Emails: {summary['leads_with_email']} ({summary['email_rate']:.1f}%)")
        logger.info(f"🌐 With Websites: {summary['leads_with_website']} ({summary['website_discovery_rate']:.1f}%)")
        logger.info(f"📁 Output: {summary['output_file']}")
        logger.info("="*60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ultimate_email_finder.py <product_doc> [followers] [seeds]")
        sys.exit(1)

    finder = UltimateEmailFinder()
    finder.run(
        product_doc=sys.argv[1],
        followers_per=int(sys.argv[2]) if len(sys.argv) > 2 else 100,
        max_seeds=int(sys.argv[3]) if len(sys.argv) > 3 else 10
    )
