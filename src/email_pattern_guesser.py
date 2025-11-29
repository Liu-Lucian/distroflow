"""
邮箱模式推断器 - Email Pattern Guesser
Like Hunter.io's pattern inference system
Guess email addresses based on company patterns
"""

import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailPatternGuesser:
    """Infer and guess email patterns for companies"""

    def __init__(self):
        """Initialize Email Pattern Guesser"""

        # Common email patterns
        self.common_patterns = [
            '{first}.{last}@{domain}',      # john.doe@company.com (most common)
            '{first}{last}@{domain}',       # johndoe@company.com
            '{f}{last}@{domain}',           # jdoe@company.com
            '{first}@{domain}',             # john@company.com
            '{last}@{domain}',              # doe@company.com
            '{first}_{last}@{domain}',      # john_doe@company.com
            '{first}-{last}@{domain}',      # john-doe@company.com
            '{last}.{first}@{domain}',      # doe.john@company.com
            '{last}{first}@{domain}',       # doejohn@company.com
            '{last}{f}@{domain}',           # doej@company.com
        ]

        # Pattern name mapping
        self.pattern_names = {
            '{first}.{last}@{domain}': 'first.last',
            '{first}{last}@{domain}': 'firstlast',
            '{f}{last}@{domain}': 'flast',
            '{first}@{domain}': 'first',
            '{last}@{domain}': 'last',
            '{first}_{last}@{domain}': 'first_last',
            '{first}-{last}@{domain}': 'first-last',
            '{last}.{first}@{domain}': 'last.first',
            '{last}{first}@{domain}': 'lastfirst',
            '{last}{f}@{domain}': 'lastf',
        }

        # Company pattern database (learned from known emails)
        self.company_patterns = {}

    def learn_pattern_from_email(self, email: str, first_name: str, last_name: str, domain: str) -> Optional[str]:
        """
        Learn email pattern from a known email

        Args:
            email: Known email address
            first_name: Person's first name
            last_name: Person's last name
            domain: Company domain

        Returns:
            Pattern string or None
        """
        if not all([email, first_name, last_name, domain]):
            return None

        # Normalize
        email = email.lower()
        first_name = first_name.lower()
        last_name = last_name.lower()
        domain = domain.lower()
        f = first_name[0] if first_name else ''

        # Check each pattern
        for pattern in self.common_patterns:
            expected = pattern.format(
                first=first_name,
                last=last_name,
                f=f,
                domain=domain
            )

            if expected == email:
                logger.info(f"  ✓ Learned pattern: {self.pattern_names.get(pattern, pattern)} for {domain}")
                return pattern

        return None

    def learn_patterns_from_emails(self, emails: List[Dict]) -> Dict[str, Dict]:
        """
        Learn patterns from a list of known emails

        Args:
            emails: List of dicts with 'email', 'first_name', 'last_name', 'domain'

        Returns:
            Dictionary of domain -> pattern distribution
        """
        domain_patterns = {}

        for email_info in emails:
            email = email_info.get('email')
            first = email_info.get('first_name')
            last = email_info.get('last_name')
            domain = email_info.get('domain')

            pattern = self.learn_pattern_from_email(email, first, last, domain)

            if pattern and domain:
                if domain not in domain_patterns:
                    domain_patterns[domain] = []
                domain_patterns[domain].append(pattern)

        # Count patterns per domain
        result = {}
        for domain, patterns in domain_patterns.items():
            pattern_counts = Counter(patterns)
            result[domain] = {
                'patterns': dict(pattern_counts),
                'most_common': pattern_counts.most_common(1)[0][0] if pattern_counts else None,
                'confidence': pattern_counts.most_common(1)[0][1] / len(patterns) if pattern_counts else 0
            }

        self.company_patterns.update(result)
        return result

    def guess_email(
        self,
        first_name: str,
        last_name: str,
        domain: str,
        known_pattern: Optional[str] = None
    ) -> List[Dict]:
        """
        Guess possible email addresses

        Args:
            first_name: Person's first name
            last_name: Person's last name
            domain: Company domain
            known_pattern: Known pattern for this domain (optional)

        Returns:
            List of possible emails with confidence scores
        """
        if not all([first_name, last_name, domain]):
            return []

        # Normalize
        first_name = first_name.lower().strip()
        last_name = last_name.lower().strip()
        domain = domain.lower().strip()
        f = first_name[0] if first_name else ''

        guesses = []

        # If we know the pattern for this domain, use it first
        if domain in self.company_patterns:
            company_info = self.company_patterns[domain]
            most_common_pattern = company_info['most_common']
            confidence = company_info['confidence']

            if most_common_pattern:
                email = most_common_pattern.format(
                    first=first_name,
                    last=last_name,
                    f=f,
                    domain=domain
                )

                guesses.append({
                    'email': email,
                    'pattern': self.pattern_names.get(most_common_pattern, most_common_pattern),
                    'confidence': int(confidence * 100),
                    'source': 'learned_pattern'
                })

        # If a specific pattern was provided
        if known_pattern and known_pattern in self.common_patterns:
            email = known_pattern.format(
                first=first_name,
                last=last_name,
                f=f,
                domain=domain
            )

            guesses.append({
                'email': email,
                'pattern': self.pattern_names.get(known_pattern, known_pattern),
                'confidence': 90,
                'source': 'provided_pattern'
            })

        # Try all common patterns (with decreasing confidence)
        pattern_confidence = {
            '{first}.{last}@{domain}': 80,  # Most common
            '{first}{last}@{domain}': 70,
            '{f}{last}@{domain}': 60,
            '{first}@{domain}': 50,
            '{first}_{last}@{domain}': 40,
            '{first}-{last}@{domain}': 40,
            '{last}.{first}@{domain}': 30,
            '{last}{first}@{domain}': 20,
            '{last}@{domain}': 20,
            '{last}{f}@{domain}': 10,
        }

        for pattern in self.common_patterns:
            email = pattern.format(
                first=first_name,
                last=last_name,
                f=f,
                domain=domain
            )

            # Skip if already added
            if any(g['email'] == email for g in guesses):
                continue

            guesses.append({
                'email': email,
                'pattern': self.pattern_names.get(pattern, pattern),
                'confidence': pattern_confidence.get(pattern, 10),
                'source': 'common_pattern'
            })

        # Sort by confidence
        guesses.sort(key=lambda x: x['confidence'], reverse=True)

        return guesses

    def extract_domain_from_website(self, website: str) -> Optional[str]:
        """
        Extract domain from website URL

        Filters out URL shorteners and social media domains that are not valid email domains.

        Args:
            website: Website URL

        Returns:
            Domain string or None if invalid
        """
        if not website:
            return None

        # Remove protocol
        domain = re.sub(r'^https?://', '', website)

        # Remove path
        domain = domain.split('/')[0]

        # Remove www.
        domain = domain.replace('www.', '')

        # Remove port
        domain = domain.split(':')[0]

        if not domain:
            return None

        # Filter out invalid domains (URL shorteners, social media)
        invalid_domains = [
            't.co',           # Twitter short links
            'twitter.com',    # Twitter
            'x.com',          # X (Twitter)
            'bit.ly',         # URL shorteners
            'tinyurl.com',
            'goo.gl',
            'ow.ly',
            'buff.ly',
            'is.gd',
            'linkedin.com',   # Social media
            'facebook.com',
            'instagram.com',
            'youtube.com',
        ]

        domain_lower = domain.lower()
        for invalid in invalid_domains:
            if domain_lower == invalid or domain_lower.endswith('.' + invalid):
                logger.debug(f"Filtered out invalid domain for email: {domain} (URL shortener/social media)")
                return None

        return domain

    def guess_company_email_from_profile(self, user_info: Dict) -> List[Dict]:
        """
        Guess company email from user profile

        Args:
            user_info: User information with name, website, etc.

        Returns:
            List of email guesses
        """
        # Extract name
        name = user_info.get('name', '')
        parts = name.split()

        if len(parts) < 2:
            logger.warning(f"Cannot guess email: name '{name}' doesn't have first and last")
            return []

        first_name = parts[0]
        last_name = parts[-1]

        # Extract domain
        website = user_info.get('website', '')
        domain = self.extract_domain_from_website(website)

        if not domain:
            logger.warning(f"Cannot guess email: no domain found in '{website}'")
            return []

        # Guess emails
        guesses = self.guess_email(first_name, last_name, domain)

        logger.info(f"  💡 Generated {len(guesses)} email guesses for {name} @ {domain}")
        for guess in guesses[:3]:
            logger.info(f"    {guess['confidence']}% - {guess['email']} ({guess['pattern']})")

        return guesses


