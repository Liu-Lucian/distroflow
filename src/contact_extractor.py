"""
联系方式提取器 - Contact Extractor
从Twitter bio、网站等提取所有可能的联系方式
Extract all possible contact information from profiles
"""

import re
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContactExtractor:
    """Extract contact information from text"""

    def __init__(self):
        # Email patterns
        self.email_patterns = [
            # Standard email
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            # Email with spaces (e.g., "email @ domain . com")
            r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b',
            # Email with [at] or (at)
            r'\b[A-Za-z0-9._%+-]+\s*[\[\(]at[\]\)]\s*[A-Za-z0-9.-]+\s*[\[\(]dot[\]\)]\s*[A-Z|a-z]{2,}\b',
            # Common obfuscations
            r'\b[A-Za-z0-9._%+-]+\s*\[at\]\s*[A-Za-z0-9.-]+\s*\[dot\]\s*[A-Z|a-z]{2,}\b',
        ]

        # Phone patterns (international + US + common formats)
        self.phone_patterns = [
            # International: +1-234-567-8900
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            # US: (234) 567-8900
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',
            # Simple: 234-567-8900 or 234.567.8900
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}',
            # International with country code
            r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
        ]

        # URL patterns
        self.url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'

        # Social media patterns
        self.social_patterns = {
            'linkedin': r'linkedin\.com/in/([a-zA-Z0-9-]+)',
            'github': r'github\.com/([a-zA-Z0-9-]+)',
            'instagram': r'instagram\.com/([a-zA-Z0-9_.]+)',
            'telegram': r'(?:t\.me|telegram\.me)/([a-zA-Z0-9_]+)',
            'discord': r'discord\.gg/([a-zA-Z0-9]+)',
        }

        # Contact indicators
        self.contact_indicators = [
            'contact', 'email', 'reach', 'dm', 'inquiries',
            'business', 'collab', 'partnership', 'hello',
            'info', 'support', 'sales', 'connect'
        ]

    def extract_all_contacts(self, text: str, url: Optional[str] = None) -> Dict:
        """
        Extract all possible contact information

        Args:
            text: Text to search (bio, about, etc.)
            url: Optional URL to check for contact info

        Returns:
            Dictionary with all found contacts
        """
        contacts = {
            'emails': [],
            'phones': [],
            'websites': [],
            'social_media': {},
            'contact_indicators': []
        }

        if not text:
            return contacts

        # Extract emails
        contacts['emails'] = self.extract_emails(text)

        # Extract phones
        contacts['phones'] = self.extract_phones(text)

        # Extract URLs
        contacts['websites'] = self.extract_urls(text)

        # Extract social media
        contacts['social_media'] = self.extract_social_media(text)

        # Check for contact indicators
        contacts['contact_indicators'] = self.find_contact_indicators(text)

        # If URL provided, check for common contact paths
        if url:
            contact_urls = self.generate_contact_urls(url)
            contacts['potential_contact_pages'] = contact_urls

        return contacts

    def extract_emails(self, text: str) -> List[str]:
        """Extract all email addresses"""
        emails = set()

        for pattern in self.email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the email
                email = match.lower().strip()
                # Remove spaces
                email = re.sub(r'\s+', '', email)
                # Replace [at] with @
                email = re.sub(r'\[at\]|\(at\)', '@', email)
                # Replace [dot] with .
                email = re.sub(r'\[dot\]|\(dot\)', '.', email)

                # Validate email
                if self._is_valid_email(email):
                    emails.add(email)

        return list(emails)

    def extract_phones(self, text: str) -> List[str]:
        """Extract all phone numbers"""
        phones = set()

        for pattern in self.phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Clean up phone number
                phone = re.sub(r'[^\d+]', '', match)
                if len(phone) >= 10:  # Valid phone number
                    phones.add(match.strip())

        return list(phones)

    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs"""
        urls = set()

        matches = re.findall(self.url_pattern, text)
        for match in matches:
            urls.add(match.strip())

        # Also look for domain names without http://
        domain_pattern = r'\b(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]+\.[a-zA-Z]{2,6}\b'
        matches = re.findall(domain_pattern, text)
        for match in matches:
            if not match.endswith('.com') and not match.endswith('.io') and not match.endswith('.net'):
                continue
            if 'twitter' not in match.lower():  # Skip twitter.com
                urls.add(f"https://{match}")

        return list(urls)

    def extract_social_media(self, text: str) -> Dict[str, str]:
        """Extract social media handles"""
        social = {}

        for platform, pattern in self.social_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                social[platform] = match.group(1)

        return social

    def find_contact_indicators(self, text: str) -> List[str]:
        """Find words indicating contact information"""
        indicators = []

        for indicator in self.contact_indicators:
            if indicator in text.lower():
                indicators.append(indicator)

        return indicators

    def generate_contact_urls(self, base_url: str) -> List[str]:
        """Generate potential contact page URLs"""
        if not base_url:
            return []

        parsed = urlparse(base_url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        contact_paths = [
            '/contact',
            '/about',
            '/team',
            '/connect',
            '/reach-us',
            '/contact-us',
            '/get-in-touch',
        ]

        return [f"{base}{path}" for path in contact_paths]

    def _is_valid_email(self, email: str) -> bool:
        """Validate email address"""
        if not email or '@' not in email:
            return False

        # Basic validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def extract_from_website(self, url: str, timeout: int = 10) -> Dict:
        """
        Extract contact info from a website by visiting it

        Args:
            url: Website URL
            timeout: Request timeout in seconds

        Returns:
            Dictionary with found contacts
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            # Try the main page first
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text()

            contacts = {
                'emails': self.extract_emails(text),
                'phones': self.extract_phones(text),
                'source': 'website',
                'url': url
            }

            # If no emails found, try common contact pages
            if not contacts['emails']:
                contact_urls = self.generate_contact_urls(url)

                for contact_url in contact_urls[:3]:  # Try first 3
                    try:
                        resp = requests.get(contact_url, headers=headers, timeout=timeout)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.content, 'html.parser')
                            text = soup.get_text()

                            emails = self.extract_emails(text)
                            phones = self.extract_phones(text)

                            if emails:
                                contacts['emails'].extend(emails)
                            if phones:
                                contacts['phones'].extend(phones)

                            if emails or phones:
                                contacts['found_on'] = contact_url
                                break
                    except:
                        continue

            # Remove duplicates
            contacts['emails'] = list(set(contacts['emails']))
            contacts['phones'] = list(set(contacts['phones']))

            return contacts

        except Exception as e:
            logger.debug(f"Error extracting from website {url}: {e}")
            return {
                'emails': [],
                'phones': [],
                'error': str(e),
                'url': url
            }

    def score_contact_quality(self, contacts: Dict) -> int:
        """
        Score the quality of contact information (0-100)

        Args:
            contacts: Contact dictionary

        Returns:
            Quality score
        """
        score = 0

        # Email is most valuable
        if contacts['emails']:
            score += 50

        # Phone is also valuable
        if contacts['phones']:
            score += 20

        # Website is good
        if contacts['websites']:
            score += 15

        # Social media adds value
        score += len(contacts['social_media']) * 3

        # Contact indicators show openness
        score += len(contacts['contact_indicators']) * 2

        return min(score, 100)


# Example usage
if __name__ == "__main__":
    extractor = ContactExtractor()

    # Test cases
    test_texts = [
        "Contact me at john.doe@example.com or call +1-234-567-8900",
        "Email: hello [at] startup [dot] io | LinkedIn: linkedin.com/in/johndoe",
        "DM for business inquiries. Website: https://mysite.com",
        "Reach out: contact@company.io | (555) 123-4567",
        "📧 info@tech.com | 🌐 mywebsite.io | 💬 Telegram: @myhandle"
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {text}")
        print('='*60)

        contacts = extractor.extract_all_contacts(text)

        print(f"Emails: {contacts['emails']}")
        print(f"Phones: {contacts['phones']}")
        print(f"Websites: {contacts['websites']}")
        print(f"Social: {contacts['social_media']}")
        print(f"Indicators: {contacts['contact_indicators']}")
        print(f"Quality Score: {extractor.score_contact_quality(contacts)}/100")
