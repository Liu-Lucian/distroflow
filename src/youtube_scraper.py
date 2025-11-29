"""
YouTube Scraper - YouTube爬虫
使用YouTube Data API v3获取创作者和评论者信息
"""

import json
import time
import logging
import requests
from typing import List, Dict, Optional
from src.platform_scraper_base import PlatformScraperBase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YouTubeScraper(PlatformScraperBase):
    """YouTube平台scraper"""

    def __init__(self, auth_file: str = "platforms_auth.json"):
        """
        初始化YouTube scraper

        Args:
            auth_file: 认证配置文件路径
        """
        try:
            with open(auth_file, 'r') as f:
                config = json.load(f)
            auth_config = config.get('youtube', {})
        except FileNotFoundError:
            logger.warning(f"⚠️  Auth file {auth_file} not found")
            auth_config = {}

        super().__init__(auth_config, 'YouTube')

        # YouTube Data API配置
        self.api_key = self.auth_config.get('api_key', '')
        self.api_base = "https://www.googleapis.com/youtube/v3"

    def search_users(self, keywords: List[str], limit: int = 100) -> List[Dict]:
        """
        搜索YouTube用户（创作者）

        策略（无需API key）：
        1. 使用YouTube的RSS feeds
        2. 从trending videos获取创作者
        3. 从推荐获取频道

        Args:
            keywords: 搜索关键词
            limit: 结果数量

        Returns:
            用户列表
        """
        logger.info(f"🔍 Searching YouTube for creators (limit: {limit}) [No API mode]")

        users = []
        seen_channel_ids = set()

        query = ' '.join(keywords) if keywords else 'startup'

        try:
            # 使用无需API的方法：通过trending和search页面
            if self.api_key:
                # 如果有API key，使用API
                users = self._search_with_api(query, limit)
            else:
                # 否则使用RSS和公开数据
                logger.info("   Using RSS/public data (no API key)")
                users = self._search_with_rss(query, limit)

            return users

        except Exception as e:
            logger.error(f"❌ Error searching YouTube: {e}")
            return []

    def _search_with_rss(self, query: str, limit: int) -> List[Dict]:
        """
        使用RSS和公开数据搜索（无需API key）

        策略：使用YouTube搜索页面HTML解析

        Returns:
            用户列表
        """
        users = []
        seen_channel_ids = set()

        try:
            import re

            # 使用YouTube搜索页面
            search_url = "https://www.youtube.com/results"
            params = {'search_query': query}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            }

            response = requests.get(search_url, params=params, headers=headers, timeout=30)

            if response.status_code == 200:
                html = response.text

                # 从HTML中提取初始数据（YouTube在页面中嵌入JSON）
                # 查找 var ytInitialData = {...}
                match = re.search(r'var ytInitialData = ({.+?});', html)

                if match:
                    import json
                    try:
                        data = json.loads(match.group(1))

                        # 导航到视频结果
                        contents = data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])

                        for content in contents:
                            item_section = content.get('itemSectionRenderer', {})
                            items = item_section.get('contents', [])

                            for item in items:
                                if len(users) >= limit:
                                    break

                                # 获取视频渲染器
                                video_renderer = item.get('videoRenderer', {})
                                if not video_renderer:
                                    continue

                                # 获取频道信息
                                owner_text = video_renderer.get('ownerText', {})
                                runs = owner_text.get('runs', [])
                                if not runs:
                                    continue

                                channel_name = runs[0].get('text', '')
                                # 频道ID在navigationEndpoint中
                                navigation = runs[0].get('navigationEndpoint', {})
                                browse_endpoint = navigation.get('browseEndpoint', {})
                                channel_id = browse_endpoint.get('browseId', '')

                                if channel_id and channel_id not in seen_channel_ids:
                                    # 构建频道信息
                                    user = {
                                        'channel_id': channel_id,
                                        'channel_title': channel_name,
                                        'profile_url': f"https://www.youtube.com/channel/{channel_id}",
                                        'platform': 'youtube',
                                        'source': 'html_search'
                                    }

                                    users.append(user)
                                    seen_channel_ids.add(channel_id)

                                    logger.debug(f"   Found channel: {channel_name}")

                        logger.info(f"   Found {len(users)} channels from HTML search")

                    except json.JSONDecodeError as e:
                        logger.debug(f"   Error parsing YouTube data: {e}")
                else:
                    logger.info("   ℹ️  YouTube HTML structure may have changed")
                    logger.info("   ℹ️  Consider providing API key for better results")

        except Exception as e:
            logger.debug(f"   Error in HTML search: {e}")

        return users

    def _search_with_api(self, query: str, limit: int) -> List[Dict]:
        """
        使用API搜索（需要API key）

        Returns:
            用户列表
        """
        users = []
        seen_channel_ids = set()

        try:
            # 搜索视频
            search_url = f"{self.api_base}/search"
            params = {
                'key': self.api_key,
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': min(50, limit * 2),
                'order': 'relevance'
            }

            response = requests.get(search_url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                videos = data.get('items', [])

                logger.info(f"   Found {len(videos)} relevant videos")

                # 从每个视频提取频道信息
                for video in videos:
                    if len(users) >= limit:
                        break

                    snippet = video.get('snippet', {})
                    channel_id = snippet.get('channelId')
                    channel_title = snippet.get('channelTitle')

                    if channel_id and channel_id not in seen_channel_ids:
                        # 获取频道详细信息
                        channel_data = self._get_channel_data(channel_id)
                        if channel_data:
                            channel_data['channel_title'] = channel_title
                            users.append(channel_data)
                            seen_channel_ids.add(channel_id)

                    time.sleep(0.1)  # Rate limiting

            elif response.status_code == 403:
                logger.error("❌ YouTube API quota exceeded or invalid API key")
            else:
                logger.warning(f"   ⚠️  Search failed: {response.status_code}")

        except Exception as e:
            logger.error(f"❌ Error searching YouTube: {e}")

        logger.info(f"✅ Found {len(users)} creators on YouTube")
        return users[:limit]

    def _get_channel_data(self, channel_id: str) -> Optional[Dict]:
        """
        获取频道详细信息

        Args:
            channel_id: YouTube频道ID

        Returns:
            频道数据字典
        """
        try:
            channels_url = f"{self.api_base}/channels"
            params = {
                'key': self.api_key,
                'part': 'snippet,statistics',
                'id': channel_id
            }

            response = requests.get(
                channels_url,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                if items:
                    channel = items[0]
                    snippet = channel.get('snippet', {})
                    statistics = channel.get('statistics', {})

                    # 过滤小频道（至少1000订阅者）
                    subscriber_count = int(statistics.get('subscriberCount', 0))
                    if subscriber_count < 1000:
                        return None

                    user = {
                        'channel_id': channel_id,
                        'channel_title': snippet.get('title', ''),
                        'description': snippet.get('description', '')[:500],
                        'profile_url': f"https://www.youtube.com/channel/{channel_id}",
                        'subscriber_count': subscriber_count,
                        'video_count': int(statistics.get('videoCount', 0)),
                        'view_count': int(statistics.get('viewCount', 0)),
                        'custom_url': snippet.get('customUrl', ''),
                        'platform': 'youtube'
                    }

                    return user

        except Exception as e:
            logger.debug(f"   Error getting channel {channel_id}: {e}")
            return None

    def get_user_profile(self, user_id: str) -> Dict:
        """
        获取YouTube频道详细资料（从HTML获取description）

        Args:
            user_id: 频道ID

        Returns:
            频道详细资料
        """
        logger.debug(f"📖 Fetching YouTube channel: {user_id}")

        # 如果有API key，使用API获取
        if self.api_key:
            channel_data = self._get_channel_data(user_id)
            if channel_data:
                return channel_data

        # 否则从HTML页面获取描述
        try:
            import re
            about_url = f"https://www.youtube.com/channel/{user_id}/about"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(about_url, headers=headers, timeout=30)

            if response.status_code == 200:
                html = response.text

                # 提取频道描述（在ytInitialData中）
                match = re.search(r'var ytInitialData = ({.+?});', html)
                if match:
                    data = json.loads(match.group(1))

                    # 导航到description
                    try:
                        metadata = data.get('metadata', {}).get('channelMetadataRenderer', {})
                        description = metadata.get('description', '')

                        return {
                            'channel_id': user_id,
                            'channel_title': metadata.get('title', ''),
                            'description': description[:500],
                            'profile_url': f"https://www.youtube.com/channel/{user_id}",
                            'platform': 'youtube'
                        }
                    except Exception as e:
                        logger.debug(f"   Error parsing channel data: {e}")

        except Exception as e:
            logger.debug(f"   Error fetching profile HTML: {e}")

        # 返回基本信息
        return {
            'channel_id': user_id,
            'profile_url': f"https://www.youtube.com/channel/{user_id}",
            'platform': 'youtube',
            'status': 'not_found'
        }

    def extract_email(self, user_profile: Dict) -> Optional[str]:
        """
        从YouTube频道提取邮箱

        YouTube创作者有时在频道描述或"关于"页面放置邮箱

        Args:
            user_profile: 频道资料

        Returns:
            邮箱地址或None
        """
        description = user_profile.get('description', '')

        if not description:
            return None

        # 简单的邮箱提取
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, description)

        if matches:
            return matches[0]

        return None

    def search_video_commenters(self, video_id: str, limit: int = 20) -> List[Dict]:
        """
        获取视频的评论者

        Args:
            video_id: 视频ID
            limit: 数量限制

        Returns:
            评论者列表
        """
        if not self.api_key:
            logger.error("❌ YouTube API key required")
            return []

        commenters = []
        seen_channels = set()

        try:
            comments_url = f"{self.api_base}/commentThreads"
            params = {
                'key': self.api_key,
                'part': 'snippet',
                'videoId': video_id,
                'maxResults': limit,
                'order': 'relevance'
            }

            response = requests.get(
                comments_url,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                for item in items:
                    snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
                    channel_id = snippet.get('authorChannelId', {}).get('value')
                    author_name = snippet.get('authorDisplayName')

                    if channel_id and channel_id not in seen_channels:
                        commenters.append({
                            'channel_id': channel_id,
                            'channel_title': author_name,
                            'profile_url': f"https://www.youtube.com/channel/{channel_id}",
                            'platform': 'youtube'
                        })
                        seen_channels.add(channel_id)

        except Exception as e:
            logger.debug(f"   Error getting commenters: {e}")

        return commenters


# 测试代码
if __name__ == "__main__":
    scraper = YouTubeScraper()

    # 测试搜索创作者
    users = scraper.search_users(["startup", "entrepreneur"], limit=10)

    print(f"\n✅ Found {len(users)} creators:")
    for user in users:
        print(f"  - {user.get('channel_title')} ({user.get('subscriber_count', 0)} subscribers)")
        print(f"    URL: {user.get('profile_url')}")