# Example usage
if __name__ == "__main__":
    guesser = EmailPatternGuesser()

    # Scenario 1: Learn from known emails
    print("=" * 60)
    print("Scenario 1: Learning from known emails")
    print("=" * 60)

    known_emails = [
        {'email': 'john.doe@apple.com', 'first_name': 'John', 'last_name': 'Doe', 'domain': 'apple.com'},
        {'email': 'jane.smith@apple.com', 'first_name': 'Jane', 'last_name': 'Smith', 'domain': 'apple.com'},
        {'email': 'bob.jones@apple.com', 'first_name': 'Bob', 'last_name': 'Jones', 'domain': 'apple.com'},
        {'email': 'alicewang@google.com', 'first_name': 'Alice', 'last_name': 'Wang', 'domain': 'google.com'},
        {'email': 'bobchen@google.com', 'first_name': 'Bob', 'last_name': 'Chen', 'domain': 'google.com'},
    ]

    patterns = guesser.learn_patterns_from_emails(known_emails)
    print(f"\nLearned patterns:")
    for domain, info in patterns.items():
        print(f"  {domain}:")
        print(f"    Most common: {info['most_common']}")
        print(f"    Confidence: {info['confidence'] * 100:.0f}%")

    # Scenario 2: Guess emails for new people
    print("\n" + "=" * 60)
    print("Scenario 2: Guessing emails for new people")
    print("=" * 60)

    # Apple (we learned the pattern)
    guesses = guesser.guess_email('Tim', 'Cook', 'apple.com')
    print(f"\nGuesses for Tim Cook @ Apple:")
    for guess in guesses[:5]:
        print(f"  {guess['confidence']:3d}% - {guess['email']} ({guess['pattern']}) [{guess['source']}]")

    # Google (we learned the pattern)
    guesses = guesser.guess_email('Sundar', 'Pichai', 'google.com')
    print(f"\nGuesses for Sundar Pichai @ Google:")
    for guess in guesses[:5]:
        print(f"  {guess['confidence']:3d}% - {guess['email']} ({guess['pattern']}) [{guess['source']}]")

    # Unknown company (use common patterns)
    guesses = guesser.guess_email('John', 'Smith', 'startup.io')
    print(f"\nGuesses for John Smith @ startup.io (unknown company):")
    for guess in guesses[:5]:
        print(f"  {guess['confidence']:3d}% - {guess['email']} ({guess['pattern']}) [{guess['source']}]")

    # Scenario 3: Guess from user profile
    print("\n" + "=" * 60)
    print("Scenario 3: Guessing from user profile")
    print("=" * 60)

    user_profile = {
        'name': 'Elon Musk',
        'website': 'https://www.tesla.com',
        'bio': 'CEO of Tesla and SpaceX'
    }

    guesses = guesser.guess_company_email_from_profile(user_profile)
    print(f"\nGuesses for profile:")
    for guess in guesses[:5]:
        print(f"  {guess['confidence']:3d}% - {guess['email']}")
