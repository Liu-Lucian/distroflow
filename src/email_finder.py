"""Email finder for lead generation"""

import re
import requests
from typing import Optional, List, Dict
from .config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailFinder:
    """Find email addresses for leads"""

    def __init__(self):
        self.hunter_api_key = config.HUNTER_API_KEY
        self.clearbit_api_key = config.CLEARBIT_API_KEY

    def extract_email_from_bio(self, bio: str, url: str = None) -> Optional[str]:
        """
        Extract email from Twitter bio or URL

        Args:
            bio: User's Twitter bio
            url: User's URL from profile

        Returns:
            Email address if found
        """
        # Email regex pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        # Search in bio
        emails = re.findall(email_pattern, bio)
        if emails:
            return emails[0]

        # Search in URL if provided
        if url:
            emails = re.findall(email_pattern, url)
            if emails:
                return emails[0]

        return None

    def guess_email_patterns(self, name: str, company_domain: str) -> List[str]:
        """
        Generate common email patterns

        Args:
            name: Person's full name
            company_domain: Company domain (e.g., 'example.com')

        Returns:
            List of possible email addresses
        """
        if not name or not company_domain:
            return []

        # Clean and split name
        name_parts = name.lower().strip().split()
        if len(name_parts) < 2:
            return []

        first_name = name_parts[0]
        last_name = name_parts[-1]

        patterns = [
            f"{first_name}.{last_name}@{company_domain}",
            f"{first_name}{last_name}@{company_domain}",
            f"{first_name}@{company_domain}",
            f"{first_name[0]}{last_name}@{company_domain}",
            f"{first_name}_{last_name}@{company_domain}",
            f"{last_name}.{first_name}@{company_domain}",
        ]

        return patterns

    def find_email_hunter(self, domain: str, first_name: str, last_name: str) -> Optional[str]:
        """
        Use Hunter.io API to find email

        Args:
            domain: Company domain
            first_name: First name
            last_name: Last name

        Returns:
            Email address if found
        """
        if not self.hunter_api_key:
            return None

        try:
            url = "https://api.hunter.io/v2/email-finder"
            params = {
                "domain": domain,
                "first_name": first_name,
                "last_name": last_name,
                "api_key": self.hunter_api_key
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("data") and data["data"].get("email"):
                    logger.info(f"Found email via Hunter: {data['data']['email']}")
                    return data["data"]["email"]

        except Exception as e:
            logger.error(f"Error using Hunter API: {e}")

        return None

    def find_email_clearbit(self, email_guess: str) -> Optional[Dict]:
        """
        Use Clearbit to verify email and get additional info

        Args:
            email_guess: Email address to verify

        Returns:
            Person info if email is valid
        """
        if not self.clearbit_api_key:
            return None

        try:
            url = f"https://person.clearbit.com/v2/people/find?email={email_guess}"
            headers = {"Authorization": f"Bearer {self.clearbit_api_key}"}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Verified email via Clearbit: {email_guess}")
                return {
                    "email": email_guess,
                    "name": data.get("name", {}).get("fullName"),
                    "title": data.get("employment", {}).get("title"),
                    "company": data.get("employment", {}).get("name"),
                    "linkedin": data.get("linkedin", {}).get("handle")
                }

        except Exception as e:
            logger.debug(f"Email not found in Clearbit: {e}")

        return None

    def extract_domain_from_url(self, url: str) -> Optional[str]:
        """
        Extract domain from URL

        Args:
            url: Full URL

        Returns:
            Domain name
        """
        if not url:
            return None

        # Simple regex to extract domain
        pattern = r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})'
        match = re.search(pattern, url)

        if match:
            return match.group(1)

        return None

    def find_email_comprehensive(self, user_data: Dict) -> Optional[str]:
        """
        Try multiple methods to find email

        Args:
            user_data: Dictionary with user information (name, bio, url, etc.)

        Returns:
            Email address if found
        """
        # Method 1: Extract from bio or URL
        bio = user_data.get('description', '')
        url = user_data.get('url', '')

        email = self.extract_email_from_bio(bio, url)
        if email:
            logger.info(f"Found email in bio: {email}")
            return email

        # Method 2: Try Hunter.io if we have domain and name
        domain = self.extract_domain_from_url(url)
        name = user_data.get('name', '')

        if domain and name:
            name_parts = name.split()
            if len(name_parts) >= 2:
                email = self.find_email_hunter(domain, name_parts[0], name_parts[-1])
                if email:
                    return email

                # Method 3: Try common patterns with Clearbit verification
                patterns = self.guess_email_patterns(name, domain)
                for pattern in patterns[:3]:  # Try first 3 patterns
                    result = self.find_email_clearbit(pattern)
                    if result:
                        return result['email']

        return None


# Example usage
if __name__ == "__main__":
    finder = EmailFinder()

    # Test data
    test_user = {
        'name': 'John Smith',
        'description': 'CEO at TechCorp. Building the future. Contact: john@techcorp.com',
        'url': 'https://techcorp.com'
    }

    email = finder.find_email_comprehensive(test_user)
    print(f"Found email: {email}")

    # Test pattern generation
    patterns = finder.guess_email_patterns('John Smith', 'example.com')
    print(f"Email patterns: {patterns}")
