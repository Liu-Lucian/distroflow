"""
Indie Hackers Scraper - Indie Hackers爬虫
通过公开API和网页抓取获取独立创业者信息
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndieHackersScraper(PlatformScraperBase):
    """Indie Hackers平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化Indie Hackers scraper

        Args:
            auth_file: 认证配置文件路径
        """
        super().__init__({}, 'Indie Hackers')

        self.base_url = "https://www.indiehackers.com"
        self.api_url = "https://www.indiehackers.com/api"

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索Indie Hackers用户（独立创业者）

        策略：
        1. 获取热门产品的创始人
        2. 获取活跃论坛成员
        3. 获取热门帖子作者

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching Indie Hackers for makers (limit: {limit})")

        users = []
        seen_usernames = set()

        try:
            # 策略1: 获取热门产品的创始人
            products_users = self._get_product_founders(limit=limit // 2)
            for user in products_users:
                if user['username'] not in seen_usernames:
                    users.append(user)
                    seen_usernames.add(user['username'])

            # 策略2: 获取热门帖子作者
            if len(users) < limit:
                post_users = self._get_post_authors(limit=limit - len(users))
                for user in post_users:
                    if user['username'] not in seen_usernames:
                        users.append(user)
                        seen_usernames.add(user['username'])

        except Exception as e:
            logger.error(f"❌ Error searching Indie Hackers: {e}")

        logger.info(f"✅ Found {len(users)} makers on Indie Hackers")
        return users[:limit]

    def _get_product_founders(self, limit: int = 50) -> List[Dict]:
        """
        获取热门产品的创始人

        Returns:
            创始人列表
        """
        founders = []

        try:
            # 获取产品列表
            products_url = f"{self.base_url}/products"

            response = requests.get(
                products_url,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                # 这里需要解析HTML或使用API
                # 简化处理：Indie Hackers的API相对开放
                logger.info("   Fetching product founders...")

                # 尝试使用公开的JSON endpoints
                # 注意：Indie Hackers可能需要特殊处理
                pass

        except Exception as e:
            logger.debug(f"   Error getting product founders: {e}")

        return founders

    def _get_post_authors(self, limit: int = 50) -> List[Dict]:
        """
        获取热门帖子的作者

        Returns:
            作者列表
        """
        authors = []

        try:
            # 获取论坛热门帖子
            posts_url = f"{self.base_url}/forum"

            response = requests.get(
                posts_url,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                logger.info("   Fetching post authors...")
                # 需要解析HTML
                pass

        except Exception as e:
            logger.debug(f"   Error getting post authors: {e}")

        return authors

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取Indie Hackers用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching Indie Hackers profile: {user_id}")

        profile_url = f"{self.base_url}/{user_id}"

        return {
            'username': user_id,
            'profile_url': profile_url,
            'platform': 'indiehackers'
        }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从Indie Hackers资料提取邮箱

        Indie Hackers不公开邮箱

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # Indie Hackers不公开邮箱
        return None


# 测试代码
if __name__ == "__main__":
    scraper = IndieHackersScraper()

    # 测试搜索
    users = scraper.search_users(["startup"], limit=10)

    print(f"\n✅ Found {len(users)} makers:")
    for user in users:
        print(f"  - {user.get('username')}")
