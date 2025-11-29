"""Twitter API client for searching and scraping"""

import tweepy
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
from .config import config
from .rate_limiter import rate_limiter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterClient:
    """Manage Twitter API interactions"""

    def __init__(self):
        """Initialize Twitter API client"""
        # OAuth 1.0a User Context
        auth = tweepy.OAuthHandler(
            config.TWITTER_API_KEY,
            config.TWITTER_API_SECRET
        )
        auth.set_access_token(
            config.TWITTER_ACCESS_TOKEN,
            config.TWITTER_ACCESS_TOKEN_SECRET
        )

        # Create API v1.1 client (for some operations)
        self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)

        # Create API v2 client (for better features)
        self.api_v2 = tweepy.Client(
            bearer_token=config.TWITTER_BEARER_TOKEN,
            consumer_key=config.TWITTER_API_KEY,
            consumer_secret=config.TWITTER_API_SECRET,
            access_token=config.TWITTER_ACCESS_TOKEN,
            access_token_secret=config.TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )

    def search_influencers(
        self,
        query: str,
        max_results: int = 20,
        min_followers: int = 1000
    ) -> List[Dict]:
        """
        Search for influencers based on keywords

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            min_followers: Minimum follower count

        Returns:
            List of user dictionaries with profile information
        """
        influencers = []

        try:
            # Human-like delay before searching
            rate_limiter.wait_if_needed(
                endpoint="search_tweets",
                max_requests=15,
                window_minutes=15,
                min_delay=3.0,
                max_delay=8.0
            )

            # Twitter API requires max_results between 10-100
            api_max_results = min(max(max_results, 10), 100)

            # Search for tweets with the query
            tweets = self.api_v2.search_recent_tweets(
                query=query,
                max_results=api_max_results,
                tweet_fields=['author_id', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name', 'description', 'public_metrics', 'profile_image_url']
            )

            if not tweets.data:
                logger.warning(f"No tweets found for query: {query}")
                return []

            # Extract unique users
            seen_users = set()
            users = tweets.includes['users'] if tweets.includes else []

            for user in users:
                if user.id in seen_users:
                    continue

                metrics = user.public_metrics
                if metrics['followers_count'] >= min_followers:
                    influencers.append({
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'description': user.description or '',
                        'followers_count': metrics['followers_count'],
                        'following_count': metrics['following_count'],
                        'tweet_count': metrics['tweet_count'],
                        'profile_image_url': user.profile_image_url,
                        'found_via': query
                    })
                    seen_users.add(user.id)

            logger.info(f"Found {len(influencers)} influencers for query: {query}")

        except Exception as e:
            logger.error(f"Error searching influencers: {e}")

        return influencers[:max_results]

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """
        Get detailed user information by username

        Args:
            username: Twitter username (without @)

        Returns:
            User dictionary or None
        """
        try:
            # Human-like delay
            rate_limiter.wait_if_needed(
                endpoint="get_user",
                max_requests=300,
                window_minutes=15,
                min_delay=1.0,
                max_delay=3.0
            )

            user = self.api_v2.get_user(
                username=username,
                user_fields=['description', 'public_metrics', 'profile_image_url', 'url']
            )

            if not user.data:
                return None

            u = user.data
            metrics = u.public_metrics

            return {
                'id': u.id,
                'username': u.username,
                'name': u.name,
                'description': u.description or '',
                'followers_count': metrics['followers_count'],
                'following_count': metrics['following_count'],
                'tweet_count': metrics['tweet_count'],
                'profile_image_url': u.profile_image_url,
                'url': u.url if hasattr(u, 'url') else None
            }

        except Exception as e:
            logger.error(f"Error fetching user {username}: {e}")
            return None

    def get_followers(
        self,
        user_id: str,
        max_followers: int = 500
    ) -> List[Dict]:
        """
        Get followers of a user

        Args:
            user_id: Twitter user ID
            max_followers: Maximum number of followers to fetch

        Returns:
            List of follower dictionaries
        """
        followers = []
        pagination_token = None

        try:
            while len(followers) < max_followers:
                # Human-like delay before each page
                rate_limiter.wait_if_needed(
                    endpoint="get_followers",
                    max_requests=15,
                    window_minutes=15,
                    min_delay=4.0,
                    max_delay=12.0
                )

                # Fetch up to 1000 followers per request (API limit)
                results_per_page = min(1000, max_followers - len(followers))

                response = self.api_v2.get_users_followers(
                    id=user_id,
                    max_results=results_per_page,
                    pagination_token=pagination_token,
                    user_fields=['username', 'name', 'description', 'public_metrics', 'profile_image_url']
                )

                if not response.data:
                    break

                for user in response.data:
                    metrics = user.public_metrics
                    followers.append({
                        'id': user.id,
                        'username': user.username,
                        'name': user.name,
                        'description': user.description or '',
                        'followers_count': metrics['followers_count'],
                        'following_count': metrics['following_count'],
                        'tweet_count': metrics['tweet_count'],
                        'profile_image_url': user.profile_image_url,
                        'scraped_at': datetime.now().isoformat()
                    })

                # Check if there are more pages
                if 'next_token' not in response.meta:
                    break

                pagination_token = response.meta['next_token']

                logger.info(f"Fetched {len(followers)} followers so far...")

                # Simulate human browsing behavior
                rate_limiter.add_scroll_behavior(len(followers))

        except Exception as e:
            logger.error(f"Error fetching followers: {e}")

        logger.info(f"Total followers fetched: {len(followers)}")
        return followers

    def follow_user(self, target_user_id: str) -> bool:
        """
        Follow a user with human-like behavior

        Args:
            target_user_id: ID of user to follow

        Returns:
            Success status
        """
        try:
            # Human-like delay (humans don't follow instantly)
            rate_limiter.wait_if_needed(
                endpoint="follow_user",
                max_requests=50,
                window_minutes=1440,  # 24 hours
                min_delay=10.0,
                max_delay=30.0
            )

            # Get authenticated user ID
            me = self.api_v2.get_me()
            self.api_v2.follow_user(target_user_id)
            logger.info(f"Successfully followed user {target_user_id}")
            return True
        except Exception as e:
            logger.error(f"Error following user: {e}")
            return False

    def send_dm(self, recipient_id: str, message: str) -> bool:
        """
        Send a direct message with human-like typing

        Args:
            recipient_id: ID of message recipient
            message: Message text

        Returns:
            Success status
        """
        try:
            # Simulate human typing the message
            rate_limiter.add_typing_delay(len(message))

            # Human-like delay between DMs
            rate_limiter.wait_if_needed(
                endpoint="send_dm",
                max_requests=500,
                window_minutes=1440,  # 24 hours
                min_delay=30.0,
                max_delay=120.0
            )

            # Using API v1.1 for DMs
            self.api_v1.send_direct_message(recipient_id, message)
            logger.info(f"Successfully sent DM to {recipient_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return False

    def like_tweet(self, tweet_id: str) -> bool:
        """
        Like a tweet with human-like behavior

        Args:
            tweet_id: ID of tweet to like

        Returns:
            Success status
        """
        try:
            # Human-like delay (people read before liking)
            rate_limiter.wait_if_needed(
                endpoint="like_tweet",
                max_requests=1000,
                window_minutes=1440,  # 24 hours
                min_delay=5.0,
                max_delay=20.0
            )

            self.api_v2.like(tweet_id)
            logger.info(f"Successfully liked tweet {tweet_id}")
            return True
        except Exception as e:
            logger.error(f"Error liking tweet: {e}")
            return False

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> List[Dict]:
        """
        Get recent tweets from a user

        Args:
            user_id: Twitter user ID
            max_results: Maximum tweets to fetch

        Returns:
            List of tweet dictionaries
        """
        try:
            tweets = self.api_v2.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics']
            )

            if not tweets.data:
                return []

            return [
                {
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count']
                }
                for tweet in tweets.data
            ]

        except Exception as e:
            logger.error(f"Error fetching user tweets: {e}")
            return []


# Example usage
if __name__ == "__main__":
    client = TwitterClient()

    # Search for influencers
    influencers = client.search_influencers("AI automation", max_results=5)
    print(f"Found {len(influencers)} influencers")

    if influencers:
        # Get followers of first influencer
        first_influencer = influencers[0]
        print(f"\nFetching followers of @{first_influencer['username']}...")
        followers = client.get_followers(first_influencer['id'], max_followers=10)
        print(f"Fetched {len(followers)} followers")
