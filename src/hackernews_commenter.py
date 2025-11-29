#!/usr/bin/env python3
"""
Hacker News 评论器 - 基于 Playwright 的自动化评论系统
遵循 HN 社区规范：技术讨论优先，反营销
"""
from playwright.sync_api import sync_playwright
import json
import time
import logging
import random
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HackerNewsCommenter:
    def __init__(self, auth_file='hackernews_auth.json'):
        self.auth_file = auth_file
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.base_url = "https://news.ycombinator.com"

    def load_cookies(self) -> List[Dict]:
        """加载 HN cookies"""
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            return auth_data.get('cookies', [])
        except FileNotFoundError:
            logger.error(f"❌ 找不到认证文件: {self.auth_file}")
            logger.info("   请先运行 python3 hackernews_login_and_save_auth.py")
            return []

    def setup_browser(self, headless=False):
        """设置浏览器"""
        logger.info("🌐 启动浏览器...")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )

        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )

        # 加载 cookies
        cookies = self.load_cookies()
        if cookies:
            self.context.add_cookies(cookies)
            logger.info("   ✅ 已加载认证cookies")

        self.page = self.context.new_page()
        logger.info("   ✅ 浏览器启动完成")

    def verify_login(self) -> bool:
        """验证是否已登录"""
        logger.info("🔐 验证登录状态...")

        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # 检查是否有登录后的用户名链接
            # HN 登录后会在右上角显示用户名
            user_link = self.page.query_selector('a[href^="user?id="]')

            if user_link:
                username = user_link.inner_text()
                logger.info(f"   ✅ 登录成功，用户名: {username}")
                return True
            else:
                logger.error("   ❌ 未登录")
                return False

        except Exception as e:
            logger.error(f"   ❌ 验证失败: {str(e)}")
            return False

    def get_frontpage_stories(self, limit=30) -> List[Dict]:
        """
        获取首页热门帖子
        返回格式：[{
            'id': 'story_id',
            'title': '...',
            'url': 'https://news.ycombinator.com/item?id=...',
            'points': 100,
            'comments': 50,
            'age': '2 hours ago'
        }]
        """
        logger.info(f"📊 获取 HN 首页前 {limit} 个帖子...")

        try:
            self.page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            stories = []

            # HN 的结构：每个帖子是一个 .athing 元素
            story_elements = self.page.query_selector_all('tr.athing')[:limit]

            logger.info(f"   找到 {len(story_elements)} 个帖子")

            for story_elem in story_elements:
                try:
                    # 获取 story ID
                    story_id = story_elem.get_attribute('id')

                    # 获取标题和链接
                    titleline = story_elem.query_selector('.titleline')
                    if not titleline:
                        continue

                    title_link = titleline.query_selector('a')
                    if not title_link:
                        continue

                    title = title_link.inner_text()

                    # 获取下一行（包含分数、评论数等）
                    subtext_row = story_elem.evaluate('el => el.nextElementSibling')
                    if not subtext_row:
                        continue

                    # 构造评论页面 URL
                    comments_url = f"{self.base_url}/item?id={story_id}"

                    # 尝试获取分数和评论数（使用 JavaScript）
                    try:
                        meta_info = self.page.evaluate(f'''() => {{
                            const row = document.getElementById('{story_id}');
                            if (!row) return null;
                            const subtext = row.nextElementSibling;
                            if (!subtext) return null;

                            const scoreElem = subtext.querySelector('.score');
                            const commentElem = Array.from(subtext.querySelectorAll('a')).find(a => a.textContent.includes('comment'));
                            const ageElem = subtext.querySelector('.age');

                            return {{
                                points: scoreElem ? parseInt(scoreElem.textContent) : 0,
                                comments: commentElem ? parseInt(commentElem.textContent) : 0,
                                age: ageElem ? ageElem.getAttribute('title') : ''
                            }};
                        }}''')
                    except:
                        meta_info = {'points': 0, 'comments': 0, 'age': ''}

                    story = {
                        'id': story_id,
                        'title': title,
                        'url': comments_url,
                        'points': meta_info.get('points', 0) if meta_info else 0,
                        'comments': meta_info.get('comments', 0) if meta_info else 0,
                        'age': meta_info.get('age', '') if meta_info else ''
                    }

                    stories.append(story)
                    logger.info(f"   📝 {len(stories)}. {title[:60]}... (👍 {story['points']}, 💬 {story['comments']})")

                except Exception as e:
                    logger.debug(f"   ⚠️  解析帖子失败: {str(e)}")
                    continue

            return stories

        except Exception as e:
            logger.error(f"   ❌ 获取帖子失败: {str(e)}")
            return []

    def post_comment(self, story_url: str, comment_text: str) -> bool:
        """
        在指定帖子下发布评论

        Args:
            story_url: 帖子 URL (e.g., https://news.ycombinator.com/item?id=12345)
            comment_text: 评论内容

        Returns:
            bool: 是否成功
        """
        logger.info(f"💬 发布评论到: {story_url}")

        try:
            # 访问帖子页面
            self.page.goto(story_url, wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # 找到评论输入框（textarea）
            comment_box = self.page.query_selector('textarea[name="text"]')

            if not comment_box:
                logger.error("   ❌ 找不到评论输入框")
                return False

            # 滚动到评论框
            comment_box.scroll_into_view_if_needed()
            time.sleep(1)

            # 点击评论框
            comment_box.click()
            time.sleep(0.5)

            # 输入评论（模拟真人打字）
            logger.info(f"   ✏️  输入评论 ({len(comment_text)} 字符)...")

            # HN 支持段落，逐段输入
            paragraphs = comment_text.split('\n\n')
            for i, para in enumerate(paragraphs):
                # 模拟打字速度
                for char in para:
                    self.page.keyboard.type(char, delay=random.randint(20, 60))

                # 段落间换行
                if i < len(paragraphs) - 1:
                    self.page.keyboard.press('Enter')
                    self.page.keyboard.press('Enter')

            time.sleep(1)

            # 点击 "add comment" 按钮
            logger.info("   🔍 查找提交按钮...")

            # HN 的提交按钮是 input[type="submit"][value="add comment"]
            submit_button = self.page.query_selector('input[type="submit"][value="add comment"]')

            if not submit_button:
                logger.error("   ❌ 找不到提交按钮")
                return False

            # 点击提交
            submit_button.click()
            logger.info("   📤 已提交评论")

            # 等待页面响应
            time.sleep(3)

            # 验证评论是否成功（HN 提交后会刷新页面并显示评论）
            # 简单检查：URL 是否还是 item 页面
            current_url = self.page.url
            if 'item?id=' in current_url:
                logger.info(f"   ✅ 评论发布成功！")
                return True
            else:
                logger.warning(f"   ⚠️  评论状态未知，当前 URL: {current_url}")
                return True  # 假设成功

        except Exception as e:
            logger.error(f"   ❌ 发布评论失败: {str(e)}")
            return False

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.close()
            except:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except:
                pass


if __name__ == "__main__":
    # 测试
    commenter = HackerNewsCommenter()

    try:
        commenter.setup_browser(headless=False)

        if not commenter.verify_login():
            print("❌ 登录验证失败，请先运行 hackernews_login_and_save_auth.py")
            exit(1)

        print("\n✅ 登录成功！")

        # 获取首页帖子
        stories = commenter.get_frontpage_stories(limit=10)
        print(f"\n📊 获取到 {len(stories)} 个帖子")

        for i, story in enumerate(stories[:5], 1):
            print(f"\n{i}. {story['title'][:70]}...")
            print(f"   👍 {story['points']} | 💬 {story['comments']} | {story['age']}")
            print(f"   🔗 {story['url']}")

        # 测试评论（默认不执行）
        test_comment = False
        if test_comment and stories:
            test_story = stories[0]
            test_text = """This is really interesting! I've been working on a similar problem.

Have you considered using streaming APIs to reduce latency? In our case, we saw a 40% improvement by switching to WebSockets instead of polling.

Would love to hear more about your architecture choices."""

            print(f"\n🧪 测试评论功能...")
            print(f"目标帖子: {test_story['title'][:60]}...")
            print(f"评论内容: {test_text[:100]}...")

            input("\n⚠️  按 Enter 继续发布测试评论（或 Ctrl+C 取消）...")

            success = commenter.post_comment(test_story['url'], test_text)
            if success:
                print("✅ 测试评论成功！")
            else:
                print("❌ 测试评论失败")

        print("\n⏸️  浏览器将保持打开60秒...")
        time.sleep(60)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断...")
    finally:
        commenter.close_browser()
        print("\n✅ 测试完成")
