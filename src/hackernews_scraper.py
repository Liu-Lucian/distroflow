"""
Hacker News Scraper - Hacker News爬虫
通过Hacker News API和Algolia API获取技术人员和创始人的信息
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HackerNewsScraper(PlatformScraperBase):
    """Hacker News平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化Hacker News scraper

        Args:
            auth_file: 认证配置文件路径（HN不需要认证）
        """
        super().__init__({}, 'Hacker News')

        # Hacker News API (官方)
        self.api_base = "https://hacker-news.firebaseio.com/v0"

        # Algolia HN Search API (更强大)
        self.algolia_base = "https://hn.algolia.com/api/v1"

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索Hacker News用户

        策略：
        1. 搜索相关的Show HN/Ask HN帖子
        2. 获取发帖者和活跃评论者
        3. 优先选择karma高的用户

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching Hacker News for active users (limit: {limit})")

        users = []
        seen_usernames = set()

        # 搜索关键词组合
        query = ' '.join(keywords) if keywords else 'hiring'

        try:
            # 使用Algolia API搜索相关帖子
            search_url = f"{self.algolia_base}/search"
            params = {
                'query': query,
                'tags': '(story,show_hn)',  # 只搜索故事和Show HN
                'hitsPerPage': 30
            }

            response = requests.get(
                search_url,
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])

                logger.info(f"   Found {len(hits)} relevant posts")

                # 从每个帖子提取作者和评论者
                for hit in hits:
                    if len(users) >= limit:
                        break

                    # 获取帖子作者
                    author = hit.get('author')
                    if author and author not in seen_usernames:
                        user_data = self._get_user_data(author)
                        if user_data:
                            users.append(user_data)
                            seen_usernames.add(author)

                    # 获取帖子的评论者
                    story_id = hit.get('objectID')
                    if story_id:
                        commenters = self._get_story_commenters(story_id, limit=5)
                        for commenter in commenters:
                            if len(users) >= limit:
                                break
                            if commenter not in seen_usernames:
                                user_data = self._get_user_data(commenter)
                                if user_data:
                                    users.append(user_data)
                                    seen_usernames.add(commenter)

                    time.sleep(0.5)  # 避免请求过快

            else:
                logger.warning(f"   ⚠️  Search failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Error searching Hacker News: {e}")

        logger.info(f"✅ Found {len(users)} users on Hacker News")
        return users[:limit]

    def _get_story_commenters(self, story_id: str, limit: int = 5) -> List[str]:
        """
        获取某个帖子的评论者

        Args:
            story_id: 帖子ID
            limit: 数量限制

        Returns:
            用户名列表
        """
        commenters = []

        try:
            # 获取帖子详情
            response = requests.get(
                f"{self.api_base}/item/{story_id}.json",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                story = response.json()
                kids = story.get('kids', [])[:limit]  # 取前N个评论

                for kid_id in kids:
                    # 获取评论详情
                    comment_response = requests.get(
                        f"{self.api_base}/item/{kid_id}.json",
                        headers=self.headers,
                        timeout=30
                    )

                    if comment_response.status_code == 200:
                        comment = comment_response.json()
                        author = comment.get('by')
                        if author:
                            commenters.append(author)

                    time.sleep(0.2)

        except Exception as e:
            logger.debug(f"   Error getting commenters: {e}")

        return commenters

    def _get_user_data(self, username: str) -> Optional[Dict]:
        """
        获取用户数据

        Args:
            username: HN用户名

        Returns:
            用户数据字典
        """
        try:
            response = requests.get(
                f"{self.api_base}/user/{username}.json",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                # 只返回karma > 100的用户（更活跃/可信）
                karma = data.get('karma', 0)
                if karma < 100:
                    return None

                user = {
                    'username': username,
                    'profile_url': f"https://news.ycombinator.com/user?id={username}",
                    'karma': karma,
                    'created': data.get('created', 0),
                    'about': data.get('about', ''),
                    'platform': 'hackernews'
                }

                return user

        except Exception as e:
            logger.debug(f"   Error getting user {username}: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取Hacker News用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        logger.debug(f"📖 Fetching HN profile: {user_id}")

        user_data = self._get_user_data(user_id)

        if user_data:
            return user_data
        else:
            return {
                'username': user_id,
                'profile_url': f"https://news.ycombinator.com/user?id={user_id}",
                'platform': 'hackernews',
                'status': 'not_found'
            }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从Hacker News资料提取邮箱

        HN的about字段有时包含邮箱或联系方式

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        about = user_profile.get('about', '')

        if not about:
            return None

        # 简单的邮箱提取
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, about)

        if matches:
            return matches[0]

        return None

    def search_hiring_posts(self, limit: int = 10) -> List[Dict]:
        """
        搜索"Who is hiring"帖子中的公司

        Hacker News每月有"Who is hiring"帖子，是获取招聘信息的好地方

        Args:
            limit: 返回数量

        Returns:
            招聘信息列表
        """
        logger.info("🔍 Searching 'Who is hiring' posts...")

        hiring_posts = []

        try:
            # 搜索Who is hiring帖子
            search_url = f"{self.algolia_base}/search"
            params = {
                'query': 'who is hiring',
                'tags': 'story',
                'hitsPerPage': 3
            }

            response = requests.get(
                search_url,
                params=params,
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                hits = data.get('hits', [])

                for hit in hits[:1]:  # 只取最新的一个
                    story_id = hit.get('objectID')
                    if story_id:
                        # 获取评论（每个评论是一个招聘信息）
                        hiring_posts = self._get_hiring_comments(story_id, limit)

        except Exception as e:
            logger.error(f"❌ Error searching hiring posts: {e}")

        return hiring_posts

    def _get_hiring_comments(self, story_id: str, limit: int = 10) -> List[Dict]:
        """
        获取招聘帖子的评论

        Args:
            story_id: 帖子ID
            limit: 数量限制

        Returns:
            招聘信息列表
        """
        hiring_info = []

        try:
            response = requests.get(
                f"{self.api_base}/item/{story_id}.json",
                headers=self.headers,
                timeout=30
            )

            if response.status_code == 200:
                story = response.json()
                kids = story.get('kids', [])[:limit]

                for kid_id in kids:
                    comment_response = requests.get(
                        f"{self.api_base}/item/{kid_id}.json",
                        headers=self.headers,
                        timeout=30
                    )

                    if comment_response.status_code == 200:
                        comment = comment_response.json()
                        hiring_info.append({
                            'text': comment.get('text', ''),
                            'author': comment.get('by', ''),
                            'time': comment.get('time', 0)
                        })

                    time.sleep(0.2)

        except Exception as e:
            logger.debug(f"   Error getting hiring comments: {e}")

        return hiring_info


# 测试代码
if __name__ == "__main__":
    scraper = HackerNewsScraper()

    # 测试搜索用户
    users = scraper.search_users(["startup", "founder"], limit=10)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - {user.get('username')} (karma: {user.get('karma', 0)})")
        print(f"    Profile: {user.get('profile_url')}")

    # 测试搜索招聘信息
    print("\n🔍 Searching hiring posts...")
    hiring = scraper.search_hiring_posts(limit=5)
    print(f"✅ Found {len(hiring)} hiring posts")
