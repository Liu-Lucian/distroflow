#!/usr/bin/env python3
"""
Substack Comment Farming System
Similar to Reddit karma farming - posts thoughtful comments on relevant articles
"""

import sys
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright
from openai import OpenAI
import json
import time
import os
import logging
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


# Configuration
TOPICS = [
    "AI",
    "startup",
    "technology",
    "interview",
    "career",
    "product management",
    "building in public"
]

COMMENTS_PER_RUN = 3  # How many comments to post per run
DELAY_BETWEEN_COMMENTS = (180, 300)  # Random delay 3-5 minutes
MIN_ARTICLE_LENGTH = 500  # Skip short articles


def find_relevant_posts(playwright):
    """
    Find Substack posts to comment on
    Strategy: Search for topics, find recent popular posts
    """

    logger.info("🔍 Finding relevant Substack posts to comment on...")

    # Load auth
    with open('substack_auth.json', 'r') as f:
        auth_data = json.load(f)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    context.add_cookies(auth_data['cookies'])
    page = context.new_page()

    posts = []

    try:
        # Go to Substack explore/discover page
        logger.info("   Going to Substack discover page...")
        page.goto("https://substack.com/discover", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)

        # Scroll to load more posts
        for i in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Find post links
        logger.info("   Extracting post links...")

        # Substack posts are typically in article cards
        post_links = page.query_selector_all('a[href*="/p/"]')

        seen_urls = set()
        for link in post_links[:20]:  # Check first 20 posts
            try:
                href = link.get_attribute('href')
                if not href or href in seen_urls:
                    continue

                # Make sure it's a full URL
                if not href.startswith('http'):
                    href = 'https://substack.com' + href

                # Get post title
                title_elem = link.query_selector('h2, h3, [class*="title"]')
                title = title_elem.inner_text().strip() if title_elem else "Untitled"

                posts.append({
                    'url': href,
                    'title': title
                })
                seen_urls.add(href)

            except Exception as e:
                continue

        logger.info(f"   ✅ Found {len(posts)} potential posts")

    except Exception as e:
        logger.error(f"❌ Error finding posts: {e}")
        import traceback
        traceback.print_exc()

    finally:
        browser.close()

    return posts


def get_article_content(playwright, post_url):
    """Extract article content for AI analysis"""

    logger.info(f"   📖 Reading article content...")

    # Load auth
    with open('substack_auth.json', 'r') as f:
        auth_data = json.load(f)

    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    context.add_cookies(auth_data['cookies'])
    page = context.new_page()

    try:
        # Set a page timeout to prevent hanging
        page.set_default_timeout(15000)  # 15 seconds max for any operation

        page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)

        # CRITICAL: Check for paywall FIRST before doing anything else
        logger.info(f"   🔍 Checking for paywall...")
        paywall_detected = False

        # Comprehensive paywall indicators
        paywall_indicators = [
            'text="Only paid subscribers can comment"',
            'text="paid subscribers can comment"',
            'text="Subscribe to comment"',
            'text="Subscribe to continue reading"',
            'text="This post is for paid subscribers"',
            'text="Upgrade to paid"',
            'text="This is a preview"',
            'text="for paying subscribers"',
            '[class*="paywall"]',
            '[class*="subscription-required"]',
            '[data-testid*="paywall"]'
        ]

        for indicator in paywall_indicators:
            try:
                elem = page.wait_for_selector(indicator, timeout=500)  # Quick check
                if elem and elem.is_visible():
                    logger.warning(f"   ⚠️  Paywall detected!")
                    paywall_detected = True
                    break
            except:
                continue

        if paywall_detected:
            browser.close()
            return "paywall"

        # Extract article title and content
        title = ""
        title_elem = page.query_selector('h1')
        if title_elem:
            title = title_elem.inner_text().strip()

        # Extract article body
        content = ""
        article_elem = page.query_selector('article, [class*="body"], [class*="post-content"]')
        if article_elem:
            content = article_elem.inner_text().strip()

        browser.close()

        # Double-check content isn't paywalled
        if not content or len(content) < 200:
            logger.warning(f"   ⚠️  Article too short or empty, might be paywalled")
            return "paywall"

        return {
            'title': title,
            'content': content[:3000],  # First 3000 chars
            'length': len(content)
        }

    except Exception as e:
        logger.error(f"   ❌ Error reading article: {e}")
        browser.close()
        return None


