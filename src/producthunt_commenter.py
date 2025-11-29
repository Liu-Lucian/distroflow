#!/usr/bin/env python3
"""
Product Hunt 评论发布器
在其他产品的 Launch 下发布真诚、有价值的评论
遵循 Build in Public 风格，自然提及 HireMeAI
"""

from social_media_poster_base import SocialMediaPosterBase
from playwright.sync_api import sync_playwright
import time
import logging
import random
import json

logger = logging.getLogger(__name__)

class ProductHuntCommenter(SocialMediaPosterBase):
    def __init__(self, auth_file: str = "platforms_auth.json"):
        super().__init__("producthunt", auth_file)
        self.home_url = "https://www.producthunt.com"

    def setup_browser(self, headless: bool = False):
        """设置浏览器（Product Hunt 增强版 - 恢复完整浏览器状态）"""
        logger.info(f"🌐 设置 Product Hunt 浏览器（增强版）...")

        # 加载认证数据
        auth_data = self._load_auth()
        if not auth_data:
            logger.error("❌ 未找到认证数据")
            return None

        # 获取 Product Hunt 认证信息
        ph_auth = auth_data.get('producthunt', {})
        if not ph_auth:
            logger.error("❌ 未找到 Product Hunt 认证信息")
            return None

        cookies = ph_auth.get('cookies', [])
        local_storage = ph_auth.get('localStorage', {})
        session_storage = ph_auth.get('sessionStorage', {})
        user_agent = ph_auth.get('user_agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        logger.info(f"   📦 加载认证数据:")
        logger.info(f"      • Cookies: {len(cookies)} 个")
        logger.info(f"      • localStorage: {len(local_storage)} 个键")
        logger.info(f"      • sessionStorage: {len(session_storage)} 个键")

        # 启动浏览器
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )

        # 创建上下文
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=user_agent
        )

        # 加载 cookies
        if cookies:
            context.add_cookies(cookies)
            logger.info("   ✅ Cookies 已加载")

        # 创建页面
        self.page = context.new_page()

        # 导航到 Product Hunt（必须先导航才能设置 localStorage）
        logger.info("   🌐 导航到 Product Hunt...")
        self.page.goto(self.home_url, timeout=30000)
        time.sleep(2)

        # 恢复 localStorage
        if local_storage:
            logger.info("   📦 恢复 localStorage...")
            for key, value in local_storage.items():
                try:
                    # 确保值被正确转义
                    self.page.evaluate(f"localStorage.setItem({json.dumps(key)}, {json.dumps(value)})")
                except Exception as e:
                    logger.warning(f"      ⚠️  无法设置 localStorage 键 '{key}': {str(e)}")
            logger.info(f"   ✅ localStorage 已恢复 ({len(local_storage)} 个键)")

        # 恢复 sessionStorage
        if session_storage:
            logger.info("   📦 恢复 sessionStorage...")
            for key, value in session_storage.items():
                try:
                    self.page.evaluate(f"sessionStorage.setItem({json.dumps(key)}, {json.dumps(value)})")
                except Exception as e:
                    logger.warning(f"      ⚠️  无法设置 sessionStorage 键 '{key}': {str(e)}")
            logger.info(f"   ✅ sessionStorage 已恢复 ({len(session_storage)} 个键)")

        # 刷新页面让存储生效
        logger.info("   🔄 刷新页面激活登录状态...")
        self.page.reload()
        time.sleep(3)

        logger.info("   ✅ 浏览器设置完成！")
        return self.page

    def find_post_button(self) -> bool:
        """
        Product Hunt 评论系统不需要 post button
        直接在产品页面评论
        """
        return True

    def verify_login(self) -> bool:
        """验证 Product Hunt 登录状态（增强版 - 优先 localStorage）"""
        try:
            logger.info("🔍 验证 Product Hunt 登录状态...")
            self.page.goto(self.home_url, timeout=30000)
            time.sleep(3)

            # 方法1（最可靠）: 检查 localStorage
            logger.info("   方法 1: 检查 localStorage（最可靠）...")
            try:
                local_storage = self.page.evaluate("() => Object.keys(localStorage)")
                user_keys = [k for k in local_storage if 'user' in k.lower() or 'auth' in k.lower() or 'session' in k.lower()]

                if user_keys:
                    logger.info(f"   ✅ 在 localStorage 找到用户数据: {', '.join(user_keys[:3])}")
                    logger.info("   ✅ Product Hunt 登录成功（通过 localStorage 验证）")
                    return True
                else:
                    logger.info("   ℹ️  localStorage 中未找到用户数据，继续其他检测...")
            except Exception as e:
                logger.warning(f"   ⚠️  无法检查 localStorage: {str(e)}")

            # 方法2: 检查登录指示器（登录后才有的元素）
            logger.info("   方法 2: 检查页面登录指示器...")
            login_indicators = [
                'a[href*="/posts/new"]',  # Submit 按钮
                'button[data-test="user-menu"]',  # 用户菜单
                'div[data-test="header-user-menu"]',  # 用户头像
                'a[href*="/settings"]',  # Settings 链接
                'button:has-text("Submit")',  # Submit 按钮（文本）
                '[data-test*="user"]',  # 任何包含 user 的 data-test
                'img[alt*="avatar"]',  # 用户头像图片
                'nav a[href*="/notifications"]',  # 通知链接
            ]

            found_login = False
            for selector in login_indicators:
                try:
                    element = self.page.wait_for_selector(selector, timeout=2000)
                    if element and element.is_visible():
                        logger.info(f"   ✅ 找到登录指示器: {selector}")
                        found_login = True
                        break
                except:
                    continue

            if found_login:
                logger.info("   ✅ Product Hunt 登录成功（通过页面元素验证）")
                return True

            # 方法3: 检查关键未登录指示器
            # 注意：不检查 "Sign up" 因为已登录用户页面底部也可能有
            logger.info("   方法 3: 检查关键未登录指示器...")
            critical_not_logged_in_indicators = [
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                'a[href="/login"]',  # 明确的登录链接
            ]

            found_not_logged_in = False
            for selector in critical_not_logged_in_indicators:
                try:
                    element = self.page.wait_for_selector(selector, timeout=2000)
                    if element and element.is_visible():
                        logger.warning(f"   ⚠️  找到未登录指示器: {selector}")
                        found_not_logged_in = True
                        break
                except:
                    continue

            if found_not_logged_in:
                logger.error("   ❌ Product Hunt 未登录（通过页面元素判断）")
                logger.info("   建议: 运行 python3 producthunt_login_and_save_auth.py")
                return False

            # 方法4: 如果所有方法都没有明确结果，采取宽松策略
            logger.warning("   ⚠️  无法明确判断登录状态")
            logger.info("   ℹ️  采取宽松策略：允许继续，后续操作如失败再处理")

            # 截图供用户检查
            self.take_screenshot("login_verification_uncertain")

            # 返回 True，让用户可以继续操作
            return True

        except Exception as e:
            logger.error(f"   ❌ 登录验证失败: {str(e)}")
            return False

    def navigate_to_product(self, product_url: str) -> bool:
        """
        导航到产品页面

        Args:
            product_url: Product Hunt 产品页面 URL

        Returns:
            是否成功导航
        """
        try:
            logger.info(f"🌐 访问产品页面: {product_url}")
            self.page.goto(product_url, timeout=30000)
            self._random_delay(3, 5)

            # 等待评论区加载
            comment_section_selectors = [
                'div[data-test="comment-list"]',
                'section[class*="comment"]',
                'div[class*="discussion"]',
                'textarea[placeholder*="comment"]',
                'textarea[placeholder*="Comment"]',
            ]

            for selector in comment_section_selectors:
                try:
                    element = self.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        logger.info("   ✅ 产品页面加载成功")
                        return True
                except:
                    continue

            logger.warning("   ⚠️  未找到评论区，但继续尝试...")
            return True

        except Exception as e:
            logger.error(f"   ❌ 导航失败: {str(e)}")
            return False

    def post_comment(self, comment_text: str) -> bool:
        """
        发布评论

        Args:
            comment_text: 评论内容

        Returns:
            是否发布成功
        """
        try:
            logger.info(f"💬 准备发布评论 ({len(comment_text)} 字符)...")

            # 查找评论输入框（使用正确的选择器）
            comment_box_selectors = [
                'div[contenteditable="true"][role="textbox"]',  # 最可靠 - 自动检测发现
                'textarea[placeholder*="comment"]',
                'textarea[placeholder*="Comment"]',
                'textarea[name="comment"]',
                'div[contenteditable="true"]',
                'textarea[class*="comment"]',
            ]

            comment_box = None
            found_selector = None
            for selector in comment_box_selectors:
                try:
                    comment_box = self.page.wait_for_selector(selector, timeout=5000)
                    if comment_box and comment_box.is_visible():
                        logger.info(f"   ✅ 找到评论框: {selector}")
                        found_selector = selector
                        break
                except:
                    continue

            if not comment_box:
                logger.error("   ❌ 未找到评论输入框")
                self.take_screenshot("comment_box_not_found")
                return False

            # 点击评论框激活
            comment_box.click()
            self._random_delay(1, 2)

            # 输入评论内容
            logger.info("   ⌨️  输入评论内容...")

            # 检查是否是 contenteditable div
            if 'contenteditable' in found_selector:
                # 使用 innerHTML 输入（contenteditable div）
                logger.info("   使用 contenteditable 输入方法...")
                comment_box.evaluate(f"el => el.innerHTML = {json.dumps(comment_text)}")
                # 触发 input 事件
                comment_box.evaluate("el => el.dispatchEvent(new Event('input', { bubbles: true }))")
            else:
                # 使用 type() 输入（textarea）
                logger.info("   使用 textarea 输入方法...")
                comment_box.type(comment_text, delay=random.randint(50, 150))

            self._random_delay(2, 3)

            self.take_screenshot("before_submit_comment")

            # 查找提交按钮
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Post")',
                'button:has-text("Comment")',
                'button:has-text("Submit")',
                'button[class*="submit"]',
                'button[class*="post"]',
            ]

            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.page.wait_for_selector(selector, timeout=3000)
                    if submit_button and submit_button.is_visible() and submit_button.is_enabled():
                        logger.info(f"   ✅ 找到提交按钮: {selector}")
                        break
                except:
                    continue

            if not submit_button:
                logger.error("   ❌ 未找到提交按钮")
                self.take_screenshot("submit_button_not_found")
                return False

            # 点击提交
            logger.info("   📤 提交评论...")
            submit_button.click()
            self._random_delay(3, 5)

            # 验证评论是否发布成功（检查是否出现在页面上）
            try:
                # 查找包含评论文本的元素
                self.page.wait_for_selector(f'text="{comment_text[:50]}"', timeout=10000)
                logger.info("   ✅ 评论发布成功！")
                self.take_screenshot("comment_posted")
                return True
            except:
                logger.warning("   ⚠️  未能确认评论是否发布，可能需要人工检查")
                self.take_screenshot("comment_status_unknown")
                return True  # 返回 True，让调度器继续

        except Exception as e:
            logger.error(f"   ❌ 评论发布失败: {str(e)}")
            self.take_screenshot("comment_error")
            return False

    def upvote_product(self) -> bool:
        """
        为产品点赞 (Upvote)

        Returns:
            是否点赞成功
        """
        try:
            logger.info("👍 尝试为产品点赞...")

            # 使用正确的选择器（从自动检测中发现）
            upvote_selectors = [
                'button[data-test*="vote"]',  # 最可靠 - 自动检测发现
                'button[data-test*="upvote"]',
                'button[class*="upvote"]',
                'button:has-text("Upvote")',
            ]

            for selector in upvote_selectors:
                try:
                    upvote_button = self.page.wait_for_selector(selector, timeout=5000)
                    if upvote_button and upvote_button.is_visible():
                        upvote_button.click()
                        logger.info("   ✅ 点赞成功")
                        self._random_delay(1, 2)
                        return True
                except:
                    continue

            logger.warning("   ⚠️  未找到点赞按钮")
            return False

        except Exception as e:
            logger.error(f"   ❌ 点赞失败: {str(e)}")
            return False

    def comment_on_product(self, product_url: str, comment_text: str, upvote: bool = True) -> bool:
        """
        在产品页面发布评论（主函数）

        Args:
            product_url: Product Hunt 产品 URL
            comment_text: 评论内容
            upvote: 是否先点赞

        Returns:
            是否成功
        """
        try:
            # 导航到产品页面
            if not self.navigate_to_product(product_url):
                return False

            # 点赞（可选）
            if upvote:
                self.upvote_product()
                self._random_delay(2, 3)

            # 发布评论
            success = self.post_comment(comment_text)

            if success:
                logger.info("✅ 完整流程执行成功")

            return success

        except Exception as e:
            logger.error(f"❌ 评论流程失败: {str(e)}")
            return False

    def create_post(self, content: dict) -> bool:
        """
        实现抽象方法（用于评论场景）

        content 格式:
        {
            'product_url': 'https://www.producthunt.com/posts/product-name',
            'comment': 'Your comment text here',
            'upvote': True  # optional
        }
        """
        product_url = content.get('product_url')
        comment = content.get('comment')
        upvote = content.get('upvote', True)

        if not product_url or not comment:
            logger.error("❌ 缺少必要参数: product_url 和 comment")
            return False

        return self.comment_on_product(product_url, comment, upvote)


# 测试代码
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    commenter = ProductHuntCommenter()
    commenter.setup_browser(headless=False)

    if commenter.verify_login():
        # 测试评论
        test_content = {
            'product_url': 'https://www.producthunt.com/posts/test-product',  # 替换为真实产品
            'comment': 'Great product! As someone building an AI interview assistant, I really appreciate tools that solve real problems.',
            'upvote': True
        }

        success = commenter.create_post(test_content)
        print(f"\n{'✅' if success else '❌'} 测试{'成功' if success else '失败'}")

    commenter.close_browser()
