#!/usr/bin/env python3
"""
Quora问题搜索器 - Simple Pattern
核心功能：根据关键词搜索相关问题
"""

from playwright.sync_api import sync_playwright, Page
import time
import logging
import random
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QuoraScraper:
    """Quora问题搜索器 - 简单模式"""

    def __init__(self, auth_config: Optional[Dict] = None):
        """
        初始化Quora scraper

        Args:
            auth_config: 认证配置 (cookies)
        """
        self.auth_config = auth_config or {}
        self.playwright = None
        self.browser = None
        self.page = None

    def setup_browser(self, headless: bool = True):
        """设置浏览器"""
        logger.info("🌐 启动浏览器...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)

        # 创建上下文并添加cookies
        context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )

        # 添加cookies（如果有）
        if self.auth_config.get('cookies'):
            context.add_cookies(self.auth_config['cookies'])
            logger.info("   ✅ Cookies已加载")

        self.page = context.new_page()
        logger.info("   ✅ 浏览器已启动")

    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("🔒 浏览器已关闭")

    def _random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def search_questions(self, keywords: str, max_questions: int = 10) -> List[Dict]:
        """
        根据关键词搜索Quora问题 - 核心函数

        Args:
            keywords: 搜索关键词
            max_questions: 最多返回多少个问题

        Returns:
            问题列表，每个问题包含:
            - question_text: 问题标题
            - question_url: 问题链接
            - answer_count: 回答数量
            - follower_count: 关注数量
        """
        logger.info(f"🔍 搜索Quora问题: '{keywords}'")
        logger.info(f"   目标: {max_questions} 个问题")

        if not self.page:
            raise Exception("浏览器未初始化，请先调用 setup_browser()")

        questions = []

        try:
            # 访问Quora搜索页面
            search_url = f"https://www.quora.com/search?q={keywords.replace(' ', '+')}"
            logger.info(f"   访问搜索页面...")
            self.page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 4)

            # 等待内容加载
            try:
                self.page.wait_for_selector('div[class*="Question"]', timeout=10000)
            except:
                logger.warning("   ⚠️  搜索结果加载较慢，继续尝试...")

            # 滚动页面加载更多内容
            for i in range(3):
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                self._random_delay(1, 2)

            # 提取问题 - 尝试多个选择器
            question_selectors = [
                'a[class*="question_link"]',
                'a[href*="/question/"]',
                'div[class*="Question"] a',
                'span[class*="QuestionText"] a',
            ]

            question_elements = []
            for selector in question_selectors:
                elements = self.page.query_selector_all(selector)
                if elements:
                    logger.info(f"   ✅ 使用选择器找到 {len(elements)} 个元素: {selector}")
                    question_elements = elements
                    break

            if not question_elements:
                logger.error("   ❌ 未找到问题元素")
                return []

            # 提取问题信息
            seen_urls = set()
            for elem in question_elements:
                if len(questions) >= max_questions:
                    break

                try:
                    # 获取问题文本和链接
                    question_text = elem.inner_text().strip()
                    question_href = elem.get_attribute('href')

                    if not question_text or not question_href:
                        continue

                    # 构造完整URL
                    if question_href.startswith('/'):
                        question_url = f"https://www.quora.com{question_href}"
                    else:
                        question_url = question_href

                    # 去重
                    if question_url in seen_urls:
                        continue
                    seen_urls.add(question_url)

                    # 过滤非问题链接
                    if '/question/' not in question_url:
                        continue

                    question_data = {
                        'question_text': question_text,
                        'question_url': question_url,
                        'answer_count': 0,  # 需要访问详情页才能获取
                        'follower_count': 0,
                        'keywords': keywords,
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }

                    questions.append(question_data)
                    logger.info(f"   📄 找到问题 {len(questions)}: {question_text[:60]}...")

                except Exception as e:
                    logger.debug(f"      跳过一个元素: {str(e)[:50]}")
                    continue

            logger.info(f"✅ 搜索完成，找到 {len(questions)} 个问题")
            return questions

        except Exception as e:
            logger.error(f"❌ 搜索失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def get_question_details(self, question_url: str) -> Dict:
        """
        获取问题详情（可选功能）

        Args:
            question_url: 问题URL

        Returns:
            问题详细信息
        """
        logger.info(f"📖 获取问题详情: {question_url}")

        try:
            self.page.goto(question_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # 获取问题标题
            question_text = ""
            try:
                title_elem = self.page.query_selector('h1, span[class*="QuestionText"]')
                if title_elem:
                    question_text = title_elem.inner_text().strip()
            except:
                pass

            # 获取回答数量
            answer_count = 0
            try:
                answer_elems = self.page.query_selector_all('div[class*="Answer"]')
                answer_count = len(answer_elems)
            except:
                pass

            return {
                'question_url': question_url,
                'question_text': question_text,
                'answer_count': answer_count,
                'retrieved_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"❌ 获取详情失败: {str(e)}")
            return {}


if __name__ == "__main__":
    """测试脚本"""
    import json

    # 测试搜索
    scraper = QuoraScraper()

    try:
        scraper.setup_browser(headless=False)

        # 测试搜索问题
        questions = scraper.search_questions("AI interview assistant", max_questions=5)

        print(f"\n找到 {len(questions)} 个问题:")
        print(json.dumps(questions, indent=2, ensure_ascii=False))

        # 保存结果
        with open('quora_test_questions.json', 'w', encoding='utf-8') as f:
            json.dump(questions, f, indent=2, ensure_ascii=False)
        print("\n✅ 结果已保存到 quora_test_questions.json")

    finally:
        input("\n按Enter关闭浏览器...")
        scraper.close_browser()
