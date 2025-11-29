"""
Product Hunt Scraper - Product Hunt爬虫
通过Product Hunt API和网页抓取获取创业者和制造者的信息
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductHuntScraper(PlatformScraperBase):
    """Product Hunt平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化Product Hunt scraper

        Args:
            auth_file: 认证配置文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('producthunt', {})
        except FileNotFoundError:
            logger.warning(f"⚠️  Auth file {auth_file} not found, using API without auth")
            auth_config = {}

        super().__init__(auth_config, 'Product Hunt')

        # Product Hunt API配置
        self.api_key = self.auth_config.get('api_key', '')
        self.api_secret = self.auth_config.get('api_secret', '')
        self.redirect_uri = self.auth_config.get('redirect_uri', '')

        # API endpoints
        self.oauth_url = "https://api.producthunt.com/v2/oauth/token"
        self.base_url = "https://api.producthunt.com/v2/api/graphql"

        # 获取access token
        self.access_token = self._get_access_token()

        # 设置headers
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}' if self.access_token else '',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def _get_access_token(self) -> str:
        """
        使用client credentials获取access token

        Returns:
            Access token字符串
        """
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️  No API credentials provided")
            return ''

        try:
            response = requests.post(
                self.oauth_url,
                json={
                    'client_id': self.api_key,
                    'client_secret': self.api_secret,
                    'grant_type': 'client_credentials'
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token', '')
                if token:
                    logger.info("✅ Product Hunt access token obtained")
                return token
            else:
                logger.warning(f"⚠️  Failed to get access token: {response.status_code}")
                return ''

        except Exception as e:
            logger.warning(f"⚠️  Error getting access token: {e}")
            return ''

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索Product Hunt用户（制造者和创业者）

        Product Hunt的用户通常是：
        - 产品制造者
        - 创业者
        - 早期采用者
        - 投资人

        Args:
            keywords: 搜索关键词（用于搜索产品或用户）
            limit: 结果数量

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching Product Hunt for makers and hunters (limit: {limit})")

        users = []

        # 策略1: 获取最近的热门产品的制造者
        users.extend(self._get_makers_from_posts(limit=limit // 2))

        # 策略2: 获取活跃的hunters
        users.extend(self._get_active_hunters(limit=limit // 2))

        logger.info(f"✅ Found {len(users)} users on Product Hunt")
        return users[:limit]

    def _get_makers_from_posts(self, limit: int = 50) -> List[Dict]:
        """
        从最近的热门产品获取制造者信息

        Returns:
            制造者列表
        """
        logger.info("   📦 Getting makers from recent products...")

        # GraphQL查询获取最近的产品
        query = """
        query {
          posts(order: VOTES) {
            edges {
              node {
                id
                name
                tagline
                votesCount
                makers {
                  id
                  name
                  username
                  headline
                  websiteUrl
                  twitterUsername
                }
              }
            }
          }
        }
        """

        makers = []

        try:
            # 如果没有access token，使用公开的RSS feed
            if not self.access_token:
                logger.info("   ℹ️  No access token, using public RSS feed...")
                makers = self._get_makers_from_rss()
            else:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json={'query': query},
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    posts = data.get('data', {}).get('posts', {}).get('edges', [])

                    for post in posts[:20]:  # 取前20个产品
                        node = post.get('node', {})
                        product_name = node.get('name', '')
                        product_makers = node.get('makers', [])

                        for maker in product_makers:
                            if len(makers) >= limit:
                                break

                            user = {
                                'name': maker.get('name', ''),
                                'username': maker.get('username', ''),
                                'profile_url': f"https://www.producthunt.com/@{maker.get('username', '')}",
                                'headline': maker.get('headline', ''),
                                'website': maker.get('websiteUrl', ''),
                                'twitter': maker.get('twitterUsername', ''),
                                'product': product_name,
                                'platform': 'producthunt'
                            }
                            makers.append(user)

                else:
                    logger.warning(f"   ⚠️  API request failed: {response.status_code}")
                    # Fallback to RSS
                    makers = self._get_makers_from_rss()

        except Exception as e:
            logger.warning(f"   ⚠️  Error getting makers: {e}")
            # Fallback to RSS
            makers = self._get_makers_from_rss()

        logger.info(f"   ✓ Found {len(makers)} makers")
        return makers

    def _get_makers_from_rss(self) -> List[Dict]:
        """
        从Product Hunt的公开RSS feed获取制造者

        Returns:
            制造者列表
        """
        makers = []

        try:
            # 使用Product Hunt的GraphQL公开端点
            # 这个端点不需要认证即可获取基本信息
            response = requests.post(
                'https://www.producthunt.com/frontend/graphql',
                headers={
                    'User-Agent': self.headers['User-Agent'],
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                json={
                    'query': '''
                    query {
                        posts {
                            edges {
                                node {
                                    name
                                    tagline
                                    makers {
                                        name
                                        username
                                        headline
                                        websiteUrl
                                        twitterUsername
                                    }
                                }
                            }
                        }
                    }
                    '''
                },
                timeout=30
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    posts = data.get('data', {}).get('posts', {}).get('edges', [])

                    for post in posts[:10]:  # 取前10个产品
                        node = post.get('node', {})
                        product_name = node.get('name', '')
                        product_makers = node.get('makers', [])

                        for maker in product_makers:
                            makers.append({
                                'name': maker.get('name', ''),
                                'username': maker.get('username', ''),
                                'profile_url': f"https://www.producthunt.com/@{maker.get('username', '')}",
                                'headline': maker.get('headline', ''),
                                'website': maker.get('websiteUrl', ''),
                                'twitter': maker.get('twitterUsername', ''),
                                'product': product_name,
                                'platform': 'producthunt'
                            })
                except Exception as e:
                    logger.debug(f"   Error parsing response: {e}")
            else:
                logger.info(f"   ℹ️  Public API returned {response.status_code}, Product Hunt data may be limited")

        except Exception as e:
            logger.warning(f"   ⚠️  Error fetching data: {e}")

        return makers

    def _get_active_hunters(self, limit: int = 50) -> List[Dict]:
        """
        获取活跃的Product Hunters

        Returns:
            hunters列表
        """
        logger.info("   🎯 Getting active hunters...")

        hunters = []

        # 由于Product Hunt API需要认证，这里返回空列表
        # 在有access token的情况下可以实现
        if not self.access_token:
            logger.info("   ℹ️  Access token required for hunter data")
            return hunters

        # TODO: 实现获取活跃hunters的逻辑

        return hunters

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取Product Hunt用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching Product Hunt profile: {user_id}")

        profile = {
            'username': user_id,
            'profile_url': f"https://www.producthunt.com/@{user_id}",
            'platform': 'producthunt'
        }

        try:
            # 访问用户主页
            response = requests.get(
                profile['profile_url'],
                headers={'User-Agent': self.headers['User-Agent']},
                timeout=30
            )

            if response.status_code == 200:
                # 这里应该解析HTML获取详细信息
                # 简化处理
                profile['status'] = 'success'
            else:
                profile['status'] = 'not_found'

        except Exception as e:
            logger.warning(f"⚠️  Error fetching profile: {e}")
            profile['status'] = 'error'

        return profile

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从Product Hunt资料提取邮箱

        Product Hunt不公开显示邮箱，需要通过：
        1. 查看用户的website
        2. 查看Twitter资料
        3. 使用Hunter.io

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # Product Hunt不公开邮箱
        # 返回None让Hunter.io从website域名推断
        return None


# 测试代码
if __name__ == "__main__":
    scraper = ProductHuntScraper()

    # 测试搜索
    users = scraper.search_users(["startup", "maker"], limit=10)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - {user.get('name', 'N/A')} (@{user.get('username', 'N/A')})")
        print(f"    Product: {user.get('product', 'N/A')}")
        print(f"    Twitter: @{user.get('twitter', 'N/A')}")