def generate_comment(article_info):
    """
    Use AI to generate a thoughtful, relevant comment
    Similar to Reddit farming - need to be genuine and add value
    """

    logger.info("   🤖 Generating comment with AI...")

    prompt = f"""
You are a Substack reader interested in AI, startups, and technology.

Article Title: {article_info['title']}
Article Content (excerpt):
{article_info['content'][:1500]}

Write a thoughtful comment for this article. Requirements:

1. Length: 50-150 words
2. Style: Casual, genuine, like a real person
3. Must add value: Ask an insightful question OR share a brief related experience OR provide a thoughtful observation
4. Don't be too praising or promotional
5. Sound natural and authentic
6. Don't start with "Great article" or similar cliches

Examples of good comments:
- "This resonates with my experience building an AI product last year. One thing I found challenging was balancing automation with human oversight. How did you approach this in your case?"
- "Interesting point about the interview prep angle. I wonder if this could also work for mock interviews, not just real ones?"
- "The STAR framework tip is spot on. I've seen so many candidates struggle with this in practice, even when they know the concept."

Write ONLY the comment text, nothing else.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
        )

        comment = response.choices[0].message.content.strip()

        # Remove quotes if AI wrapped it
        if comment.startswith('"') and comment.endswith('"'):
            comment = comment[1:-1]

        logger.info(f"   ✅ Generated comment ({len(comment)} chars)")
        logger.info(f"   Preview: {comment[:100]}...")

        return comment

    except Exception as e:
        logger.error(f"   ❌ Failed to generate comment: {e}")
        return None


def post_comment(playwright, post_url, comment_text):
    """Post a comment on a Substack article"""

    logger.info(f"\n💬 Posting comment...")

    # Load auth
    with open('substack_auth.json', 'r') as f:
        auth_data = json.load(f)

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    context.add_cookies(auth_data['cookies'])
    page = context.new_page()

    try:
        # Set timeout to prevent hanging
        page.set_default_timeout(15000)

        # Go to article
        logger.info("1. Opening article...")
        page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
        time.sleep(2)

        # Scroll down to comments section
        logger.info("2. Scrolling to comments section...")
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

        # Check for paywall (double-check, should already be caught earlier)
        logger.info("3. Checking for comment paywall...")
        paywall_detected = False
        paywall_indicators = [
            'text="Only paid subscribers can comment"',
            'text="paid subscribers can comment"',
            'text="Subscribe to comment"',
            'text="for paying subscribers"'
        ]

        for indicator in paywall_indicators:
            try:
                elem = page.wait_for_selector(indicator, timeout=1000)
                if elem and elem.is_visible():
                    logger.warning("   ⚠️  This post requires paid subscription to comment")
                    paywall_detected = True
                    break
            except:
                continue

        if paywall_detected:
            logger.warning("   ⚠️  Skipping paid-only post")
            browser.close()
            return "paywall"

        # Find comment textarea
        logger.info("4. Finding comment input...")

        comment_input_selectors = [
            'textarea[placeholder*="comment" i]',
            'textarea[placeholder*="write" i]',
            'div[contenteditable="true"]',
            '[class*="comment"] textarea',
            '[class*="editor"] textarea'
        ]

        comment_input = None
        for selector in comment_input_selectors:
            try:
                comment_input = page.wait_for_selector(selector, timeout=3000)
                if comment_input and comment_input.is_visible():
                    logger.info(f"   ✅ Found comment input: {selector}")
                    break
            except:
                continue

        if not comment_input:
            logger.error("   ❌ Could not find comment input")
            page.screenshot(path="comment_error_no_input.png")
            browser.close()
            return False

        # Click and type comment
        logger.info("5. Typing comment...")
        comment_input.click()
        time.sleep(1)
        comment_input.fill(comment_text)
        time.sleep(2)

        page.screenshot(path="comment_typed.png")
        logger.info("   📸 Screenshot: comment_typed.png")

        # Find and click submit button
        logger.info("6. Submitting comment...")

        submit_selectors = [
            'button:has-text("Post")',
            'button:has-text("Comment")',
            'button:has-text("Submit")',
            'button[type="submit"]'
        ]

        for selector in submit_selectors:
            try:
                btn = page.wait_for_selector(selector, timeout=2000)
                if btn and btn.is_visible():
                    logger.info(f"   ✅ Found submit button: {selector}")
                    btn.click()
                    time.sleep(3)
                    break
            except:
                continue

        page.screenshot(path="comment_submitted.png")
        logger.info("   📸 Screenshot: comment_submitted.png")

        logger.info("   ✅ Comment posted!")

        time.sleep(2)
        browser.close()
        return True

    except Exception as e:
        logger.error(f"❌ Error posting comment: {e}")
        import traceback
        traceback.print_exc()
        page.screenshot(path="comment_error.png")
        browser.close()
        return False


def load_commented_posts():
    """Load history of posts we've already commented on"""
    try:
        with open('substack_commented_posts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_commented_post(post_info):
    """Save post to commented history"""
    history = load_commented_posts()
    history.append({
        'url': post_info['url'],
        'title': post_info['title'],
        'commented_at': datetime.now().isoformat()
    })

    with open('substack_commented_posts.json', 'w') as f:
        json.dump(history, f, indent=2)


def main():
    """Main farming loop"""

    logger.info("="*80)
    logger.info("🌾 Substack Comment Farmer")
    logger.info("="*80)
    logger.info(f"Will post {COMMENTS_PER_RUN} comments this run")
    logger.info(f"Delay between comments: {DELAY_BETWEEN_COMMENTS[0]}-{DELAY_BETWEEN_COMMENTS[1]}s")
    logger.info("")

    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        return

    playwright = sync_playwright().start()

    # Find posts
    posts = find_relevant_posts(playwright)

    if not posts:
        logger.error("❌ No posts found")
        playwright.stop()
        return

    # Load history to avoid duplicate comments
    commented_urls = {p['url'] for p in load_commented_posts()}

    # Filter out already commented posts
    new_posts = [p for p in posts if p['url'] not in commented_urls]

    if not new_posts:
        logger.warning("⚠️  All found posts have already been commented on")
        logger.info("💡 Try again later or clear substack_commented_posts.json")
        playwright.stop()
        return

    logger.info(f"📊 {len(new_posts)} new posts available (filtered {len(posts) - len(new_posts)} already commented)")

    # Comment on posts
    comments_posted = 0
    posts_attempted = 0

    for post in new_posts:
        # Stop if we've posted enough comments
        if comments_posted >= COMMENTS_PER_RUN:
            break

        posts_attempted += 1
        logger.info("\n" + "="*80)
        logger.info(f"📝 Attempt {posts_attempted} (Posted: {comments_posted}/{COMMENTS_PER_RUN})")
        logger.info("="*80)
        logger.info(f"Post: {post['title']}")
        logger.info(f"URL: {post['url']}")

        # Get article content
        article_info = get_article_content(playwright, post['url'])

        # Check if article is paywalled (detected early)
        if article_info == "paywall":
            logger.warning("   ⚠️  Article is paywalled, skipping to next...")
            continue

        if not article_info:
            logger.warning("   ⚠️  Could not read article, skipping...")
            continue

        if article_info['length'] < MIN_ARTICLE_LENGTH:
            logger.warning(f"   ⚠️  Article too short ({article_info['length']} chars), skipping...")
            continue

        logger.info(f"   ✅ Article readable, length: {article_info['length']} chars")

        # Generate comment
        comment = generate_comment(article_info)

        if not comment:
            logger.warning("   ⚠️  Could not generate comment, skipping...")
            continue

        # Post comment
        result = post_comment(playwright, post['url'], comment)

        if result == "paywall":
            logger.warning(f"\n⚠️  Post is paid-only, skipping to next...")
            # Don't count as posted, don't save to history, continue to next
            continue
        elif result:
            logger.info(f"\n✅ Comment posted successfully! ({comments_posted + 1}/{COMMENTS_PER_RUN})")
            save_commented_post(post)
            comments_posted += 1

            # Random delay before next comment (except if we're done)
            if comments_posted < COMMENTS_PER_RUN:
                delay = random.randint(*DELAY_BETWEEN_COMMENTS)
                logger.info(f"\n⏳ Waiting {delay}s before next comment...")
                time.sleep(delay)
        else:
            logger.error(f"\n❌ Failed to post comment, trying next post...")

    playwright.stop()

    logger.info("\n" + "="*80)
    logger.info(f"✅ Farming session complete!")
    logger.info(f"📊 Comments posted: {comments_posted}/{COMMENTS_PER_RUN}")
    logger.info("="*80)


if __name__ == "__main__":
    main()
