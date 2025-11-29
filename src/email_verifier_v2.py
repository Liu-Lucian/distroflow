"""
Enhanced Email Verifier - Hunter.io Style
Multi-layer email verification system with:
1. Syntax validation
2. DNS MX record checking
3. SMTP verification
4. Disposable email filtering
5. Confidence scoring
"""

import re
import smtplib
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    logging.warning("dnspython not installed. DNS checking disabled. Install: pip install dnspython")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EmailVerificationResult:
    """Email verification result"""
    email: str
    status: str  # 'valid', 'invalid', 'unknown'
    confidence_score: int  # 0-100
    checks: Dict[str, bool]
    details: Dict[str, str]
    mx_servers: List[str]
    is_disposable: bool
    is_free_provider: bool


class EmailVerifierV2:
    """Enhanced email verifier with Hunter.io-style multi-layer validation"""

    def __init__(self, enable_smtp: bool = True, timeout: int = 10):
        """
        Initialize email verifier

        Args:
            enable_smtp: Enable SMTP verification (slower but more accurate)
            timeout: Timeout for SMTP/DNS operations in seconds
        """
        self.enable_smtp = enable_smtp
        self.timeout = timeout

        # Disposable email domains (common ones, can be expanded)
        self.disposable_domains = {
            'temp-mail.org', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email', 'tempmail.com',
            'maildrop.cc', 'getnada.com', 'trashmail.com',
            'yopmail.com', 'fakeinbox.com', 'sharklasers.com',
            'guerrillamail.biz', 'guerrillamail.com', 'guerrillamail.de',
            'guerrillamail.net', 'guerrillamail.org', 'spam4.me',
            'grr.la', 'tmpeml.info', 'emailondeck.com'
        }

        # Free email providers (lower confidence for B2B)
        self.free_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'mail.com', 'protonmail.com',
            'zoho.com', 'yandex.com', 'gmx.com', 'mail.ru'
        }

        # Cache for DNS lookups (avoid repeated queries)
        self._dns_cache = {}
        self._smtp_cache = {}

    def verify_email(self, email: str) -> EmailVerificationResult:
        """
        Comprehensive email verification

        Args:
            email: Email address to verify

        Returns:
            EmailVerificationResult with status and details
        """
        email = email.lower().strip()

        checks = {
            'syntax_valid': False,
            'dns_valid': False,
            'smtp_valid': False,
            'not_disposable': True,
        }

        details = {}
        mx_servers = []

        # Step 1: Syntax validation
        syntax_valid, syntax_msg = self._validate_syntax(email)
        checks['syntax_valid'] = syntax_valid
        details['syntax'] = syntax_msg

        if not syntax_valid:
            return EmailVerificationResult(
                email=email,
                status='invalid',
                confidence_score=0,
                checks=checks,
                details=details,
                mx_servers=[],
                is_disposable=False,
                is_free_provider=False
            )

        domain = email.split('@')[1]

        # Step 2: Check if disposable
        is_disposable = domain in self.disposable_domains
        checks['not_disposable'] = not is_disposable

        if is_disposable:
            details['disposable'] = f"Disposable email domain: {domain}"
            return EmailVerificationResult(
                email=email,
                status='invalid',
                confidence_score=10,
                checks=checks,
                details=details,
                mx_servers=[],
                is_disposable=True,
                is_free_provider=False
            )

        # Step 3: DNS MX record check
        if DNS_AVAILABLE:
            dns_valid, mx_servers, dns_msg = self._check_dns_mx(domain)
            checks['dns_valid'] = dns_valid
            details['dns'] = dns_msg

            if not dns_valid:
                return EmailVerificationResult(
                    email=email,
                    status='invalid',
                    confidence_score=15,
                    checks=checks,
                    details=details,
                    mx_servers=[],
                    is_disposable=False,
                    is_free_provider=domain in self.free_providers
                )
        else:
            details['dns'] = 'DNS checking disabled (dnspython not installed)'
            dns_valid = True  # Assume valid if can't check

        # Step 4: SMTP verification
        smtp_valid = False
        if self.enable_smtp and mx_servers:
            smtp_valid, smtp_msg = self._verify_smtp(email, mx_servers[0])
            checks['smtp_valid'] = smtp_valid
            details['smtp'] = smtp_msg
        else:
            details['smtp'] = 'SMTP verification disabled or no MX servers'

        # Step 5: Calculate status and confidence
        is_free = domain in self.free_providers
        status, confidence = self._calculate_status_and_confidence(checks, is_free, smtp_valid)

        return EmailVerificationResult(
            email=email,
            status=status,
            confidence_score=confidence,
            checks=checks,
            details=details,
            mx_servers=mx_servers,
            is_disposable=False,
            is_free_provider=is_free
        )

    def verify_emails_batch(self, emails: List[str], max_workers: int = 5) -> List[EmailVerificationResult]:
        """
        Verify multiple emails in parallel

        Args:
            emails: List of email addresses
            max_workers: Number of parallel workers

        Returns:
            List of EmailVerificationResult
        """
        results = []

        # Remove duplicates
        unique_emails = list(set(email.lower().strip() for email in emails if email))

        logger.info(f"Verifying {len(unique_emails)} unique emails...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.verify_email, unique_emails))

        return results

    def _validate_syntax(self, email: str) -> Tuple[bool, str]:
        """Validate email syntax according to RFC 5322"""
        # Basic regex for email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False, "Invalid email format"

        # Additional checks
        local, domain = email.split('@')

        # Check local part
        if len(local) > 64:
            return False, "Local part too long (max 64 chars)"

        if local.startswith('.') or local.endswith('.'):
            return False, "Local part cannot start/end with dot"

        if '..' in local:
            return False, "Local part cannot contain consecutive dots"

        # Check domain
        if len(domain) > 255:
            return False, "Domain too long (max 255 chars)"

        if domain.startswith('-') or domain.endswith('-'):
            return False, "Domain cannot start/end with hyphen"

        # Check TLD
        tld = domain.split('.')[-1]
        if len(tld) < 2:
            return False, "Invalid TLD"

        return True, "Valid syntax"

    def _check_dns_mx(self, domain: str) -> Tuple[bool, List[str], str]:
        """Check DNS MX records for domain"""
        # Check cache first
        if domain in self._dns_cache:
            return self._dns_cache[domain]

        try:
            # Query MX records
            mx_records = dns.resolver.resolve(domain, 'MX', lifetime=self.timeout)

            # Sort by priority (lower is better)
            mx_list = sorted(
                [(r.preference, str(r.exchange).rstrip('.')) for r in mx_records],
                key=lambda x: x[0]
            )

            mx_servers = [mx[1] for mx in mx_list]

            if mx_servers:
                result = (True, mx_servers, f"Found {len(mx_servers)} MX server(s)")
                self._dns_cache[domain] = result
                return result
            else:
                result = (False, [], "No MX records found")
                self._dns_cache[domain] = result
                return result

        except dns.resolver.NXDOMAIN:
            result = (False, [], "Domain does not exist")
            self._dns_cache[domain] = result
            return result
        except dns.resolver.NoAnswer:
            result = (False, [], "No MX records found")
            self._dns_cache[domain] = result
            return result
        except dns.resolver.Timeout:
            return (False, [], "DNS query timeout")
        except Exception as e:
            return (False, [], f"DNS error: {str(e)}")

    def _verify_smtp(self, email: str, mx_server: str) -> Tuple[bool, str]:
        """Verify email via SMTP handshake"""
        # Check cache first
        cache_key = f"{email}:{mx_server}"
        if cache_key in self._smtp_cache:
            return self._smtp_cache[cache_key]

        try:
            # Connect to mail server
            server = smtplib.SMTP(timeout=self.timeout)
            server.connect(mx_server, 25)

            # EHLO
            server.ehlo('verify.local')

            # Try MAIL FROM
            server.mail('verify@verify.local')

            # Try RCPT TO (this checks if email exists)
            code, message = server.rcpt(email)

            server.quit()

            # 250 = OK, 251 = User not local (but will forward)
            if code in [250, 251]:
                result = (True, f"Email verified (SMTP code {code})")
                self._smtp_cache[cache_key] = result
                return result
            else:
                result = (False, f"Email rejected (SMTP code {code})")
                self._smtp_cache[cache_key] = result
                return result

        except smtplib.SMTPServerDisconnected:
            return (False, "Server disconnected")
        except smtplib.SMTPConnectError:
            return (False, "Cannot connect to mail server")
        except smtplib.SMTPRecipientsRefused:
            result = (False, "Email rejected by server")
            self._smtp_cache[cache_key] = result
            return result
        except Exception as e:
            # Many servers block SMTP verification, return unknown
            return (False, f"SMTP check failed: {str(e)[:50]}")

    def _calculate_status_and_confidence(
        self,
        checks: Dict[str, bool],
        is_free: bool,
        smtp_valid: bool
    ) -> Tuple[str, int]:
        """Calculate overall status and confidence score"""

        # Base confidence from checks
        confidence = 0

        # Syntax valid: +30
        if checks['syntax_valid']:
            confidence += 30

        # DNS valid: +30
        if checks['dns_valid']:
            confidence += 30

        # SMTP valid: +30
        if smtp_valid:
            confidence += 30

        # Not disposable: +10
        if checks['not_disposable']:
            confidence += 10

        # Penalties
        # Free provider: -15 (less reliable for B2B)
        if is_free:
            confidence -= 15

        # Cap at 0-100
        confidence = max(0, min(100, confidence))

        # Determine status
        if not checks['syntax_valid'] or not checks['not_disposable']:
            status = 'invalid'
        elif not checks['dns_valid']:
            status = 'invalid'
        elif smtp_valid:
            status = 'valid'
        elif checks['dns_valid'] and not smtp_valid:
            # DNS valid but SMTP failed/unavailable
            if confidence >= 50:
                status = 'unknown'  # Likely valid but can't confirm
            else:
                status = 'invalid'
        else:
            status = 'unknown'

        return status, confidence

    def print_verification_result(self, result: EmailVerificationResult):
        """Print formatted verification result"""
        status_emoji = {
            'valid': '✅',
            'invalid': '❌',
            'unknown': '❓'
        }

        print(f"\n{status_emoji.get(result.status, '❓')} {result.email}")
        print(f"   Status: {result.status.upper()}")
        print(f"   Confidence: {result.confidence_score}%")

        if result.is_disposable:
            print(f"   ⚠️  Disposable email")

        if result.is_free_provider:
            print(f"   ℹ️  Free email provider")

        if result.mx_servers:
            print(f"   MX: {result.mx_servers[0]}")

        print(f"   Checks:")
        for check, passed in result.checks.items():
            symbol = '✓' if passed else '✗'
            print(f"     {symbol} {check}")


if __name__ == "__main__":
    # Test the verifier
    verifier = EmailVerifierV2(enable_smtp=True, timeout=10)

    test_emails = [
        "test@gmail.com",
        "invalid@@@domain.com",
        "test@temp-mail.org",
        "john.doe@stripe.com",
        "contact@anthropic.com",
    ]

    print("🔍 Email Verifier Test\n")
    print("="*60)

    for email in test_emails:
        result = verifier.verify_email(email)
        verifier.print_verification_result(result)

    print("\n" + "="*60)
    print("\n🔄 Batch Verification Test\n")

    results = verifier.verify_emails_batch(test_emails, max_workers=3)

    # Summary
    valid = sum(1 for r in results if r.status == 'valid')
    invalid = sum(1 for r in results if r.status == 'invalid')
    unknown = sum(1 for r in results if r.status == 'unknown')

    print(f"\nSummary:")
    print(f"  ✅ Valid: {valid}")
    print(f"  ❌ Invalid: {invalid}")
    print(f"  ❓ Unknown: {unknown}")
    print(f"  📊 Total: {len(results)}")
