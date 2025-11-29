#!/usr/bin/env python3
"""
Reddit智能养号系统 - 自动发评论积累Karma
策略：AI分析热门帖子，生成有价值/搞笑评论
"""
import sys
sys.path.insert(0, 'src')
from reddit_poster import RedditPoster
import time
import logging
import random
from openai import OpenAI
import os
from reddit_comment_button_finder import click_comment_button_with_ai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RedditKarmaFarmer:
    def __init__(self):
        self.poster = RedditPoster()
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        # 适合养号的热门板块（容易涨karma）
        self.target_subreddits = [
            'AskReddit',           # 最容易涨karma
            'technology',          # 科技相关，契合你的产品
            'programming',         # 技术讨论
            'webdev',             # Web开发
            'startups',           # 创业（混脸熟）
            'Entrepreneur',       # 创业者社区
            'artificial',         # AI讨论
            'MachineLearning',    # ML社区
            'todayilearned',      # 轻松内容
            'explainlikeimfive'   # 简单解释类
        ]

    def get_hot_posts(self, subreddit, limit=10):
        """获取热门帖子"""
        logger.info(f"👀 yo let's check out r/{subreddit} hot posts rn...")

        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot"
            self.poster.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            posts = []

            # 获取帖子列表（使用shreddit-post，Reddit新UI）
            post_selectors = [
                'shreddit-post',              # Reddit新UI（最优先）
                'div[data-testid="post-container"]',
                'article',
                'div.Post'
            ]

            post_elements = None
            for selector in post_selectors:
                post_elements = self.poster.page.query_selector_all(selector)
                if post_elements and len(post_elements) > 0:
                    logger.info(f"   ✅ 使用选择器: {selector}")
                    break

            if not post_elements:
                logger.error(f"   ❌ 找不到帖子元素")
                return []

            logger.info(f"   ✅ 找到 {len(post_elements)} 个帖子")

            for i, post_elem in enumerate(post_elements[:limit]):
                try:
                    # 获取标题 - 尝试多种选择器
                    title_selectors = [
                        'h3',
                        '[slot="title"]',
                        'a[slot="full-post-link"]',
                        'div[slot="title"]',
                        'a[data-click-id="body"]',
                        'a[href*="/comments/"]'
                    ]

                    title = None
                    title_elem = None
                    for selector in title_selectors:
                        title_elem = post_elem.query_selector(selector)
                        if title_elem:
                            title = title_elem.inner_text().strip()
                            if title and len(title) > 5:  # 确保不是空标题
                                break

                    if not title:
                        # 调试：打印元素HTML看看结构
                        # logger.debug(f"   ⚠️  帖子 {i+1} 没有标题，跳过")
                        continue

                    # 获取帖子链接
                    link_elem = post_elem.query_selector('a[href*="/comments/"]')
                    if not link_elem and title_elem and title_elem.get_attribute('href'):
                        link_elem = title_elem

                    if not link_elem:
                        continue

                    post_url = link_elem.get_attribute('href')
                    if not post_url:
                        continue

                    if not post_url.startswith('http'):
                        post_url = f"https://www.reddit.com{post_url}"

                    # 获取upvote数（作为热度指标）
                    upvote_text = "?"
                    upvote_selectors = [
                        'faceplate-number',
                        'div[id*="vote"]',
                        'button[aria-label*="upvote"]',
                        'shreddit-score'
                    ]
                    for selector in upvote_selectors:
                        upvote_elem = post_elem.query_selector(selector)
                        if upvote_elem:
                            upvote_text = upvote_elem.inner_text().strip()
                            if upvote_text:
                                break

                    posts.append({
                        'title': title,
                        'url': post_url,
                        'upvotes': upvote_text,
                        'subreddit': subreddit
                    })

                    logger.info(f"   📝 {i+1}. {title[:60]}... ({upvote_text} upvotes ngl)")

                except Exception as e:
                    # logger.debug(f"   ⚠️  处理帖子 {i+1} 出错: {str(e)}")
                    continue

            return posts

        except Exception as e:
            logger.error(f"   ❌ 获取帖子失败: {str(e)}")
            return []

    def analyze_and_generate_comment(self, post_title, post_content=""):
        """AI分析帖子并生成评论"""
        logger.info("🤖 AI cooking up some comments lol...")

        prompt = f"""You are a chill Reddit community member. Analyze this post and write a GENUINE, VALUABLE comment.

Post Title: {post_title}

Requirements:
1. **Be authentic** - Sound like a real person, not a bot
2. **Add value** - Share insight, experience, or helpful perspective
3. **Be conversational** - Use natural language, contractions, casual tone
4. **Keep it concise** - 2-4 sentences max
5. **NO promotion** - Don't mention any products/services
6. **Match the vibe** - If it's serious, be helpful. If it's fun, be witty
7. **NO PERIODS at the end** - Don't end sentences with periods, keep it casual and relaxed (just let sentences flow naturally or end with "lol", "tbh", "ngl", etc)
8. **Use internet slang naturally** - Sprinkle in casual terms like "ngl", "tbh", "fr", "lol" when appropriate
9. **NO EMOJIS** - Never use emojis in the comment, keep it text only

Comment types that work well:
- Share personal experience ("I had this happen too...")
- Ask clarifying question ("Have you tried...?")
- Offer helpful tip ("Pro tip: ...")
- Make witty/funny observation (if appropriate)
- Show genuine curiosity ("This is interesting ngl")

Output ONLY the comment text (no quotes, no meta-commentary):"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,  # Higher for more natural variation
                max_tokens=150
            )

            comment = response.choices[0].message.content.strip()

            # Remove quotes if AI added them
            if comment.startswith('"') and comment.endswith('"'):
                comment = comment[1:-1]
            if comment.startswith("'") and comment.endswith("'"):
                comment = comment[1:-1]

            logger.info(f"   ✅ got it: {comment[:80]}... (sounds legit fr fr)")
            return comment

        except Exception as e:
            logger.error(f"   ❌ 生成评论失败: {str(e)}")
            return None

    def post_comment(self, post_url, comment_text):
        """发布评论到帖子"""
        logger.info(f"💬 bout to yeet this comment: {post_url[:60]}...")

        try:
            # 访问帖子
            self.poster.page.goto(post_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # 往下翻一点（找"Share your thoughts"输入框）
            logger.info("   📜 scrolling down a bit...")
            self.poster.page.evaluate("window.scrollBy(0, 400)")
            time.sleep(2)

            # 直接查找所有textarea然后手动筛选"Share your thoughts"
            logger.info("   🔍 hunting for that comment box...")

            # 等待页面加载textarea
            time.sleep(2)

            textareas = self.poster.page.query_selector_all('textarea')
            logger.info(f"   found {len(textareas)} textareas tbh")

            comment_box = None
            for i, ta in enumerate(textareas):
                placeholder = ta.get_attribute('placeholder') or ''
                is_visible = ta.is_visible()
                logger.info(f"      textarea {i}: placeholder='{placeholder}' visible={is_visible}")

                if 'Share your thoughts' in placeholder and is_visible:
                    logger.info(f"   ✅ gotcha! found the comment box (textarea {i})")
                    comment_box = ta
                    break
                elif 'Share your thoughts' in placeholder:
                    logger.info(f"      ⚠️  found it but hidden, lemme scroll...")
                    try:
                        ta.scroll_into_view_if_needed()
                        time.sleep(1)
                        if ta.is_visible():
                            logger.info(f"   ✅ nice! it's visible now")
                            comment_box = ta
                            break
                    except:
                        pass

            if not comment_box:
                logger.error("   ❌ bruh can't find the comment box")
                return False

            # 输入评论（模拟真人打字）
            comment_box.click()
            time.sleep(1)

            # 对于shreddit-composer，需要找到内部的textarea
            if 'shreddit-composer' in str(comment_box):
                logger.info("   ✏️  using shreddit-composer...")
                # 尝试找到内部的textarea
                textarea = comment_box.query_selector('faceplate-textarea')
                if textarea:
                    textarea.click()
                    time.sleep(0.5)

            # 输入文本
            self.poster.page.keyboard.type(comment_text, delay=random.randint(30, 80))
            time.sleep(2)

            # 点击发布按钮（Reddit新UI）
            logger.info("   🔍 looking for that submit button...")
            submit_selectors = [
                'button[slot="submit"]',           # Reddit新UI提交按钮
                'shreddit-composer button[type="submit"]',
                'button:has-text("Comment")',
                'button[type="submit"]',
                'button:has-text("Reply")'
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.poster.page.query_selector(selector)
                    if submit_button and submit_button.is_visible() and not submit_button.is_disabled():
                        logger.info(f"   ✅ ez! found it: {selector}")
                        break
                except:
                    continue

            if not submit_button:
                logger.error("   ❌ yo where's the submit button lol")
                # 尝试查找所有按钮
                all_buttons = self.poster.page.query_selector_all('button')
                logger.info(f"   💡 there's like {len(all_buttons)} buttons here")
                return False

            submit_button.click()
            time.sleep(3)

            # 检查是否成功（页面刷新或出现新评论）
            logger.info("   ✅ comment posted gg!")
            return True

        except Exception as e:
            logger.error(f"   ❌ oof posting failed: {str(e)}")
            return False

    def run_karma_farming_session(self, comments_per_session=3):
        """运行一次养号会话"""
        logger.info("=" * 80)
        logger.info("🚀 Reddit karma farming session let's goooo")
        logger.info("=" * 80)

        try:
            # 启动浏览器
            if not self.poster.browser:
                self.poster.setup_browser(headless=False)

                if not self.poster.verify_login():
                    logger.error("❌ login failed rip")
                    return False

            total_comments_posted = 0

            # 随机选择板块
            selected_subreddits = random.sample(
                self.target_subreddits,
                min(3, len(self.target_subreddits))
            )

            for subreddit in selected_subreddits:
                if total_comments_posted >= comments_per_session:
                    break

                logger.info(f"\n{'='*80}")
                logger.info(f"📍 checking out r/{subreddit} rn")
                logger.info(f"{'='*80}\n")

                # 获取热门帖子
                posts = self.get_hot_posts(subreddit, limit=5)

                if not posts:
                    logger.warning(f"⚠️  no posts found in r/{subreddit}, skipping lol")
                    continue

                # 随机选择1-2个帖子评论
                posts_to_comment = random.sample(posts, min(2, len(posts)))

                for post in posts_to_comment:
                    if total_comments_posted >= comments_per_session:
                        break

                    logger.info(f"\n📝 working on: {post['title'][:60]}...")

                    # AI生成评论
                    comment = self.analyze_and_generate_comment(post['title'])

                    if not comment:
                        logger.warning("   ⚠️  AI failed to generate comment, skip")
                        continue

                    # 发布评论
                    success = self.post_comment(post['url'], comment)

                    if success:
                        total_comments_posted += 1
                        logger.info(f"\n✅ nice! posted {total_comments_posted}/{comments_per_session} so far")

                        # 随机等待（2-5分钟，模拟真人行为）
                        if total_comments_posted < comments_per_session:
                            wait_time = random.randint(120, 300)
                            logger.info(f"⏳ brb taking a {wait_time//60} min break...\n")
                            time.sleep(wait_time)
                    else:
                        logger.warning("   ⚠️  posting failed, moving on")

                    # 短暂停顿
                    time.sleep(random.randint(5, 10))

            logger.info("\n" + "=" * 80)
            logger.info(f"✅ session done! posted {total_comments_posted} comments gg")
            logger.info("=" * 80)

            return True

        except Exception as e:
            logger.error(f"❌ session crashed rip: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_daily_farming(self, sessions_per_day=3, comments_per_session=3):
        """每日养号计划"""
        logger.info("=" * 80)
        logger.info("🌱 Daily Reddit karma farming plan glhf")
        logger.info("=" * 80)
        logger.info(f"📅 {sessions_per_day} sessions per day")
        logger.info(f"💬 {comments_per_session} comments per session")
        logger.info(f"📊 total {sessions_per_day * comments_per_session} comments per day ez")
        logger.info("=" * 80)

        for session in range(sessions_per_day):
            logger.info(f"\n\n🔄 starting session {session+1}/{sessions_per_day}...")

            success = self.run_karma_farming_session(comments_per_session)

            if not success:
                logger.error("❌ session failed oof")

            # 如果不是最后一个会话，等待一段时间
            if session < sessions_per_day - 1:
                # 会话间隔：2-4小时
                wait_hours = random.uniform(2, 4)
                wait_seconds = int(wait_hours * 3600)
                logger.info(f"\n⏰ taking a {wait_hours:.1f} hour break before next session...")
                logger.info(f"   (press Ctrl+C to stop btw)\n")
                time.sleep(wait_seconds)

        logger.info("\n\n" + "=" * 80)
        logger.info("✅ today's farming complete gg wp!")
        logger.info("💡 run again tomorrow same time fr")
        logger.info("=" * 80)

    def close(self):
        """关闭浏览器"""
        if self.poster:
            try:
                self.poster.close_browser()
            except:
                pass

if __name__ == "__main__":
    farmer = RedditKarmaFarmer()

    try:
        # 运行每日养号计划
        # 每天3个会话，每个会话3条评论 = 每天9条评论
        farmer.run_daily_farming(sessions_per_day=3, comments_per_session=3)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  user interrupted, peace out...")
    finally:
        farmer.close()
        logger.info("\n✅ karma farming stopped cya")
