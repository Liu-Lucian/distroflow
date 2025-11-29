"""
终极邮箱发现系统 - 集成Hunter.io版
使用Hunter.io API替代弱势功能：
1. Email Finder - 替代LLM邮箱推断（更准确）
2. Email Verifier - 替代dnspython验证（更可靠）
"""

import os
import logging
from typing import Dict
from dotenv import load_dotenv

# Import base class
from ultimate_email_finder import UltimateEmailFinder
from hunter_io_client import HunterIOClient

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class UltimateEmailFinderWithHunter(UltimateEmailFinder):
    """
    Enhanced email finder with Hunter.io integration

    Improvements:
    1. Use Hunter.io Email Finder instead of LLM inference (more accurate)
    2. Use Hunter.io Email Verifier instead of dnspython (more reliable)
    """

    def __init__(self, auth_file: str = "auth.json", output_dir: str = "ultimate_leads",
                 enable_email_verification: bool = True, smtp_timeout: int = 10,
                 hunter_api_key: str = None):
        """
        Initialize with Hunter.io integration

        Args:
            auth_file: Twitter auth file
            output_dir: Output directory
            enable_email_verification: Use Hunter.io for verification
            smtp_timeout: Timeout (not used with Hunter.io)
            hunter_api_key: Hunter.io API key (defaults to env var)
        """
        super().__init__(
            auth_file=auth_file,
            output_dir=output_dir,
            enable_email_verification=False,  # Disable default verifier
            smtp_timeout=smtp_timeout
        )

        # Initialize Hunter.io
        # Try multiple sources for API key
        api_key = hunter_api_key or os.getenv('HUNTER_API_KEY') or '1553249bbb256b2a3d111c9c67755c2927053828'
        if api_key and api_key != '':
            self.hunter = HunterIOClient(api_key=api_key)
            self.use_hunter = True
            logger.info("✅ Hunter.io integration enabled")

            # Check account
            try:
                account = self.hunter.get_account_info()
                if account:
                    logger.info(f"   📊 Hunter.io Account: {account.get('email')}")
                    logger.info(f"      Plan: {account.get('plan_name', 'Free')}")
            except:
                logger.warning("   ⚠️  Could not fetch Hunter.io account info")
        else:
            self.hunter = None
            self.use_hunter = False
            logger.warning("⚠️  No Hunter.io API key found, using fallback methods")

    def run(self, product_doc: str, followers_per: int = 100, max_seeds: int = 10):
        """Run enhanced email finding pipeline with Hunter.io"""
        logger.info("🚀 Ultimate Email Finder (Hunter.io Enhanced) Starting...")

        # Call parent run method but we'll override specific steps
        return super().run(product_doc, followers_per, max_seeds)

    def _is_valid_email_domain(self, email: str) -> bool:
        """
        Check if email domain is valid (not t.co, twitter.com, etc)

        Args:
            email: Email address to check

        Returns:
            True if valid domain, False otherwise
        """
        if not email or '@' not in email:
            return False

        domain = email.split('@')[1].lower()

        # Blacklist of invalid domains
        invalid_domains = [
            't.co',           # Twitter short links
            'twitter.com',    # Twitter itself
            'x.com',          # X (Twitter)
            'bit.ly',         # URL shortener
            'tinyurl.com',    # URL shortener
            'goo.gl',         # URL shortener
            'ow.ly',          # URL shortener
        ]

        for invalid in invalid_domains:
            if domain == invalid or domain.endswith('.' + invalid):
                logger.info(f"      ❌ Filtered out invalid domain: {email} (domain: {domain})")
                return False

        return True

    def _find_email_with_hunter(self, follower: Dict) -> str:
        """
        Use Hunter.io Email Finder instead of LLM inference

        This is MORE ACCURATE than LLM because:
        - Hunter has a database of verified emails
        - Knows actual email patterns for companies
        - Returns confidence scores based on real data

        Args:
            follower: Twitter follower data

        Returns:
            Email address or None
        """
        if not self.use_hunter:
            return None

        name = follower.get('name', '')
        website = follower.get('website', '')

        if not name or not website:
            return None

        # Extract domain from website
        from urllib.parse import urlparse
        try:
            parsed = urlparse(website)
            domain = parsed.netloc or parsed.path
            domain = domain.replace('www.', '')

            # Skip social media domains
            skip_domains = ['twitter.com', 'x.com', 'linkedin.com', 'facebook.com', 't.co']
            if any(skip in domain for skip in skip_domains):
                logger.debug(f"      ⚠️  Skipping social media domain: {domain}")
                return None

        except:
            return None

        # Split name into first/last
        name_parts = name.split()
        if len(name_parts) < 2:
            # Use full name
            first_name = name
            last_name = ''
        else:
            first_name = name_parts[0]
            last_name = name_parts[-1]

        # Call Hunter.io Email Finder
        logger.info(f"    🔍 Hunter.io: Finding email for {name} @ {domain}...")
        result = self.hunter.find_email(
            domain=domain,
            first_name=first_name if last_name else None,
            last_name=last_name if last_name else None,
            full_name=name if not last_name else None
        )

        if result and result.get('email'):
            email = result['email']
            score = result.get('score', 0)

            # Only accept high confidence emails
            if score >= 50:  # Hunter.io score is 0-100
                follower['email_source'] = f'hunter_finder (score: {score})'
                logger.info(f"      ✅ Hunter.io found: {email} (confidence: {score}%)")
                return email
            else:
                logger.info(f"      ⚠️  Hunter.io found {email} but low confidence ({score}%), skipping")
                return None

        return None

    def _verify_email_with_hunter(self, email: str) -> Dict:
        """
        Use Hunter.io Email Verifier instead of dnspython

        This is MORE RELIABLE than dnspython because:
        - Checks SMTP deliverability (not just DNS)
        - Has database of known valid/invalid emails
        - Returns detailed status (valid/invalid/accept_all/disposable)

        Args:
            email: Email address to verify

        Returns:
            Verification result dict
        """
        if not self.use_hunter:
            return {'status': 'unknown', 'confidence': 50}

        result = self.hunter.verify_email(email)

        if not result:
            return {'status': 'unknown', 'confidence': 50}

        # Map Hunter.io status to our format
        status = result.get('status', 'unknown')
        score = result.get('score', 50)

        # Hunter.io status: valid, invalid, accept_all, webmail, disposable, unknown
        confidence_map = {
            'valid': score,
            'invalid': 0,
            'accept_all': 40,  # Lower confidence for catch-all domains
            'webmail': score,
            'disposable': 0,  # Filter out disposable
            'unknown': 50
        }

        confidence = confidence_map.get(status, 50)

        return {
            'status': status,
            'confidence': confidence,
            'smtp_check': result.get('smtp_check', False),
            'mx_records': result.get('mx_records', False),
            'is_disposable': status == 'disposable'
        }

    def _verify_all_emails(self):
        """
        Override parent method to use Hunter.io Email Verifier
        """
        if not self.use_hunter:
            # Fall back to parent method
            return super()._verify_all_emails()

        # Collect all unique emails
        all_emails = []
        for lead in self.all_leads:
            emails = lead.get('all_contacts', {}).get('emails', [])
            all_emails.extend(emails)

        if not all_emails:
            logger.info("  No emails to verify")
            return

        unique_emails = list(set(all_emails))
        logger.info(f"\n🔍 Verifying {len(unique_emails)} emails with Hunter.io...")

        # Verify each email with Hunter.io
        verification_map = {}
        for email in unique_emails:
            logger.info(f"  🔍 Verifying: {email}")
            result = self._verify_email_with_hunter(email)
            verification_map[email.lower()] = result

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
                # First, filter out invalid domains (t.co, etc)
                if not self._is_valid_email_domain(email):
                    invalid_count += 1
                    continue

                # Then verify with Hunter.io
                result = verification_map.get(email.lower())
                if result:
                    # Store verification result
                    if 'email_verification' not in lead:
                        lead['email_verification'] = {}

                    lead['email_verification'][email] = {
                        'status': result.get('status'),
                        'confidence': result.get('confidence'),
                        'smtp_check': result.get('smtp_check', False),
                        'mx_records': result.get('mx_records', False),
                        'is_disposable': result.get('is_disposable', False)
                    }

                    # Filter logic
                    status = result.get('status')
                    confidence = result.get('confidence', 0)

                    # Keep valid and high-confidence emails
                    if status == 'valid' or (status == 'webmail' and confidence >= 70) or \
                       (status == 'unknown' and confidence >= 60):
                        verified_emails.append(email)
                        if status == 'valid':
                            verified_count += 1
                        else:
                            unknown_count += 1
                    # Filter out invalid, disposable, and low-confidence
                    elif status in ['invalid', 'disposable'] or confidence < 40:
                        invalid_count += 1
                        logger.info(f"  ❌ Filtered out: {email} (status: {status}, confidence: {confidence}%)")
                    # Keep accept_all with warning
                    else:
                        verified_emails.append(email)
                        unknown_count += 1
                        logger.info(f"  ⚠️  Kept with warning: {email} (status: {status})")
                else:
                    # No verification result, keep email
                    verified_emails.append(email)
                    unknown_count += 1

            # Update lead with verified emails
            lead['all_contacts']['emails'] = verified_emails
            lead['all_contacts']['emails_verified'] = len(verified_emails)

        logger.info(f"\n  📊 Verification Summary (Hunter.io):")
        logger.info(f"     ✅ Valid: {verified_count}")
        logger.info(f"     ❓ Unknown/Warning: {unknown_count}")
        logger.info(f"     ❌ Filtered out: {invalid_count}")


