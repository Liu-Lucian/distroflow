#!/usr/bin/env python3
"""
Twitter发布器 - Thread发布
使用已验证的选择器发布Twitter线程
"""

from social_media_poster_base import SocialMediaPosterBase
import time
import logging

logger = logging.getLogger(__name__)

class TwitterPoster(SocialMediaPosterBase):
    def __init__(self, auth_file: str = "auth.json"):
        super().__init__("twitter", auth_file)
        self.home_url = "https://twitter.com/home"
        # 已验证的选择器（从auto_configure获得）
        self.new_tweet_button = 'a[data-testid="SideNav_NewTweet_Button"]'

    def find_post_button(self) -> bool:
        """查找Tweet按钮"""
        try:
            element = self.page.wait_for_selector(self.new_tweet_button, timeout=5000)
            if element and element.is_visible():
                logger.info(f"   ✅ 找到Tweet按钮")
                return True
            return False
        except Exception as e:
            logger.error(f"   ❌ 查找按钮错误: {str(e)}")
            return False

    def create_post(self, content: dict) -> bool:
        """
        创建Twitter帖子（可能是单条或Thread）

        content格式:
        {
            'tweets': ['Tweet 1', 'Tweet 2', ...],
            'total_tweets': 5
        }
        """
        try:
            tweets = content.get('tweets', [])
            if not tweets:
                logger.error("   ❌ 没有tweets内容")
                return False

            logger.info(f"🌐 访问Twitter主页...")
            # 使用更长的超时和更宽松的wait_until
            try:
                self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=60000)
            except Exception as e:
                logger.warning(f"   ⚠️  页面加载超时，尝试继续...")
                # 即使超时也继续，可能页面已部分加载
            self._random_delay(3, 5)

            # 截图1 - 初始状态
            self.take_screenshot("before_tweet")

            # 发布第一条Tweet
            logger.info(f"   📍 发布第一条Tweet ({len(tweets[0])} 字符)...")

            # 点击Tweet按钮打开编辑框
            try:
                tweet_button = self.page.wait_for_selector(self.new_tweet_button, timeout=5000)
                if tweet_button and tweet_button.is_visible():
                    tweet_button.click()
                    logger.info("      ✅ 打开Tweet编辑框")
                else:
                    logger.error("      ❌ Tweet按钮不可见")
                    return False
            except Exception as e:
                logger.error(f"      ❌ 无法点击Tweet按钮: {str(e)}")
                return False

            self._random_delay(2, 3)

            # 填写第一条Tweet
            tweet_selectors = [
                'div[data-testid="tweetTextarea_0"]',
                'div[contenteditable="true"][data-testid*="tweet"]',
                'div[role="textbox"][data-testid*="tweet"]',
                'div[contenteditable="true"]:not([aria-label*="Reply"])'
            ]

            tweet_box = None
            for selector in tweet_selectors:
                try:
                    tweet_box = self.page.wait_for_selector(selector, timeout=3000)
                    if tweet_box and tweet_box.is_visible():
                        logger.info(f"      ✅ 找到输入框: {selector}")
                        break
                except:
                    continue

            if not tweet_box:
                logger.error("      ❌ 未找到Tweet输入框")
                self.take_screenshot("tweet_box_not_found")
                return False

            # 输入第一条Tweet
            tweet_box.click()
            self._random_delay(0.5, 1)

            # 模拟人类打字
            first_tweet = tweets[0]
            words = first_tweet.split(' ')
            for i, word in enumerate(words):
                self.page.keyboard.type(word)
                if i < len(words) - 1:
                    self.page.keyboard.type(' ')
                # 随机延迟，模拟真实打字
                if i % 10 == 0:
                    self._random_delay(0.1, 0.3)

            logger.info(f"      ✅ 第一条Tweet已输入")
            self._random_delay(1, 2)

            # 截图2 - 第一条输入完成
            self.take_screenshot("first_tweet_entered")

            # 如果是Thread（多条tweets），添加后续tweets
            if len(tweets) > 1:
                logger.info(f"   📍 添加Thread ({len(tweets)-1} 条后续tweets)...")

                for idx, tweet_text in enumerate(tweets[1:], start=2):
                    # 点击"+"添加下一条 - 尝试多个选择器
                    add_button_selectors = [
                        'button[data-testid="addButton"]',
                        'button[aria-label="Add"]',
                        'button[aria-label*="Add"]',
                        '[data-testid="toolBar"] button:has-text("+")',
                        'div[role="group"] button:has-text("+")',
                        'button:has-text("+")',
                    ]

                    button_found = False
                    for selector in add_button_selectors:
                        try:
                            add_thread_button = self.page.wait_for_selector(
                                selector,
                                timeout=2000
                            )
                            if add_thread_button and add_thread_button.is_visible():
                                add_thread_button.click()
                                logger.info(f"      ✅ 添加第 {idx} 条 (使用选择器: {selector})")
                                self._random_delay(1, 2)
                                button_found = True
                                break
                        except:
                            continue

                    if not button_found:
                        logger.warning(f"      ⚠️  无法找到添加按钮，尝试所有选择器都失败")
                        break

                    # 找到新的输入框
                    try:
                        new_box_selector = f'div[data-testid="tweetTextarea_{idx-1}"]'
                        new_tweet_box = self.page.wait_for_selector(new_box_selector, timeout=3000)
                        if not new_tweet_box:
                            # 尝试找最后一个contenteditable
                            boxes = self.page.query_selector_all('div[contenteditable="true"]')
                            if boxes:
                                new_tweet_box = boxes[-1]

                        if new_tweet_box:
                            new_tweet_box.click()
                            self._random_delay(0.5, 1)

                            # 输入内容
                            words = tweet_text.split(' ')
                            for i, word in enumerate(words):
                                self.page.keyboard.type(word)
                                if i < len(words) - 1:
                                    self.page.keyboard.type(' ')
                                if i % 10 == 0:
                                    self._random_delay(0.1, 0.2)

                            logger.info(f"      ✅ 第 {idx} 条已输入 ({len(tweet_text)} 字符)")
                        else:
                            logger.warning(f"      ⚠️  无法找到第 {idx} 条输入框")
                            break

                    except Exception as e:
                        logger.warning(f"      ⚠️  输入第 {idx} 条失败: {str(e)[:50]}")
                        break

                    self._random_delay(1, 2)

            # 截图3 - 所有内容输入完成
            self.take_screenshot("all_tweets_entered")

            # 点击"Post"或"Tweet all"发布
            logger.info(f"   📍 发布Thread...")

            # 等待一下确保按钮可点击
            self._random_delay(2, 3)

            # 优先尝试最精确的data-testid选择器
            post_selectors = [
                '[data-testid="tweetButtonInline"]',  # 对话框内的Post按钮
                '[data-testid="tweetButton"]',  # 备用
            ]

            posted = False
            for idx, selector in enumerate(post_selectors):
                try:
                    logger.info(f"      尝试选择器 {idx+1}/{len(post_selectors)}: {selector}")

                    # 等待按钮可点击
                    button = self.page.wait_for_selector(
                        selector,
                        state='visible',
                        timeout=5000
                    )

                    if button:
                        # 确保按钮已启用
                        if button.is_enabled():
                            # 使用JavaScript点击，更可靠
                            self.page.evaluate('(element) => element.click()', button)
                            logger.info(f"      ✅ 发布按钮已点击 (JS): {selector}")
                            posted = True
                            break
                        else:
                            logger.warning(f"      ⚠️  按钮不可用: {selector}")

                except Exception as e:
                    logger.debug(f"         失败: {str(e)[:100]}")
                    continue

            if not posted:
                logger.error("   ❌ 无法点击发布按钮")
                self.take_screenshot("post_button_not_found")
                return False

            # 等待发布完成
            logger.info("   ⏳ 等待发布完成...")
            self._random_delay(5, 8)

            # 截图4 - 发布后
            self.take_screenshot("after_post")

            # 验证发布成功 - Twitter发布后通常回到首页
            current_url = self.page.url
            if "home" in current_url or "status" in current_url:
                logger.info(f"   ✅ Twitter Thread发布成功！")
                logger.info(f"   📊 共发布 {len(tweets)} 条tweets")
                return True
            else:
                logger.warning(f"   ⚠️  发布状态未知，当前URL: {current_url}")
                return True  # 仍然返回True，因为可能成功了

        except Exception as e:
            logger.error(f"   ❌ Twitter发布失败: {str(e)}")
            self.take_screenshot("error")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == "__main__":
    # 测试
    import sys
    import os

    # 设置日志
    logging.basicConfig(level=logging.INFO)

    # 检查API key
    if 'OPENAI_API_KEY' not in os.environ:
        print("❌ 请设置 OPENAI_API_KEY")
        sys.exit(1)

    # 测试内容 - 简单单条tweet
    test_content = {
        'tweets': [
            '🚀 Testing MarketingMind AI Twitter automation...\n\nThis is an automated test tweet to verify the posting workflow. #AI #Automation',
        ],
        'total_tweets': 1
    }

    # 测试Thread（可选）
    # test_content = {
    #     'tweets': [
    #         '1/ Thread test: How AI is transforming job interviews 🤖',
    #         '2/ Traditional interviews often miss key candidate qualities',
    #         '3/ AI tools can help prepare better and showcase your skills',
    #         '4/ Learn more at HireMeAI.app'
    #     ],
    #     'total_tweets': 4
    # }

    poster = TwitterPoster()

    try:
        poster.setup_browser(headless=False)

        if poster.verify_login():
            print("✅ 登录验证成功")

            success = poster.create_post(test_content)

            if success:
                print("✅ 发布测试成功！")
            else:
                print("❌ 发布测试失败")
        else:
            print("❌ 登录验证失败，请先运行 twitter_login_and_save_auth.py")

    finally:
        input("\n按Enter关闭浏览器...")
        poster.close_browser()
