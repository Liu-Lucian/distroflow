"""
Medium Scraper - Medium爬虫
通过Medium的公开API和RSS获取作者信息
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediumScraper(PlatformScraperBase):
    """Medium平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化Medium scraper

        Args:
            auth_file: 认证配置文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('medium', {})
        except FileNotFoundError:
            logger.warning(f"⚠️  Auth file {auth_file} not found, using public API")
            auth_config = {}

        super().__init__(auth_config, 'Medium')

        # Medium API配置
        self.api_base = "https://api.medium.com/v1"
        self.public_base = "https://medium.com"

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json'
        }

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索Medium用户（作者）

        策略：
        1. 搜索相关标签的文章
        2. 获取文章作者
        3. 筛选活跃作者

        Args:
            keywords: 搜索关键词（标签）
            limit: 结果数量

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching Medium for authors (limit: {limit})")

        users = []
        seen_usernames = set()

        # Medium标签搜索
        tags = keywords if keywords else ['startup', 'entrepreneurship']

        try:
            for tag in tags[:3]:  # 限制标签数量
                if len(users) >= limit:
                    break

                logger.info(f"   Searching tag: {tag}")

                # 使用Medium的公开feed
                feed_url = f"{self.public_base}/tag/{tag}/latest"

                response = requests.get(
                    feed_url,
                    headers=self.headers,
                    params={'format': 'json'},
                    timeout=30
                )

                if response.status_code == 200:
                    # Medium返回的JSON前面有 ])}while(1);</x>
                    content = response.text
                    if content.startswith('])}while(1);</x>'):
                        content = content[16:]

                    try:
                        data = json.loads(content)
                        payload = data.get('payload', {})
                        references = payload.get('references', {})
                        users_data = references.get('User', {})

                        for user_id, user_info in users_data.items():
                            if len(users) >= limit:
                                break

                            username = user_info.get('username')
                            if username and username not in seen_usernames:
                                user = {
                                    'user_id': user_id,
                                    'username': username,
                                    'name': user_info.get('name', ''),
                                    'profile_url': f"https://medium.com/@{username}",
                                    'bio': user_info.get('bio', '')[:500],
                                    'follower_count': user_info.get('socialStats', {}).get('followerCount', 0),
                                    'platform': 'medium'
                                }

                                # 只保留有一定关注者的作者
                                if user['follower_count'] >= 100:
                                    users.append(user)
                                    seen_usernames.add(username)

                    except json.JSONDecodeError:
                        logger.debug(f"   Could not parse response for tag {tag}")

                time.sleep(2)  # Rate limiting

        except Exception as e:
            logger.error(f"❌ Error searching Medium: {e}")

        logger.info(f"✅ Found {len(users)} authors on Medium")
        return users[:limit]

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取Medium用户详细资料

        Args:
            user_id: 用户名或user_id

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching Medium profile: {user_id}")

        # 如果是username，构建profile URL
        if not user_id.startswith('@'):
            user_id = f"@{user_id}"

        profile_url = f"{self.public_base}/{user_id}"

        try:
            response = requests.get(
                profile_url,
                headers=self.headers,
                params={'format': 'json'},
                timeout=30
            )

            if response.status_code == 200:
                content = response.text
                if content.startswith('])}while(1);</x>'):
                    content = content[16:]

                data = json.loads(content)
                payload = data.get('payload', {})
                user_data = payload.get('user', {})

                return {
                    'user_id': user_data.get('userId'),
                    'username': user_data.get('username'),
                    'name': user_data.get('name', ''),
                    'profile_url': profile_url,
                    'bio': user_data.get('bio', ''),
                    'follower_count': user_data.get('socialStats', {}).get('followerCount', 0),
                    'platform': 'medium'
                }

        except Exception as e:
            logger.debug(f"   Error fetching profile: {e}")

        return {
            'username': user_id,
            'profile_url': profile_url,
            'platform': 'medium',
            'status': 'not_found'
        }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从Medium资料提取邮箱

        Medium不公开显示邮箱

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # Medium不公开邮箱
        return None


# 测试代码
if __name__ == "__main__":
    scraper = MediumScraper()

    # 测试搜索作者
    users = scraper.search_users(["startup", "entrepreneurship"], limit=10)

    print(f"\n✅ Found {len(users)} authors:")
    for user in users:
        print(f"  - @{user.get('username')} ({user.get('follower_count', 0)} followers)")
        print(f"    Name: {user.get('name', 'N/A')}")
