"""
Reddit Scraper - Reddit爬虫
使用PRAW (Python Reddit API Wrapper) 或直接API访问
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedditScraper(PlatformScraperBase):
    """Reddit平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化Reddit scraper

        Args:
            auth_file: 认证配置文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('reddit', {})
        except FileNotFoundError:
            logger.warning(f"⚠️  Auth file {auth_file} not found, using public API")
            auth_config = {}

        super().__init__(auth_config, 'Reddit')

        # Reddit API配置
        self.client_id = self.auth_config.get('client_id', '')
        self.client_secret = self.auth_config.get('client_secret', '')
        self.user_agent = self.auth_config.get('user_agent', 'MarketingMindAI/1.0')

        # API endpoints
        self.oauth_url = "https://www.reddit.com/api/v1/access_token"
        self.api_base = "https://oauth.reddit.com"
        self.public_api_base = "https://www.reddit.com"

        # 获取access token（如果有credentials）
        self.access_token = self._get_access_token()

        # 设置headers
        if self.access_token:
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'User-Agent': self.user_agent
            }
        else:
            self.headers = {
                'User-Agent': self.user_agent
            }

    def _get_access_token(self) -> str:
        """
        获取Reddit OAuth access token

        Returns:
            Access token字符串
        """
        if not self.client_id or not self.client_secret:
            logger.info("ℹ️  No Reddit credentials, using public API")
            return ''

        try:
            response = requests.post(
                self.oauth_url,
                auth=(self.client_id, self.client_secret),
                data={'grant_type': 'client_credentials'},
                headers={'User-Agent': self.user_agent},
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token', '')
                if token:
                    logger.info("✅ Reddit access token obtained")
                return token
            else:
                logger.warning(f"⚠️  Failed to get access token: {response.status_code}")
                return ''

        except Exception as e:
            logger.warning(f"⚠️  Error getting access token: {e}")
            return ''

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索Reddit用户

        策略：
        1. 搜索相关subreddits
        2. 获取热门帖子的作者
        3. 获取活跃评论者

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching Reddit for active users (limit: {limit})")

        users = []
        seen_usernames = set()

        # 搜索相关subreddits
        query = ' '.join(keywords) if keywords else 'startup'

        try:
            # 使用公开API搜索
            base_url = self.api_base if self.access_token else self.public_api_base

            # 搜索帖子
            search_url = f"{base_url}/search.json"
            params = {
                'q': query,
                'sort': 'relevance',
                'limit': 25,
                't': 'month'  # 最近一个月
            }

            response = requests.get(
                search_url,
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])

                logger.info(f"   Found {len(posts)} relevant posts")

                # 从每个帖子提取作者和评论者
                for post in posts:
                    if len(users) >= limit:
                        break

                    post_data = post.get('data', {})

                    # 获取帖子作者
                    author = post_data.get('author')
                    if author and author not in ['[deleted]', 'AutoModerator'] and author not in seen_usernames:
                        user_data = self._get_user_data(author)
                        if user_data:
                            users.append(user_data)
                            seen_usernames.add(author)

                    # 获取评论者
                    post_id = post_data.get('id')
                    if post_id and len(users) < limit:
                        commenters = self._get_post_commenters(post_id, limit=5)
                        for commenter in commenters:
                            if len(users) >= limit:
                                break
                            if commenter not in seen_usernames:
                                user_data = self._get_user_data(commenter)
                                if user_data:
                                    users.append(user_data)
                                    seen_usernames.add(commenter)

                    time.sleep(1)  # Rate limiting

            else:
                logger.warning(f"   ⚠️  Search failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Error searching Reddit: {e}")

        logger.info(f"✅ Found {len(users)} users on Reddit")
        return users[:limit]

    def _get_post_commenters(self, post_id: str, limit: int = 5) -> List[str]:
        """
        获取帖子的评论者

        Args:
            post_id: 帖子ID
            limit: 数量限制

        Returns:
            用户名列表
        """
        commenters = []

        try:
            base_url = self.api_base if self.access_token else self.public_api_base
            comments_url = f"{base_url}/comments/{post_id}.json"

            response = requests.get(
                comments_url,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                # Reddit返回[post_data, comments_data]
                if len(data) > 1:
                    comments = data[1].get('data', {}).get('children', [])

                    for comment in comments[:limit]:
                        comment_data = comment.get('data', {})
                        author = comment_data.get('author')
                        if author and author not in ['[deleted]', 'AutoModerator']:
                            commenters.append(author)

        except Exception as e:
            logger.debug(f"   Error getting commenters: {e}")

        return commenters

    def _get_user_data(self, username: str) -> Optional[Dict]:
        """
        获取用户数据

        Args:
            username: Reddit用户名

        Returns:
            用户数据字典
        """
        try:
            base_url = self.api_base if self.access_token else self.public_api_base
            user_url = f"{base_url}/user/{username}/about.json"

            response = requests.get(
                user_url,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {})

                # 过滤低karma用户
                link_karma = user_data.get('link_karma', 0)
                comment_karma = user_data.get('comment_karma', 0)
                total_karma = link_karma + comment_karma

                if total_karma < 100:  # 只要karma>100的用户
                    return None

                user = {
                    'username': username,
                    'profile_url': f"https://www.reddit.com/user/{username}",
                    'karma': total_karma,
                    'link_karma': link_karma,
                    'comment_karma': comment_karma,
                    'created_utc': user_data.get('created_utc', 0),
                    'platform': 'reddit'
                }

                return user

        except Exception as e:
            logger.debug(f"   Error getting user {username}: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取Reddit用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching Reddit profile: {user_id}")

        user_data = self._get_user_data(user_id)

        if user_data:
            return user_data
        else:
            return {
                'username': user_id,
                'profile_url': f"https://www.reddit.com/user/{user_id}",
                'platform': 'reddit',
                'status': 'not_found'
            }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从Reddit资料提取邮箱

        Reddit不公开邮箱，需要从用户的帖子和评论中搜索

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # Reddit不公开邮箱
        # 可以尝试从用户的帖子历史中搜索，但这里简化处理
        return None

    def search_subreddit_users(self, subreddit: str, limit: int = 50) -> List[Dict]:
        """
        从特定subreddit获取活跃用户

        Args:
            subreddit: subreddit名称（例如'startups', 'entrepreneur'）
            limit: 数量限制

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching r/{subreddit} for active users...")

        users = []
        seen_usernames = set()

        try:
            base_url = self.api_base if self.access_token else self.public_api_base
            subreddit_url = f"{base_url}/r/{subreddit}/hot.json"

            response = requests.get(
                subreddit_url,
                params={'limit': 25},
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                posts = data.get('data', {}).get('children', [])

                for post in posts:
                    if len(users) >= limit:
                        break

                    post_data = post.get('data', {})
                    author = post_data.get('author')

                    if author and author not in ['[deleted]', 'AutoModerator'] and author not in seen_usernames:
                        user_data = self._get_user_data(author)
                        if user_data:
                            users.append(user_data)
                            seen_usernames.add(author)

                    time.sleep(0.5)

        except Exception as e:
            logger.error(f"❌ Error: {e}")

        logger.info(f"✅ Found {len(users)} users from r/{subreddit}")
        return users


# 测试代码
if __name__ == "__main__":
    scraper = RedditScraper()

    # 测试搜索用户
    users = scraper.search_users(["startup", "founder"], limit=10)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - u/{user.get('username')} (karma: {user.get('karma', 0)})")
        print(f"    Profile: {user.get('profile_url')}")

    # 测试subreddit搜索
    print("\n🔍 Searching r/startups...")
    startup_users = scraper.search_subreddit_users('startups', limit=5)
    print(f"✅ Found {len(startup_users)} users from r/startups")
