"""
Smart Email Finder - 智能分工版本
合理分配 Hunter.io 和 LLM 的使用场景

策略：
1. Hunter.io - 用于精准查找（有公司域名的情况）
2. LLM - 用于模式识别和推断（简短prompt）
3. 自动过滤无效域名（t.co等）
"""

from ultimate_email_finder_hunter import UltimateEmailFinderWithHunter
import logging

logger = logging.getLogger(__name__)


class SmartEmailFinder(UltimateEmailFinderWithHunter):
    """
    智能邮箱查找器 - 最优策略

    分工原则：
    - Hunter.io：精准查找（有姓名+公司域名）
    - LLM：模式识别（媒体/组织通用邮箱）
    - 自动过滤：@t.co等短链接域名
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Store original LLM finder before monkey-patching
        self.original_llm_finder = self.llm_finder

        # 统计使用情况
        self.stats = {
            'hunter_attempts': 0,
            'hunter_success': 0,
            'llm_attempts': 0,
            'llm_success': 0,
            'filtered_tco': 0
        }

    def _is_valid_email_format(self, email: str) -> bool:
        """
        强验证邮箱格式（过滤LLM生成的无效邮箱）

        Args:
            email: 邮箱地址

        Returns:
            True if valid format, False otherwise
        """
        if not email or '@' not in email:
            logger.info(f"      ❌ Filtered: {email} (no @)")
            return False

        email_lower = email.lower()

        # 1. 过滤占位符（英文和中文）
        placeholders = [
            '[', ']',           # [domain], [company]
            '网站', '域名', '公司',  # 中文占位符
            'placeholder',
            '.what', '.for',    # 错误后缀
            'comsocial', 'comaddress',  # 拼接错误
            '.com)', '.(she/her)@',     # 格式错误
        ]
        for p in placeholders:
            if p in email_lower:
                logger.info(f"      ❌ Filtered placeholder: {email}")
                return False

        # 2. 验证基本格式
        import re
        # 标准邮箱格式：xxx@yyy.zzz
        if not re.match(r'^[a-zA-Z0-9._+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            logger.info(f"      ❌ Filtered invalid format: {email}")
            return False

        # 3. 检查域名部分
        domain = email.split('@')[1]

        # 域名必须有至少一个点
        if '.' not in domain:
            logger.info(f"      ❌ Filtered: {email} (no TLD)")
            return False

        # 检查TLD是否合理（不应该是 .we, .goodfin, .vcfor 等）
        tld = domain.split('.')[-1]
        invalid_tlds = ['we', 'goodfin', 'vcfor', 'restagno', 'what']
        if tld in invalid_tlds:
            logger.info(f"      ❌ Filtered invalid TLD: {email} (.{tld})")
            return False

        # TLD长度应该在2-6之间
        if len(tld) < 2 or len(tld) > 6:
            logger.info(f"      ❌ Filtered: {email} (TLD too long/short)")
            return False

        # 4. 检查是否有多余的点（如 .ai.we）
        parts = domain.split('.')
        if len(parts) > 3:  # example.co.uk 是ok的，但 example.ai.we.com 不行
            logger.info(f"      ❌ Filtered: {email} (too many dots in domain)")
            return False

        return True

    def _should_use_hunter(self, follower: dict) -> bool:
        """
        判断是否应该使用Hunter.io

        使用Hunter.io的场景：
        - 有真实公司域名（不是t.co）
        - 有姓名
        - 账号看起来像个人（而不是媒体/组织）

        Args:
            follower: 用户信息

        Returns:
            True if should use Hunter.io
        """
        if not self.use_hunter:
            return False

        name = follower.get('name', '')
        website = follower.get('website', '')
        username = follower.get('username', '')

        # 必须有网站和姓名
        if not website or not name:
            return False

        # 过滤短链接域名
        if 't.co' in website or 'bit.ly' in website:
            return False

        # 如果是媒体/组织账号，不用Hunter（用LLM更好）
        media_keywords = ['news', 'tech', 'magazine', 'media', 'daily', 'times',
                         'post', 'journal', 'press', 'blog']
        username_lower = username.lower()
        name_lower = name.lower()

        for keyword in media_keywords:
            if keyword in username_lower or keyword in name_lower:
                logger.info(f"      ℹ️  {username} looks like media, using LLM instead")
                return False

        # 看起来是个人账号，用Hunter.io
        return True

    def _find_email_smart(self, follower: dict) -> str:
        """
        智能查找邮箱 - 自动选择最佳方法

        决策逻辑：
        1. 检查是否@t.co域名 → 过滤
        2. 有真实公司域名 + 姓名 → Hunter.io
        3. 媒体/组织账号 → LLM (简短prompt)
        4. 其他 → 回退到基础方法

        Args:
            follower: 用户信息

        Returns:
            Email address or None
        """
        username = follower.get('username', '')
        name = follower.get('name', '')
        website = follower.get('website', '')

        # Step 1: 检查t.co域名
        if website and 't.co' in website:
            self.stats['filtered_tco'] += 1
            logger.info(f"      ⚠️  Skipping {username} - t.co domain (short link)")
            return None

        # Step 2: 尝试Hunter.io（适合个人账号）
        if self._should_use_hunter(follower):
            self.stats['hunter_attempts'] += 1
            logger.info(f"      🎯 Using Hunter.io for {username} (person account)")

            email = self._find_email_with_hunter(follower)
            if email:
                self.stats['hunter_success'] += 1
                return email

        # Step 3: 使用LLM（适合媒体/组织）
        self.stats['llm_attempts'] += 1

        # 简化的LLM prompt（你的建议）
        # Use original LLM finder to avoid infinite loop
        original_llm = getattr(self, 'original_llm_finder', self.llm_finder)
        if original_llm:
            logger.info(f"      🤖 Using LLM for {username} (org/media account)")

            result = original_llm.analyze_profile_for_contacts(follower)
            if result and result.get('possible_emails'):
                emails = result['possible_emails']
                for email_obj in emails:
                    email = email_obj.get('email', '')

                    # 强验证邮箱格式
                    if not self._is_valid_email_format(email):
                        continue

                    # 过滤@t.co
                    if self._is_valid_email_domain(email):
                        self.stats['llm_success'] += 1
                        confidence = email_obj.get('confidence', 0)
                        logger.info(f"      ✅ LLM found: {email} (confidence: {confidence}%)")
                        return email

        return None

    def print_stats(self):
        """打印使用统计"""
        logger.info("\n📊 Email Finding Strategy Stats:")
        logger.info(f"   Hunter.io: {self.stats['hunter_success']}/{self.stats['hunter_attempts']} " +
                   f"({self.stats['hunter_success']/max(self.stats['hunter_attempts'],1)*100:.1f}%)")
        logger.info(f"   LLM: {self.stats['llm_success']}/{self.stats['llm_attempts']} " +
                   f"({self.stats['llm_success']/max(self.stats['llm_attempts'],1)*100:.1f}%)")
        logger.info(f"   Filtered @t.co: {self.stats['filtered_tco']}")


# Monkey-patch the enhanced run method
from ultimate_email_finder import UltimateEmailFinder

original_run = UltimateEmailFinder.run

def smart_run(self, product_doc: str, followers_per: int = 100, max_seeds: int = 10):
    """Smart run with Hunter.io + LLM hybrid approach"""

    if hasattr(self, 'hunter') and self.hunter and hasattr(self, '_find_email_smart'):
        # Store original LLM finder
        original_llm_finder = self.llm_finder

        # Create smart wrapper
        class SmartEmailWrapper:
            def __init__(self, parent_instance):
                self.parent = parent_instance

            def analyze_profile_for_contacts(self, profile):
                # Use smart finder
                email = self.parent._find_email_smart(profile)
                if email:
                    return {
                        'possible_emails': [{
                            'email': email,
                            'confidence': 85  # High confidence from smart finder
                        }]
                    }
                # Fallback to original LLM
                return original_llm_finder.analyze_profile_for_contacts(profile) if original_llm_finder else {}

        # Replace LLM finder
        self.llm_finder = SmartEmailWrapper(self)

    # Call original run
    result = original_run(self, product_doc, followers_per, max_seeds)

    # Print stats
    if hasattr(self, 'print_stats'):
        self.print_stats()

    return result

# Apply enhancement
SmartEmailFinder.run = smart_run


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python smart_email_finder.py <product_doc> [followers] [seeds]")
        sys.exit(1)

    finder = SmartEmailFinder(
        auth_file="/Users/l.u.c/my-app/MarketingMind AI/auth.json",
        enable_email_verification=True  # Hunter.io verification
    )

    finder.run(
        product_doc=sys.argv[1],
        followers_per=int(sys.argv[2]) if len(sys.argv) > 2 else 50,
        max_seeds=int(sys.argv[3]) if len(sys.argv) > 3 else 3
    )
