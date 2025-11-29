"""
GitHub Scraper - GitHub用户爬虫
使用GitHub REST API v3
"""

import json
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubScraper(PlatformScraperBase):
    """GitHub平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化GitHub scraper

        Args:
            auth_file: 认证配置文件路径
        """
        # 加载认证配置
        with open(auth_file, 'r') as f:
            config = json.load(f)

        super().__init__(config['github'], 'GitHub')

        self.access_token = self.auth_config['access_token']
        self.headers = {
            'Authorization': f'token {self.access_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        self.base_url = 'https://api.github.com'

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索GitHub用户

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        # 构建搜索查询
        query = ' '.join(keywords)

        logger.info(f"🔍 Searching GitHub: {query}")

        users = []
        page = 1
        per_page = min(30, limit)  # GitHub API每页最多100个，我们用30

        while len(users) < limit:
            try:
                # GitHub User Search API
                url = f"{self.base_url}/search/users"
                params = {
                    'q': query,
                    'per_page': per_page,
                    'page': page
                }

                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()

                data = response.json()
                items = data.get('items', [])

                if not items:
                    break  # 没有更多结果

                for item in items:
                    if len(users) >= limit:
                        break

                    user = {
                        'username': item['login'],
                        'id': item['login'],  # 使用username作为id
                        'profile_url': item['html_url'],
                        'avatar_url': item.get('avatar_url', ''),
                        'platform': 'github'
                    }
                    users.append(user)

                page += 1

                # 检查是否还有更多结果
                if len(items) < per_page:
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ GitHub API error: {e}")
                break

        logger.info(f"✅ Found {len(users)} users on GitHub")
        return users[:limit]

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取GitHub用户详细资料

        Args:
            user_id: 用户名

        Returns:
            用户详细资料
        """
        username = user_id
        logger.debug(f"📖 Fetching profile: {username}")

        try:
            # Get user details
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            data = response.json()

            profile = {
                'username': data['login'],
                'name': data.get('name', ''),
                'bio': data.get('bio', ''),
                'location': data.get('location', ''),
                'website': data.get('blog', ''),
                'email': data.get('email', ''),  # 公开邮箱（如果有）
                'company': data.get('company', ''),
                'twitter_username': data.get('twitter_username', ''),
                'followers_count': data.get('followers', 0),
                'following_count': data.get('following', 0),
                'public_repos': data.get('public_repos', 0),
                'profile_url': data['html_url'],
                'avatar_url': data.get('avatar_url', ''),
                'platform': 'github'
            }

            # 如果profile没有邮箱，尝试从多个来源获取
            if not profile.get('email'):
                # 优先级1: README文件（最常见）
                email_from_readme = self._get_email_from_readme(username)
                if email_from_readme:
                    profile['email'] = email_from_readme
                else:
                    # 优先级2: commits
                    email_from_events = self._get_email_from_events(username)
                    if email_from_events:
                        profile['email'] = email_from_events

            return profile

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching GitHub profile {username}: {e}")
            return {
                'username': username,
                'platform': 'github',
                'profile_url': f'https://github.com/{username}'
            }

    def _get_email_from_readme(self, username: str) -> Optional[str]:
        """
        从用户的profile README中提取邮箱

        Args:
            username: 用户名

        Returns:
            邮箱地址或None
        """
        import re

        try:
            # GitHub profile README位于 username/username 仓库
            url = f"{self.base_url}/repos/{username}/{username}/readme"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                readme_data = response.json()
                # README content是base64编码的
                import base64
                content = base64.b64decode(readme_data['content']).decode('utf-8', errors='ignore')

                # 正则提取邮箱
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, content)

                # 过滤noreply和example邮箱
                for email in emails:
                    email_lower = email.lower()
                    if 'noreply' not in email_lower and 'example' not in email_lower and 'your' not in email_lower:
                        logger.debug(f"   Found email from README: {email}")
                        return email

        except Exception as e:
            logger.debug(f"   Could not extract email from README: {e}")

        return None

    def _get_email_from_events(self, username: str) -> Optional[str]:
        """
        从用户的公开events中提取邮箱（从commit中）

        Args:
            username: 用户名

        Returns:
            邮箱地址或None
        """
        try:
            url = f"{self.base_url}/users/{username}/events/public"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            events = response.json()

            # 查找PushEvent中的commit邮箱
            for event in events[:10]:  # 只检查最近10个events
                if event.get('type') == 'PushEvent':
                    commits = event.get('payload', {}).get('commits', [])
                    for commit in commits:
                        author = commit.get('author', {})
                        email = author.get('email', '')

                        # 过滤noreply邮箱
                        if email and 'noreply' not in email.lower():
                            logger.debug(f"   Found email from commits: {email}")
                            return email

        except Exception as e:
            logger.debug(f"   Could not extract email from events: {e}")

        return None

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从GitHub资料提取邮箱

        Args:
            user_profile: 用户资料

        Returns:
            邮箱地址或None
        """
        # GitHub可能公开邮箱
        email = user_profile.get('email', '')

        if email and 'noreply' not in email.lower():
            return email

        # 如果没有，返回None让Hunter.io处理
        return None

    def search_by_repository(self, repo_name: str, limit: int = 50) -> List[Dict]:
        """
        获取某个仓库的contributors

        Args:
            repo_name: 仓库名（格式: owner/repo）
            limit: 数量限制

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching contributors of {repo_name}")

        try:
            url = f"{self.base_url}/repos/{repo_name}/contributors"
            params = {'per_page': min(100, limit)}

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            contributors = response.json()

            users = []
            for contributor in contributors[:limit]:
                user = {
                    'username': contributor['login'],
                    'id': contributor['login'],
                    'profile_url': contributor['html_url'],
                    'avatar_url': contributor.get('avatar_url', ''),
                    'contributions': contributor.get('contributions', 0),
                    'platform': 'github'
                }
                users.append(user)

            logger.info(f"✅ Found {len(users)} contributors")
            return users

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching contributors: {e}")
            return []

    def search_by_topic(self, topic: str, limit: int = 100) -> List[Dict]:
        """
        通过topic搜索活跃用户

        Args:
            topic: 主题（如: machine-learning, ai, interview）
            limit: 数量限制

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching GitHub users by topic: {topic}")

        try:
            # 先搜索该topic的热门仓库
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': f'topic:{topic}',
                'sort': 'stars',
                'per_page': 10
            }

            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()

            repos = response.json().get('items', [])

            # 从这些仓库收集contributors
            all_users = []
            seen_usernames = set()

            for repo in repos:
                if len(all_users) >= limit:
                    break

                repo_full_name = repo['full_name']
                contributors = self.search_by_repository(
                    repo_full_name,
                    limit=min(20, limit - len(all_users))
                )

                # 去重
                for user in contributors:
                    if user['username'] not in seen_usernames:
                        all_users.append(user)
                        seen_usernames.add(user['username'])

                    if len(all_users) >= limit:
                        break

            logger.info(f"✅ Found {len(all_users)} users for topic {topic}")
            return all_users[:limit]

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error searching by topic: {e}")
            return []


# 测试代码
if __name__ == "__main__":
    scraper = GitHubScraper()

    # 测试搜索
    test_keywords = ["recruiter", "hiring", "interview"]
    users = scraper.search_users(test_keywords, limit=5)

    print(f"\n✅ Found {len(users)} users:")
    for user in users:
        print(f"  - {user['username']} | {user.get('profile_url', 'N/A')}")

    # 测试获取详情
    if users:
        profile = scraper.get_user_profile(users[0]['username'])
        print(f"\n📖 Profile details:")
        print(f"  Name: {profile.get('name')}")
        print(f"  Email: {profile.get('email', 'Not public')}")
        print(f"  Company: {profile.get('company')}")
        print(f"  Location: {profile.get('location')}")
        print(f"  Followers: {profile.get('followers_count')}")

    # 测试topic搜索
    print("\n🔍 Testing topic search...")
    topic_users = scraper.search_by_topic("interview", limit=5)
    print(f"✅ Found {len(topic_users)} users for topic 'interview'")
