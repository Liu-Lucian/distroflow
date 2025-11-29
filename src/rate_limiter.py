"""Human-like rate limiting to avoid detection and respect API limits"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HumanLikeRateLimiter:
    """Rate limiter that mimics human behavior patterns"""

    def __init__(self):
        self.request_times: Dict[str, list] = {}
        self.last_request: Dict[str, float] = {}

    def wait_if_needed(
        self,
        endpoint: str,
        max_requests: int = 15,
        window_minutes: int = 15,
        min_delay: float = 2.0,
        max_delay: float = 8.0
    ):
        """
        Wait with human-like delays before making requests

        Args:
            endpoint: API endpoint name
            max_requests: Maximum requests allowed in window
            window_minutes: Time window in minutes
            min_delay: Minimum delay between requests (seconds)
            max_delay: Maximum delay between requests (seconds)
        """
        current_time = time.time()

        # Initialize tracking for this endpoint
        if endpoint not in self.request_times:
            self.request_times[endpoint] = []

        # Clean old requests outside the window
        window_seconds = window_minutes * 60
        cutoff_time = current_time - window_seconds
        self.request_times[endpoint] = [
            t for t in self.request_times[endpoint] if t > cutoff_time
        ]

        # Check if we're approaching the rate limit
        requests_in_window = len(self.request_times[endpoint])

        if requests_in_window >= max_requests - 1:
            # We're at the limit, wait until the oldest request expires
            oldest_request = min(self.request_times[endpoint])
            sleep_time = (oldest_request + window_seconds) - current_time + random.uniform(1, 5)

            if sleep_time > 0:
                logger.warning(f"Rate limit approaching for {endpoint}. Waiting {sleep_time:.1f}s...")
                self._human_like_sleep(sleep_time)

        # Add human-like delay between requests
        if endpoint in self.last_request:
            time_since_last = current_time - self.last_request[endpoint]
            needed_delay = self._calculate_human_delay(min_delay, max_delay)

            if time_since_last < needed_delay:
                sleep_time = needed_delay - time_since_last
                logger.debug(f"Human-like delay: {sleep_time:.2f}s")
                self._human_like_sleep(sleep_time)

        # Record this request
        self.request_times[endpoint].append(time.time())
        self.last_request[endpoint] = time.time()

    def _calculate_human_delay(self, min_delay: float, max_delay: float) -> float:
        """
        Calculate a human-like delay with realistic patterns

        Humans don't act at constant intervals. They have:
        - Variable response times
        - Occasional longer pauses
        - Clustering of activity
        """
        # 70% of time: normal delay range
        if random.random() < 0.7:
            return random.uniform(min_delay, max_delay)

        # 20% of time: slightly longer pause (reading, thinking)
        elif random.random() < 0.9:
            return random.uniform(max_delay, max_delay * 2)

        # 10% of time: much longer pause (distraction, break)
        else:
            return random.uniform(max_delay * 2, max_delay * 4)

    def _human_like_sleep(self, total_seconds: float):
        """
        Sleep in a human-like way with micro-breaks

        Humans don't wait perfectly still. They:
        - Have variable attention
        - Take micro-breaks
        - Resume activity with slight variations
        """
        if total_seconds < 5:
            # Short waits: just sleep with small random variation
            time.sleep(total_seconds + random.uniform(-0.1, 0.3))
            return

        # Long waits: break into chunks with variations
        remaining = total_seconds
        while remaining > 0:
            # Sleep in 30-60 second chunks for long waits
            chunk = min(remaining, random.uniform(30, 60))

            # Add progress indicator for very long waits
            if total_seconds > 60:
                mins_remaining = remaining / 60
                logger.info(f"⏳ Waiting {mins_remaining:.1f} more minutes to avoid rate limits...")

            time.sleep(chunk)
            remaining -= chunk

    def add_scroll_behavior(self, items_count: int):
        """
        Simulate human scrolling/browsing behavior

        Humans don't process items at constant speed
        """
        if items_count == 0:
            return

        # Vary reading speed based on position
        if items_count < 5:
            # First few items: read more carefully
            delay = random.uniform(1.5, 3.5)
        elif items_count < 20:
            # Middle items: moderate speed
            delay = random.uniform(0.8, 2.0)
        else:
            # Later items: faster scanning
            delay = random.uniform(0.3, 1.2)

        # 15% chance of longer pause (found something interesting)
        if random.random() < 0.15:
            delay *= random.uniform(1.5, 3.0)

        time.sleep(delay)

    def add_typing_delay(self, text_length: int):
        """
        Simulate human typing speed

        Average typing: 40-60 words per minute (3-5 chars/second)
        """
        # Assume average word length of 5 characters
        words = text_length / 5

        # 40-60 WPM = 0.67-1.0 words per second
        base_time = words / random.uniform(0.67, 1.0)

        # Add thinking pauses (humans pause while composing)
        thinking_pauses = random.randint(1, 3) * random.uniform(1, 3)

        total_delay = base_time + thinking_pauses
        time.sleep(total_delay)

    def should_take_break(self, actions_count: int, session_duration: float) -> bool:
        """
        Decide if human would take a break

        Args:
            actions_count: Number of actions taken in session
            session_duration: Time in seconds since session start

        Returns:
            True if should take a break
        """
        # Take break after 30-50 actions
        if actions_count >= random.randint(30, 50):
            return True

        # Take break after 20-40 minutes of activity
        if session_duration >= random.uniform(1200, 2400):
            return True

        # Random 5% chance of spontaneous break
        if random.random() < 0.05:
            return True

        return False

    def take_break(self):
        """
        Take a human-like break

        Humans take breaks of varying lengths:
        - Short break: 2-5 minutes (coffee, bathroom)
        - Medium break: 5-15 minutes (snack, chat)
        - Long break: 15-30 minutes (lunch, meeting)
        """
        break_type = random.choices(
            ['short', 'medium', 'long'],
            weights=[0.6, 0.3, 0.1]
        )[0]

        if break_type == 'short':
            duration = random.uniform(120, 300)  # 2-5 minutes
            logger.info("☕ Taking a short break (2-5 min) to appear more human...")
        elif break_type == 'medium':
            duration = random.uniform(300, 900)  # 5-15 minutes
            logger.info("🍪 Taking a medium break (5-15 min) to avoid detection...")
        else:
            duration = random.uniform(900, 1800)  # 15-30 minutes
            logger.info("🍽️  Taking a longer break (15-30 min) for natural behavior...")

        self._human_like_sleep(duration)

    def get_human_time_of_day_multiplier(self) -> float:
        """
        Adjust activity based on time of day

        Humans are more active during certain hours:
        - Night (12am-6am): Very slow (0.3x)
        - Early morning (6am-9am): Moderate (0.7x)
        - Working hours (9am-5pm): Normal (1.0x)
        - Evening (5pm-10pm): Moderate (0.8x)
        - Late night (10pm-12am): Slow (0.5x)
        """
        current_hour = datetime.now().hour

        if 0 <= current_hour < 6:
            return 0.3  # Night - very slow
        elif 6 <= current_hour < 9:
            return 0.7  # Early morning
        elif 9 <= current_hour < 17:
            return 1.0  # Working hours - normal
        elif 17 <= current_hour < 22:
            return 0.8  # Evening
        else:
            return 0.5  # Late night


# Singleton instance
rate_limiter = HumanLikeRateLimiter()


# Example usage and testing
if __name__ == "__main__":
    limiter = HumanLikeRateLimiter()

    print("Testing human-like rate limiting...")

    # Simulate 20 API calls
    for i in range(20):
        print(f"\nRequest {i+1}/20")

        # Wait with human-like behavior
        limiter.wait_if_needed(
            endpoint="search_tweets",
            max_requests=15,
            window_minutes=15,
            min_delay=2.0,
            max_delay=6.0
        )

        print(f"✓ Request {i+1} sent at {datetime.now().strftime('%H:%M:%S')}")

        # Simulate processing results
        limiter.add_scroll_behavior(i)

        # Check if should take break
        if limiter.should_take_break(i, time.time()):
            limiter.take_break()

    print("\n✅ Test complete! All requests sent with human-like timing.")