# Override specific methods in parent class to use Hunter.io
# This is done by monkey-patching the parent's _llm_finder step

original_run = UltimateEmailFinder.run

def enhanced_run(self, product_doc: str, followers_per: int = 100, max_seeds: int = 10):
    """Enhanced run that uses Hunter.io for email finding"""

    # If this instance has Hunter.io, override the LLM step
    if hasattr(self, 'hunter') and self.hunter:
        # Store original LLM finder
        original_llm_finder = self.llm_finder

        # Create a wrapper that tries Hunter.io first
        class HunterFirstFinder:
            def __init__(self, hunter_client, original_finder, parent_instance):
                self.hunter = hunter_client
                self.original = original_finder
                self.parent = parent_instance

            def analyze_profile_for_contacts(self, profile):
                # Try Hunter.io first
                email = self.parent._find_email_with_hunter(profile)
                if email:
                    return {
                        'possible_emails': [{
                            'email': email,
                            'confidence': 90  # High confidence from Hunter.io
                        }]
                    }

                # Fall back to LLM
                return self.original.analyze_profile_for_contacts(profile)

        # Replace LLM finder temporarily
        self.llm_finder = HunterFirstFinder(self.hunter, original_llm_finder, self)

    # Call original run
    return original_run(self, product_doc, followers_per, max_seeds)

# Apply the enhancement
UltimateEmailFinderWithHunter.run = enhanced_run


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ultimate_email_finder_hunter.py <product_doc> [followers] [seeds]")
        print("\nExample:")
        print("  python ultimate_email_finder_hunter.py products/hiremeai.md 50 3")
        sys.exit(1)

    # Create enhanced finder with Hunter.io
    finder = UltimateEmailFinderWithHunter(
        auth_file="/Users/l.u.c/my-app/MarketingMind AI/auth.json",
        enable_email_verification=True  # Will use Hunter.io
    )

    finder.run(
        product_doc=sys.argv[1],
        followers_per=int(sys.argv[2]) if len(sys.argv) > 2 else 50,
        max_seeds=int(sys.argv[3]) if len(sys.argv) > 3 else 3
    )
