"""
邮箱验证器 - Email Verifier
SMTP-based email verification without sending emails
Like Hunter.io's verification system
"""

import re
import socket
import smtplib
import dns.resolver
import logging
from typing import Dict, Optional, List
from email.utils import parseaddr

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailVerifier:
    """Verify email addresses using SMTP"""

    def __init__(self, timeout: int = 10):
        """
        Initialize Email Verifier

        Args:
            timeout: SMTP connection timeout in seconds
        """
        self.timeout = timeout

        # Common disposable email domains
        self.disposable_domains = {
            'tempmail.com', 'guerrillamail.com', '10minutemail.com',
            'mailinator.com', 'throwaway.email', 'temp-mail.org',
            'fakeinbox.com', 'yopmail.com', 'maildrop.cc'
        }

        # Common free email providers (lower deliverability for B2B)
        self.free_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
        }

    def validate_format(self, email: str) -> bool:
        """
        Validate email format (RFC 5322)

        Args:
            email: Email address

        Returns:
            True if format is valid
        """
        if not email:
            return False

        # Basic regex validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(pattern, email):
            return False

        # Parse address
        name, addr = parseaddr(email)

        if not addr:
            return False

        # Check for valid domain
        parts = addr.split('@')
        if len(parts) != 2:
            return False

        local, domain = parts

        # Local part checks
        if len(local) == 0 or len(local) > 64:
            return False

        # Domain part checks
        if len(domain) == 0 or len(domain) > 255:
            return False

        return True

    def check_mx_records(self, domain: str) -> Optional[List[str]]:
        """
        Check if domain has valid MX records

        Args:
            domain: Email domain

        Returns:
            List of MX servers or None
        """
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_servers = [str(r.exchange).rstrip('.') for r in mx_records]
            return mx_servers if mx_servers else None
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
            logger.debug(f"No MX records found for {domain}")
            return None
        except Exception as e:
            logger.debug(f"Error checking MX for {domain}: {e}")
            return None

    def verify_smtp(self, email: str, mx_server: str) -> Dict:
        """
        Verify email via SMTP handshake (without sending)

        Args:
            email: Email address to verify
            mx_server: MX server to connect to

        Returns:
            Dictionary with verification result
        """
        result = {
            'email': email,
            'deliverable': False,
            'smtp_check': False,
            'error': None
        }

        try:
            # Get local hostname
            local_hostname = socket.gethostname()
            from_email = f'verify@{local_hostname}'

            # Connect to SMTP server
            with smtplib.SMTP(timeout=self.timeout) as smtp:
                smtp.connect(mx_server, 25)

                # EHLO
                smtp.ehlo(local_hostname)

                # MAIL FROM
                smtp.mail(from_email)

                # RCPT TO (this is where we check if email exists)
                code, message = smtp.rcpt(email)

                # 250 = success, email exists
                # 550 = mailbox unavailable / doesn't exist
                # 451/452 = temporary failure
                # 553 = mailbox name not allowed

                if code == 250:
                    result['deliverable'] = True
                    result['smtp_check'] = True
                elif code in [550, 551, 553]:
                    result['deliverable'] = False
                    result['smtp_check'] = True
                    result['error'] = f"Mailbox not found (code {code})"
                else:
                    result['smtp_check'] = True
                    result['error'] = f"Uncertain (code {code}): {message.decode()}"

                # Important: QUIT without actually sending
                smtp.quit()

        except smtplib.SMTPServerDisconnected:
            result['error'] = 'Server disconnected'
        except smtplib.SMTPConnectError:
            result['error'] = 'Could not connect to SMTP server'
        except socket.timeout:
            result['error'] = 'SMTP connection timeout'
        except Exception as e:
            result['error'] = f'SMTP error: {str(e)}'

        return result

    def verify_email(self, email: str) -> Dict:
        """
        Comprehensive email verification

        Args:
            email: Email address to verify

        Returns:
            Dictionary with detailed verification results
        """
        result = {
            'email': email,
            'valid_format': False,
            'domain_exists': False,
            'mx_records': [],
            'smtp_verified': False,
            'deliverable': False,
            'is_disposable': False,
            'is_free_provider': False,
            'confidence_score': 0,
            'status': 'invalid',
            'error': None
        }

        # Step 1: Format validation
        result['valid_format'] = self.validate_format(email)
        if not result['valid_format']:
            result['status'] = 'invalid_format'
            result['error'] = 'Invalid email format'
            return result

        # Extract domain
        domain = email.split('@')[1].lower()

        # Check if disposable
        result['is_disposable'] = domain in self.disposable_domains
        if result['is_disposable']:
            result['status'] = 'disposable'
            result['confidence_score'] = 0
            return result

        # Check if free provider
        result['is_free_provider'] = domain in self.free_providers

        # Step 2: Check MX records
        mx_servers = self.check_mx_records(domain)
        if mx_servers:
            result['domain_exists'] = True
            result['mx_records'] = mx_servers
        else:
            result['status'] = 'no_mx_records'
            result['error'] = 'Domain has no MX records'
            result['confidence_score'] = 0
            return result

        # Step 3: SMTP verification (try first MX server)
        if mx_servers:
            smtp_result = self.verify_smtp(email, mx_servers[0])
            result['smtp_verified'] = smtp_result['smtp_check']
            result['deliverable'] = smtp_result['deliverable']

            if smtp_result['error']:
                result['error'] = smtp_result['error']

        # Calculate confidence score
        if result['deliverable']:
            result['confidence_score'] = 95
            result['status'] = 'deliverable'
        elif result['smtp_verified']:
            result['confidence_score'] = 50
            result['status'] = 'undeliverable'
        elif result['domain_exists']:
            result['confidence_score'] = 30
            result['status'] = 'unknown'
        else:
            result['confidence_score'] = 0
            result['status'] = 'invalid'

        # Reduce score for free providers (less valuable for B2B)
        if result['is_free_provider']:
            result['confidence_score'] = int(result['confidence_score'] * 0.8)

        return result

    def verify_batch(self, emails: List[str], max_workers: int = 5) -> List[Dict]:
        """
        Verify multiple emails (with threading for speed)

        Args:
            emails: List of email addresses
            max_workers: Maximum concurrent verifications

        Returns:
            List of verification results
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_email = {executor.submit(self.verify_email, email): email for email in emails}

            for future in as_completed(future_to_email):
                email = future_to_email[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"  ✓ Verified {email}: {result['status']} ({result['confidence_score']}%)")
                except Exception as e:
                    logger.error(f"  ❌ Error verifying {email}: {e}")
                    results.append({
                        'email': email,
                        'status': 'error',
                        'confidence_score': 0,
                        'error': str(e)
                    })

        return results

    def classify_email_quality(self, verification_result: Dict) -> str:
        """
        Classify email quality based on verification

        Args:
            verification_result: Result from verify_email()

        Returns:
            Quality classification string
        """
        score = verification_result['confidence_score']

        if score >= 90:
            return 'high_quality'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'medium'
        elif score >= 30:
            return 'low'
        else:
            return 'invalid'


# Example usage
if __name__ == "__main__":
    verifier = EmailVerifier()

    print("=" * 60)
    print("Email Verification Tests")
    print("=" * 60)

    test_emails = [
        'john@apple.com',           # Real company
        'test@gmail.com',           # Free provider
        'fake@invaliddomain.xyz',   # Invalid domain
        'hello@tempmail.com',       # Disposable
        'invalid-email',            # Invalid format
    ]

    for email in test_emails:
        print(f"\n📧 Verifying: {email}")
        result = verifier.verify_email(email)

        print(f"  Status: {result['status']}")
        print(f"  Confidence: {result['confidence_score']}%")
        print(f"  Deliverable: {result['deliverable']}")
        print(f"  Format Valid: {result['valid_format']}")
        print(f"  MX Records: {len(result['mx_records'])} found")
        print(f"  SMTP Verified: {result['smtp_verified']}")
        print(f"  Free Provider: {result['is_free_provider']}")
        print(f"  Disposable: {result['is_disposable']}")
        print(f"  Quality: {verifier.classify_email_quality(result)}")

        if result['error']:
            print(f"  Error: {result['error']}")

    # Batch verification example
    print("\n" + "=" * 60)
    print("Batch Verification")
    print("=" * 60)

    batch_emails = ['test1@gmail.com', 'test2@yahoo.com', 'test3@outlook.com']
    batch_results = verifier.verify_batch(batch_emails, max_workers=3)

    print(f"\nVerified {len(batch_results)} emails:")
    for result in batch_results:
        print(f"  {result['email']}: {result['status']} ({result['confidence_score']}%)")
