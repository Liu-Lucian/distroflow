"""
深度用户主页爬取器 - Deep Profile Scraper
进入用户主页，提取所有可能的线索
Inspired by Hunter.io's deep crawling approach
"""

import re
import time
import logging
import requests
from typing import Dict, List, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeout
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeepProfileScraper:
    """Deep scrape user profiles for contact information"""

    def __init__(self, contact_extractor=None):
        """
        Initialize Deep Profile Scraper

        Args:
            contact_extractor: ContactExtractor instance for extracting contacts
        """
        self.contact_extractor = contact_extractor

        # External resource patterns to follow
        self.external_platforms = {
            'linktree': r'linktr\.ee/([a-zA-Z0-9_-]+)',
            'beacons': r'beacons\.ai/([a-zA-Z0-9_-]+)',
            'bio_link': r'bio\.link/([a-zA-Z0-9_-]+)',
            'carrd': r'([a-zA-Z0-9_-]+)\.carrd\.co',
            'notion': r'notion\.site/([a-zA-Z0-9_-]+)',
            'medium': r'medium\.com/@([a-zA-Z0-9_-]+)',
            'substack': r'([a-zA-Z0-9_-]+)\.substack\.com',
            'github_io': r'([a-zA-Z0-9_-]+)\.github\.io',
        }

    def scrape_twitter_profile_deep(self, page: Page, username: str, timeout: int = 30) -> Dict:
        """
        Deep scrape a Twitter user's profile page

        Args:
            page: Playwright page object
            username: Twitter username
            timeout: Maximum time to spend on profile

        Returns:
            Dictionary with all extracted information
        """
        logger.info(f"🔍 Deep scraping profile: @{username}")

        result = {
            'username': username,
            'profile_url': f'https://twitter.com/{username}',
            'bio': '',
            'location': '',
            'website': '',
            'pinned_tweet': '',
            'recent_tweets': [],
            'external_links': [],
            'contact_info': {},
            'social_profiles': {},
        }

        try:
            # Navigate to user profile
            profile_url = f'https://twitter.com/{username}'
            page.goto(profile_url, wait_until='domcontentloaded', timeout=timeout * 1000)

            # Wait for profile to load
            time.sleep(2)

            # Extract bio
            try:
                bio_selector = '[data-testid="UserDescription"]'
                bio_elem = page.wait_for_selector(bio_selector, timeout=5000)
                if bio_elem:
                    result['bio'] = bio_elem.inner_text()
                    logger.info(f"  ✓ Bio: {result['bio'][:50]}...")
            except:
                pass

            # Extract location
            try:
                location_selector = '[data-testid="UserLocation"]'
                location_elem = page.query_selector(location_selector)
                if location_elem:
                    result['location'] = location_elem.inner_text()
            except:
                pass

            # Extract website (primary external link)
            try:
                website_selector = '[data-testid="UserUrl"] a'
                website_elem = page.query_selector(website_selector)
                if website_elem:
                    result['website'] = website_elem.get_attribute('href')
                    logger.info(f"  ✓ Website: {result['website']}")
            except:
                pass

            # Extract pinned tweet (often contains important info)
            try:
                pinned_selector = '[data-testid="primaryColumn"] article'
                pinned_elem = page.query_selector(pinned_selector)
                if pinned_elem:
                    pinned_text = pinned_elem.inner_text()
                    if 'Pinned' in pinned_text or '置顶' in pinned_text:
                        result['pinned_tweet'] = pinned_text
                        logger.info(f"  ✓ Pinned tweet found")
            except:
                pass

            # Scroll to load recent tweets
            try:
                for _ in range(3):  # Scroll 3 times
                    page.evaluate('window.scrollBy(0, 500)')
                    time.sleep(0.5)

                # Extract recent tweets
                tweet_elements = page.query_selector_all('[data-testid="tweet"]')
                for tweet_elem in tweet_elements[:10]:  # First 10 tweets
                    tweet_text = tweet_elem.inner_text()
                    result['recent_tweets'].append(tweet_text)

                logger.info(f"  ✓ Extracted {len(result['recent_tweets'])} recent tweets")
            except Exception as e:
                logger.debug(f"  Could not extract tweets: {e}")

            # Extract all links from bio and tweets
            all_text = result['bio'] + '\n' + result['pinned_tweet'] + '\n' + '\n'.join(result['recent_tweets'])

            # Find external platform links
            for platform, pattern in self.external_platforms.items():
                matches = re.findall(pattern, all_text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        if platform == 'linktree':
                            url = f'https://linktr.ee/{match}'
                        elif platform == 'beacons':
                            url = f'https://beacons.ai/{match}'
                        elif platform == 'carrd':
                            url = f'https://{match}.carrd.co'
                        elif platform == 'substack':
                            url = f'https://{match}.substack.com'
                        else:
                            url = match

                        result['external_links'].append({
                            'platform': platform,
                            'url': url,
                            'handle': match
                        })

                        logger.info(f"  ✓ Found {platform}: {url}")

            # Extract contact info from all collected text
            if self.contact_extractor:
                result['contact_info'] = self.contact_extractor.extract_all_contacts(all_text)

            return result

        except PlaywrightTimeout:
            logger.warning(f"  ⏱️  Timeout scraping @{username}")
            return result
        except Exception as e:
            logger.error(f"  ❌ Error scraping @{username}: {e}")
            return result

    def scrape_linktree(self, url: str, timeout: int = 10) -> Dict:
        """
        Scrape Linktree page for all external links

        Args:
            url: Linktree URL
            timeout: Request timeout

        Returns:
            Dictionary with extracted links and contacts
        """
        logger.info(f"🔗 Scraping Linktree: {url}")

        result = {
            'url': url,
            'links': [],
            'emails': [],
            'phones': [],
            'social_profiles': {}
        }

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)

                # Skip internal Linktree links
                if 'linktr.ee' in href or href.startswith('/'):
                    continue

                result['links'].append({
                    'url': href,
                    'text': text
                })

            logger.info(f"  ✓ Found {len(result['links'])} external links on Linktree")

            # Extract contacts from page text
            page_text = soup.get_text()
            if self.contact_extractor:
                contacts = self.contact_extractor.extract_all_contacts(page_text)
                result['emails'] = contacts.get('emails', [])
                result['phones'] = contacts.get('phones', [])
                result['social_profiles'] = contacts.get('social_media', {})

            return result

        except Exception as e:
            logger.warning(f"  ⚠️  Could not scrape Linktree: {e}")
            return result

    def scrape_personal_website_deep(self, url: str, max_pages: int = 5, timeout: int = 10) -> Dict:
        """
        Deep scrape personal website (multiple pages)

        Args:
            url: Website URL
            max_pages: Maximum pages to crawl
            timeout: Request timeout per page

        Returns:
            Dictionary with all extracted contacts
        """
        logger.info(f"🌐 Deep scraping website: {url}")

        result = {
            'url': url,
            'pages_scraped': [],
            'emails': [],
            'phones': [],
            'social_profiles': {},
            'documents': []  # PDF, DOC links
        }

        visited = set()
        to_visit = [url]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        base_domain = urlparse(url).netloc

        while to_visit and len(visited) < max_pages:
            current_url = to_visit.pop(0)

            if current_url in visited:
                continue

            try:
                logger.info(f"  📄 Scraping page: {current_url}")

                response = requests.get(current_url, headers=headers, timeout=timeout)
                response.raise_for_status()

                visited.add(current_url)
                result['pages_scraped'].append(current_url)

                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract text content
                page_text = soup.get_text()

                # Extract contacts
                if self.contact_extractor:
                    contacts = self.contact_extractor.extract_all_contacts(page_text)
                    result['emails'].extend(contacts.get('emails', []))
                    result['phones'].extend(contacts.get('phones', []))

                    # Merge social profiles
                    for platform, handle in contacts.get('social_media', {}).items():
                        if platform not in result['social_profiles']:
                            result['social_profiles'][platform] = handle

                # Find document links (PDF, DOC, PPT)
                for link in soup.find_all('a', href=True):
                    href = link.get('href')

                    # Check for documents
                    if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx', '.ppt', '.pptx']):
                        full_url = urljoin(current_url, href)
                        result['documents'].append(full_url)
                        logger.info(f"    📎 Found document: {full_url}")

                    # Find more pages to crawl (same domain only)
                    full_url = urljoin(current_url, href)
                    link_domain = urlparse(full_url).netloc

                    if link_domain == base_domain and full_url not in visited and full_url not in to_visit:
                        # Prioritize contact/about pages
                        if any(keyword in href.lower() for keyword in ['contact', 'about', 'team', 'connect']):
                            to_visit.insert(0, full_url)  # Add to front
                        else:
                            to_visit.append(full_url)

            except Exception as e:
                logger.debug(f"    ⚠️  Could not scrape {current_url}: {e}")
                continue

        # Remove duplicates
        result['emails'] = list(set(result['emails']))
        result['phones'] = list(set(result['phones']))

        logger.info(f"  ✓ Scraped {len(result['pages_scraped'])} pages")
        logger.info(f"  ✓ Found {len(result['emails'])} unique emails")
        logger.info(f"  ✓ Found {len(result['phones'])} unique phones")
        logger.info(f"  ✓ Found {len(result['documents'])} documents")

        return result

    def discover_company_domain(self, user_info: Dict) -> Optional[str]:
        """
        Discover company domain from user information

        Args:
            user_info: User information dictionary

        Returns:
            Company domain if found
        """
        bio = user_info.get('bio', '')
        website = user_info.get('website', '')
        location = user_info.get('location', '')

        # Extract domain from website
        if website:
            domain = urlparse(website).netloc
            if domain:
                # Remove www.
                domain = domain.replace('www.', '')
                return domain

        # Look for @company mentions in bio
        company_pattern = r'@([a-zA-Z0-9_-]+)'
        matches = re.findall(company_pattern, bio)

        # Try to find company website from bio text
        url_pattern = r'https?://([a-zA-Z0-9.-]+)'
        url_matches = re.findall(url_pattern, bio)
        if url_matches:
            domain = url_matches[0].replace('www.', '')
            return domain

        return None

    def extract_name_from_profile(self, user_info: Dict) -> Dict[str, str]:
        """
        Extract first and last name from user profile

        Args:
            user_info: User information

        Returns:
            Dictionary with first_name and last_name
        """
        name = user_info.get('name', '')

        # Simple name splitting
        parts = name.split()

        if len(parts) >= 2:
            return {
                'first_name': parts[0],
                'last_name': parts[-1],
                'full_name': name
            }
        elif len(parts) == 1:
            return {
                'first_name': parts[0],
                'last_name': '',
                'full_name': name
            }
        else:
            return {
                'first_name': '',
                'last_name': '',
                'full_name': ''
            }


# Example usage
if __name__ == "__main__":
    from contact_extractor import ContactExtractor
    from playwright.sync_api import sync_playwright

    extractor = ContactExtractor()
    scraper = DeepProfileScraper(contact_extractor=extractor)

    # Test website deep scrape
    result = scraper.scrape_personal_website_deep('https://example.com', max_pages=3)
    print(f"\n📊 Website scraping result:")
    print(f"Emails: {result['emails']}")
    print(f"Phones: {result['phones']}")
    print(f"Documents: {result['documents']}")

    # Test Linktree
    linktree_result = scraper.scrape_linktree('https://linktr.ee/someuser')
    print(f"\n🔗 Linktree result:")
    print(f"Links found: {len(linktree_result['links'])}")
    print(f"Emails: {linktree_result['emails']}")
