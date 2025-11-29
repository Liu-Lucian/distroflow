"""
平台抽象基类 - Platform Scraper Base
统一的多平台scraper接口
"""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlatformScraperBase(ABC):
    """所有平台scraper的抽象基类"""

    def __init__(self, auth_config: Dict, platform_name: str):
        """
        初始化平台scraper

        Args:
            auth_config: 认证配置
            platform_name: 平台名称
        """
        self.auth_config = auth_config
        self.platform_name = platform_name
        logger.info(f"🔌 Initializing {platform_name} scraper...")

    @abstractmethod
    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        根据关键词搜索用户

        Args:
            keywords: 搜索关键词列表
            limit: 返回用户数量限制

        Returns:
            用户列表，每个用户是一个字典
        """
        pass

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取用户详细资料

        Args:
            user_id: 用户ID或用户名

        Returns:
            用户资料字典
        """
        pass

    @abstractmethod
    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从用户资料中提取邮箱

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        pass

    def normalize_user_data(self, raw_data: Dict) -> Dict:
        """
        将平台特定的用户数据标准化为统一格式

        Args:
            raw_data: 平台原始数据

        Returns:
            标准化的用户数据
        """
        return {
            'platform': self.platform_name,
            'username': raw_data.get('username', ''),
            'name': raw_data.get('name', ''),
            'bio': raw_data.get('bio', ''),
            'location': raw_data.get('location', ''),
            'website': raw_data.get('website', ''),
            'email': raw_data.get('email', ''),
            'company': raw_data.get('company', ''),
            'job_title': raw_data.get('job_title', ''),
            'followers_count': raw_data.get('followers_count', 0),
            'profile_url': raw_data.get('profile_url', ''),
            'raw_data': raw_data  # 保留原始数据
        }

    def get_leads(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        完整的获取leads流程（搜索 + 获取详情 + 提取邮箱）

        Args:
            keywords: 搜索关键词
            limit: 数量限制

        Returns:
            标准化的leads列表
        """
        logger.info(f"\n🔍 Searching {self.platform_name} for: {', '.join(keywords)}")
        logger.info(f"   Target: {limit} users")

        # Step 1: 搜索用户
        users = self.search_users(keywords, limit)
        logger.info(f"   ✅ Found {len(users)} users")

        # Step 2: 获取详细资料和邮箱
        leads = []
        for i, user in enumerate(users, 1):
            try:
                # 获取详细资料
                profile = self.get_user_profile(user.get('id') or user.get('username'))

                # 提取邮箱
                email = self.extract_email(profile)

                # 标准化数据
                normalized = self.normalize_user_data(profile)
                if email:
                    normalized['email'] = email

                leads.append(normalized)

                if i % 10 == 0:
                    logger.info(f"   Progress: {i}/{len(users)} processed")

            except Exception as e:
                logger.warning(f"   ⚠️  Error processing user: {e}")
                continue

        logger.info(f"   ✅ Processed {len(leads)} leads")
        emails_found = sum(1 for lead in leads if lead.get('email'))
        logger.info(f"   📧 Emails found: {emails_found}/{len(leads)} ({emails_found/len(leads)*100:.1f}%)")

        return leads
