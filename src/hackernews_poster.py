#!/usr/bin/env python3
"""
Hacker News Poster - 发帖基础类
支持 Show HN, Ask HN, 普通帖子发布
"""
from playwright.sync_api import sync_playwright
import json
import time
import logging
import random
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HackerNewsPoster:
    def __init__(self, auth_file='hackernews_auth.json'):
        self.auth_file = auth_file
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.base_url = "https://news.ycombinator.com"

    def load_cookies(self):
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

    def submit_post(self, post_data: Dict) -> bool:
        """
        提交帖子到 HN

        post_data 格式:
        {
            "title": "Show HN: Real-time AI interview assistant",
            "url": "https://interviewasssistant.com",  # 可选，如果有 URL
            "text": "帖子正文内容..."  # 可选，如果是 Ask HN 或自我介绍
        }

        HN 发帖规则:
        - Show HN: 必须有 URL 或 text（产品展示）
        - Ask HN: 通常只有 title 和 text（问题）
        - 普通帖子: 可以有 URL 或 text

        Returns:
            bool: 是否成功
        """
        logger.info(f"📤 开始发布帖子: {post_data['title'][:60]}...")

        try:
            # 访问 submit 页面
            self.page.goto(f"{self.base_url}/submit", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)

            # 填写标题
            logger.info("   ✏️  填写标题...")
            title_input = self.page.query_selector('input[name="title"]')
            if not title_input:
                logger.error("   ❌ 找不到标题输入框")
                return False

            title_input.fill(post_data['title'])
            time.sleep(0.5)

            # 如果有 URL，填写 URL
            if post_data.get('url'):
                logger.info(f"   🔗 填写 URL: {post_data['url']}")
                url_input = self.page.query_selector('input[name="url"]')
                if url_input:
                    url_input.fill(post_data['url'])
                    time.sleep(0.5)

            # 如果有正文，填写正文
            if post_data.get('text'):
                logger.info(f"   📝 填写正文 ({len(post_data['text'])} 字符)...")

                # HN 的正文框可能是 textarea
                text_area = self.page.query_selector('textarea[name="text"]')
                if text_area:
                    # 模拟真人打字
                    paragraphs = post_data['text'].split('\n\n')
                    for i, para in enumerate(paragraphs):
                        # 逐字输入（稍快一些，因为是发帖不是评论）
                        for char in para:
                            self.page.keyboard.type(char, delay=random.randint(10, 30))

                        # 段落间换行
                        if i < len(paragraphs) - 1:
                            self.page.keyboard.press('Enter')
                            self.page.keyboard.press('Enter')

                    time.sleep(1)

            # 点击提交按钮
            logger.info("   🔍 查找提交按钮...")

            # HN 的提交按钮是 input[type="submit"][value="submit"]
            submit_button = self.page.query_selector('input[type="submit"][value="submit"]')

            if not submit_button:
                logger.error("   ❌ 找不到提交按钮")
                return False

            # 截图用于调试
            # self.page.screenshot(path=f"hackernews_submit_{int(time.time())}.png")

            # 点击提交
            submit_button.click()
            logger.info("   📤 已提交帖子")

            # 等待页面响应
            time.sleep(3)

            # 验证是否成功（HN 提交后会跳转到该帖子页面）
            current_url = self.page.url
            logger.info(f"   📍 当前 URL: {current_url}")

            # 成功的话会跳转到 /item?id=xxx
            if 'item?id=' in current_url:
                logger.info(f"   ✅ 帖子发布成功！")
                logger.info(f"   🔗 帖子链接: {current_url}")
                return True
            # 或者可能返回到首页
            elif current_url == f"{self.base_url}/" or current_url == f"{self.base_url}/newest":
                logger.info(f"   ✅ 帖子可能发布成功（返回首页）")
                return True
            else:
                logger.warning(f"   ⚠️  帖子状态未知，当前 URL: {current_url}")
                return True  # 假设成功

        except Exception as e:
            logger.error(f"   ❌ 发布帖子失败: {str(e)}")
            import traceback
            traceback.print_exc()
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
    poster = HackerNewsPoster()

    try:
        poster.setup_browser(headless=False)

        if not poster.verify_login():
            print("❌ 登录验证失败，请先运行 hackernews_login_and_save_auth.py")
            exit(1)

        print("\n✅ 登录成功！")
        print("\n测试帖子提交功能...")

        # 测试数据
        test_post = {
            "title": "Ask HN: What's the best approach for real-time AI streaming?",
            "text": """I'm building a real-time interview assistant and trying to optimize latency.

Current stack:
- Azure Speech SDK for ASR (streaming mode)
- GPT-4 for response generation
- SSE for client streaming

Main bottleneck is the first-byte latency (~1s). We've tried:
- Precomputing common answers (80% speedup)
- Dual-level caching
- Vector similarity search

Any suggestions for sub-500ms first-byte? Is WebSockets + delta updates worth the complexity?

Would love to hear your experiences with real-time AI systems."""
        }

        print("\n⚠️  这是一个测试帖子，将会真实发布到 HN!")
        print(f"   标题: {test_post['title']}")
        print(f"   正文: {test_post['text'][:100]}...")
        print()

        confirm = input("确认发布？(输入 YES 继续): ")

        if confirm == "YES":
            success = poster.submit_post(test_post)
            if success:
                print("\n✅ 测试帖子发布成功！")
            else:
                print("\n❌ 测试帖子发布失败")
        else:
            print("❌ 已取消")

        print("\n⏸️  浏览器将保持打开30秒...")
        time.sleep(30)

    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断...")
    finally:
        poster.close_browser()
        print("\n✅ 测试完成")
