"""
Hunter.io API Client
专业的邮箱查找和验证服务

功能：
1. Email Verifier - 验证邮箱有效性（比dnspython更准确）
2. Email Finder - 从姓名+域名查找邮箱（比LLM推断更准确）
3. Domain Search - 查找公司所有邮箱
"""

import requests
import logging
import time
from typing import Dict, List, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class HunterIOClient:
    """Hunter.io API Client"""

    def __init__(self, api_key: str):
        """
        Initialize Hunter.io client

        Args:
            api_key: Your Hunter.io API key
        """
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
        self.session = requests.Session()

        # Rate limits
        self.verifier_rate_limit = 10  # requests per second
        self.finder_rate_limit = 15    # requests per second
        self.last_request_time = 0

    def _wait_for_rate_limit(self, endpoint_type: str = "verifier"):
        """Wait to respect rate limits"""
        rate_limit = self.verifier_rate_limit if endpoint_type == "verifier" else self.finder_rate_limit
        min_interval = 1.0 / rate_limit

        elapsed = time.time() - self.last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self.last_request_time = time.time()

    def verify_email(self, email: str) -> Dict:
        """
        Verify email deliverability using Hunter.io Email Verifier

        Args:
            email: Email address to verify

        Returns:
            {
                'email': str,
                'status': 'valid'|'invalid'|'accept_all'|'webmail'|'disposable'|'unknown',
                'score': int (0-100),
                'smtp_check': bool,
                'mx_records': bool,
                'sources': list
            }
        """
        self._wait_for_rate_limit("verifier")

        url = f"{self.base_url}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }

        try:
            response = self.session.get(url, params=params, timeout=25)

            # Handle 202 (verification pending)
            if response.status_code == 202:
                logger.info(f"   Hunter.io verification pending for {email}, retrying...")
                time.sleep(2)
                response = self.session.get(url, params=params, timeout=25)

            response.raise_for_status()
            data = response.json()

            if 'data' in data:
                result = data['data']
                logger.info(f"   ✅ Hunter.io verified: {email} - {result.get('status')} (score: {result.get('score')})")
                return result
            else:
                logger.error(f"   ❌ Hunter.io API error: {data.get('errors', 'Unknown error')}")
                return None

        except requests.exceptions.Timeout:
            logger.warning(f"   ⚠️  Hunter.io timeout for {email}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Hunter.io request failed for {email}: {e}")
            return None
        except Exception as e:
            logger.error(f"   ❌ Hunter.io unexpected error for {email}: {e}")
            return None

    def find_email(self, domain: str, first_name: str = None, last_name: str = None,
                   full_name: str = None, company: str = None) -> Dict:
        """
        Find email address using Hunter.io Email Finder

        Args:
            domain: Company domain (e.g., "salesforce.com")
            first_name: Person's first name
            last_name: Person's last name
            full_name: Full name (alternative to first/last)
            company: Company name (alternative to domain)

        Returns:
            {
                'email': str,
                'score': int (0-100),
                'first_name': str,
                'last_name': str,
                'position': str,
                'sources': list,
                'verification': dict
            }
        """
        self._wait_for_rate_limit("finder")

        url = f"{self.base_url}/email-finder"
        params = {'api_key': self.api_key}

        # Add required parameters
        if domain:
            params['domain'] = domain
        elif company:
            params['company'] = company
        else:
            logger.error("   ❌ Either domain or company must be provided")
            return None

        # Add name parameters
        if full_name:
            params['full_name'] = full_name
        elif first_name and last_name:
            params['first_name'] = first_name
            params['last_name'] = last_name
        else:
            logger.error("   ❌ Either full_name or first_name+last_name must be provided")
            return None

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'data' in data:
                result = data['data']
                if result.get('email'):
                    logger.info(f"   ✅ Hunter.io found: {result['email']} (score: {result.get('score')})")
                    return result
                else:
                    logger.warning(f"   ⚠️  Hunter.io: No email found for {full_name or f'{first_name} {last_name}'} @ {domain or company}")
                    return None
            else:
                logger.error(f"   ❌ Hunter.io API error: {data.get('errors', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Hunter.io request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"   ❌ Hunter.io unexpected error: {e}")
            return None

    def domain_search(self, domain: str = None, company: str = None,
                     limit: int = 10, offset: int = 0,
                     email_type: str = None, seniority: str = None,
                     department: str = None) -> Dict:
        """
        Search all emails for a domain using Hunter.io Domain Search

        Args:
            domain: Company domain (e.g., "salesforce.com")
            company: Company name (alternative to domain)
            limit: Max results (default 10, max 100)
            offset: Pagination offset
            email_type: Filter by type (personal, generic)
            seniority: Filter by seniority (junior, senior, executive)
            department: Filter by department (executive, it, finance, etc.)

        Returns:
            {
                'domain': str,
                'pattern': str,
                'emails': list,
                'accept_all': bool
            }
        """
        self._wait_for_rate_limit("finder")

        url = f"{self.base_url}/domain-search"
        params = {
            'api_key': self.api_key,
            'limit': min(limit, 100),
            'offset': offset
        }

        if domain:
            params['domain'] = domain
        elif company:
            params['company'] = company
        else:
            logger.error("   ❌ Either domain or company must be provided")
            return None

        # Optional filters
        if email_type:
            params['type'] = email_type
        if seniority:
            params['seniority'] = seniority
        if department:
            params['department'] = department

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'data' in data:
                result = data['data']
                email_count = len(result.get('emails', []))
                logger.info(f"   ✅ Hunter.io found {email_count} emails for {domain or company}")
                return result
            else:
                logger.error(f"   ❌ Hunter.io API error: {data.get('errors', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Hunter.io request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"   ❌ Hunter.io unexpected error: {e}")
            return None

    def get_account_info(self) -> Dict:
        """
        Get account information and remaining credits

        Returns:
            {
                'email': str,
                'plan_name': str,
                'requests': {
                    'available': int,
                    'used': int
                }
            }
        """
        url = f"{self.base_url}/account"
        params = {'api_key': self.api_key}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'data' in data:
                account = data['data']
                logger.info(f"   📊 Hunter.io Account: {account.get('email')}")
                logger.info(f"      Plan: {account.get('plan_name')}")
                requests_data = account.get('requests', {})
                logger.info(f"      Credits: {requests_data.get('available')} available, {requests_data.get('used')} used")
                return account
            else:
                logger.error(f"   ❌ Hunter.io API error: {data.get('errors', 'Unknown error')}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"   ❌ Hunter.io request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"   ❌ Hunter.io unexpected error: {e}")
            return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize with your API key
    hunter = HunterIOClient(api_key="1553249bbb256b2a3d111c9c67755c2927053828")

    print("\n" + "="*70)
    print("🔍 Testing Hunter.io API")
    print("="*70)

    # Test 1: Check account info
    print("\n1️⃣ Checking account info...")
    account = hunter.get_account_info()

    # Test 2: Verify email
    print("\n2️⃣ Verifying email...")
    verification = hunter.verify_email("marc@salesforce.com")
    if verification:
        print(f"   Status: {verification.get('status')}")
        print(f"   Score: {verification.get('score')}")
        print(f"   SMTP Check: {verification.get('smtp_check')}")

    # Test 3: Find email
    print("\n3️⃣ Finding email...")
    email_data = hunter.find_email(
        domain="salesforce.com",
        first_name="Marc",
        last_name="Benioff"
    )
    if email_data:
        print(f"   Found: {email_data.get('email')}")
        print(f"   Score: {email_data.get('score')}")

    # Test 4: Domain search
    print("\n4️⃣ Searching domain...")
    domain_data = hunter.domain_search(domain="stripe.com", limit=5)
    if domain_data:
        print(f"   Pattern: {domain_data.get('pattern')}")
        print(f"   Found {len(domain_data.get('emails', []))} emails")
        for email_obj in domain_data.get('emails', [])[:3]:
            print(f"      • {email_obj.get('value')} ({email_obj.get('first_name')} {email_obj.get('last_name')})")

    print("\n" + "="*70)
    print("✅ Hunter.io API test complete!")
    print("="*70)
