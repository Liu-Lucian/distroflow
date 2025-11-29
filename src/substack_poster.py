#!/usr/bin/env python3
"""
Substack 发布器 - 自动发布Newsletter风格文章
支持标题、副标题、正文内容
"""

try:
    from .social_media_poster_base import SocialMediaPosterBase
except ImportError:
    from social_media_poster_base import SocialMediaPosterBase

import time
import logging

logger = logging.getLogger(__name__)

class SubstackPoster(SocialMediaPosterBase):
    def __init__(self, auth_file: str = "substack_auth.json", substack_url: str = None):
        """
        初始化Substack发布器

        Args:
            auth_file: 认证文件路径
            substack_url: 你的Substack域名，如 "yourname.substack.com"
        """
        super().__init__("substack", auth_file)
        self.substack_url = substack_url
        self.home_url = f"https://{substack_url}" if substack_url else "https://substack.com"
        self.write_url = f"https://{substack_url}/publish/post/new" if substack_url else None

    def find_post_button(self) -> bool:
        """查找Substack发布按钮"""
        try:
            publish_selectors = [
                'button:has-text("Publish")',
                'button:has-text("Publish now")',
                'button[data-testid="publish-button"]',
                '[aria-label*="Publish"]',
            ]

            for selector in publish_selectors:
                try:
                    button = self.page.wait_for_selector(selector, timeout=2000)
                    if button and button.is_visible():
                        return True
                except:
                    continue
            return False
        except Exception as e:
            logger.error(f"查找发布按钮失败: {str(e)}")
            return False

    def verify_login(self) -> bool:
        """验证Substack登录状态"""
        try:
            logger.info("🔐 验证 Substack 登录状态...")
            self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # 检查是否已登录
            login_indicators = [
                'button:has-text("New post")',
                'a[href*="/publish"]',
                'button:has-text("Write")',
                'a:has-text("Dashboard")',
                '[data-testid="user-menu"]',
                'img[alt*="avatar"]'
            ]

            for indicator in login_indicators:
                try:
                    element = self.page.wait_for_selector(indicator, timeout=3000)
                    if element and element.is_visible():
                        logger.info("   ✅ Substack 登录状态正常")
                        return True
                except:
                    continue

            logger.error("   ❌ Substack 未登录")
            return False

        except Exception as e:
            logger.error(f"   ❌ Substack 登录验证失败: {str(e)}")
            return False

    def create_post(self, content: dict) -> bool:
        """
        创建 Substack 文章

        content 格式:
        {
            'title': '文章标题',
            'subtitle': '副标题',
            'content': '完整的文章内容（支持Markdown）',
            'publish_immediately': True/False  # 是否立即发布（否则保存为草稿）
        }
        """
        try:
            logger.info("📝 开始发布 Substack 文章...")

            # 步骤1: 访问新建文章页面
            if self.write_url:
                logger.info(f"🌐 访问 Substack 写作页面...")
                self.page.goto(self.write_url, wait_until="domcontentloaded", timeout=30000)
            else:
                # 如果没有指定URL，从首页找New post按钮
                logger.info(f"🌐 访问 Substack 首页...")
                self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30000)
                self._random_delay(2, 3)

                # 查找并点击New post按钮
                new_post_selectors = [
                    'button:has-text("New post")',
                    'a:has-text("New post")',
                    'button:has-text("Write")',
                    'a[href*="/publish/post/new"]'
                ]

                new_post_found = False
                for selector in new_post_selectors:
                    try:
                        btn = self.page.wait_for_selector(selector, timeout=3000)
                        if btn and btn.is_visible():
                            logger.info(f"   ✅ 找到 New post 按钮: {selector}")
                            btn.click()
                            new_post_found = True
                            break
                    except:
                        continue

                if not new_post_found:
                    logger.error("   ❌ 未找到 New post 按钮")
                    self.take_screenshot("substack_new_post_not_found")
                    return False

            # 等待编辑器加载
            logger.info(f"   ⏳ 等待编辑器加载...")
            self._random_delay(3, 5)

            # 截图1 - 编辑器页面
            self.take_screenshot("substack_editor_loaded")

            # 步骤2: 填写标题
            title = content.get('title', '')
            logger.info(f"   📍 步骤1: 填写标题...")

            title_filled = False
            title_selectors = [
                'textarea[placeholder*="Post title"]',
                'input[placeholder*="Post title"]',
                'textarea[name="title"]',
                'div[data-testid="post-title"]',
                'textarea[aria-label*="title"]'
            ]

            for selector in title_selectors:
                try:
                    title_input = self.page.wait_for_selector(selector, timeout=3000)
                    if title_input and title_input.is_visible():
                        title_input.click()
                        self._random_delay(0.5, 1)
                        title_input.fill(title)
                        logger.info(f"      ✅ 标题已填写: {title[:50]}...")
                        title_filled = True
                        break
                except Exception as e:
                    logger.debug(f"      尝试选择器 {selector} 失败: {str(e)}")
                    continue

            if not title_filled:
                logger.error("   ❌ 无法填写标题")
                self.take_screenshot("substack_title_not_found")
                return False

            self._random_delay(1, 2)

            # 步骤3: 填写副标题（如果有）
            subtitle = content.get('subtitle', '')
            if subtitle:
                logger.info(f"   📍 步骤2: 填写副标题...")

                subtitle_selectors = [
                    'textarea[placeholder*="Subtitle"]',
                    'input[placeholder*="Subtitle"]',
                    'textarea[name="subtitle"]',
                    'div[data-testid="post-subtitle"]'
                ]

                for selector in subtitle_selectors:
                    try:
                        subtitle_input = self.page.wait_for_selector(selector, timeout=3000)
                        if subtitle_input and subtitle_input.is_visible():
                            subtitle_input.click()
                            self._random_delay(0.5, 1)
                            subtitle_input.fill(subtitle)
                            logger.info(f"      ✅ 副标题已填写: {subtitle[:50]}...")
                            break
                    except:
                        continue

                self._random_delay(1, 2)

            # 步骤4: 填写正文内容
            article_content = content.get('content', '')
            logger.info(f"   📍 步骤3: 填写正文 ({len(article_content)} 字符)...")

            # Substack使用富文本编辑器
            editor_selectors = [
                'div[contenteditable="true"]',
                'div[data-testid="post-body"]',
                'div.ProseMirror',
                'div[role="textbox"]',
                'textarea[placeholder*="Body"]'
            ]

            editor_found = False
            for selector in editor_selectors:
                try:
                    editor = self.page.wait_for_selector(selector, timeout=3000)
                    if editor and editor.is_visible():
                        logger.info(f"      ✅ 找到编辑器: {selector}")
                        editor.click()
                        self._random_delay(1, 2)

                        # 分段输入正文
                        paragraphs = article_content.split('\n\n')
                        for i, paragraph in enumerate(paragraphs):
                            if paragraph.strip():
                                # 检查是否是标题（# 开头）
                                if paragraph.strip().startswith('#'):
                                    # Substack支持Markdown，直接输入
                                    self.page.keyboard.type(paragraph.strip())
                                else:
                                    # 普通段落
                                    self.page.keyboard.type(paragraph.strip())

                                # 段落间换行
                                if i < len(paragraphs) - 1:
                                    self.page.keyboard.press('Enter')
                                    self.page.keyboard.press('Enter')

                                # 每隔3段延迟一下，模拟人类打字
                                if i % 3 == 0:
                                    self._random_delay(0.3, 0.8)

                        editor_found = True
                        break
                except Exception as e:
                    logger.debug(f"      尝试编辑器 {selector} 失败: {str(e)}")
                    continue

            if not editor_found:
                logger.error("   ❌ 无法找到编辑器")
                self.take_screenshot("substack_editor_not_found")
                return False

            logger.info(f"      ✅ 正文已填写")
            self._random_delay(2, 3)

            # 截图2 - 内容填写完成
            self.take_screenshot("substack_content_filled")

            # 步骤5: 发布或保存为草稿
            publish_immediately = content.get('publish_immediately', False)

            if publish_immediately:
                logger.info(f"   📍 步骤4: 准备发布...")

                # 查找Publish按钮
                publish_selectors = [
                    'button:has-text("Publish")',
                    'button:has-text("Publish now")',
                    'button[data-testid="publish-button"]',
                    '[aria-label*="Publish"]'
                ]

                publish_clicked = False
                for selector in publish_selectors:
                    try:
                        publish_button = self.page.wait_for_selector(selector, timeout=3000)
                        if publish_button and publish_button.is_visible():
                            publish_button.click()
                            logger.info(f"      ✅ 点击 Publish 按钮")
                            publish_clicked = True
                            break
                    except:
                        continue

                if not publish_clicked:
                    logger.warning("   ⚠️  未找到 Publish 按钮，内容可能已保存为草稿")
                    self.take_screenshot("substack_publish_button_not_found")

                self._random_delay(2, 3)

                # 处理发布确认对话框（如果有）
                try:
                    confirm_publish = self.page.wait_for_selector('button:has-text("Publish now")', timeout=3000)
                    if confirm_publish and confirm_publish.is_visible():
                        confirm_publish.click()
                        logger.info("      ✅ 确认发布")
                        self._random_delay(3, 5)
                except:
                    pass

                logger.info(f"   ✅ Substack 文章已发布！")
            else:
                logger.info(f"   💾 Substack 文章已保存为草稿")

            # 截图3 - 发布后
            self.take_screenshot("substack_after_publish")

            return True

        except Exception as e:
            logger.error(f"   ❌ Substack 发布失败: {str(e)}")
            self.take_screenshot("substack_error")
            import traceback
            logger.error(traceback.format_exc())
            return False


if __name__ == "__main__":
    # 测试
    import sys
    import os

    logging.basicConfig(level=logging.INFO)

    # 使用示例
    test_content = {
        'title': 'Week 1: Building HireMeAI - The Journey Begins',
        'subtitle': 'Behind the scenes of an AI interview assistant',
        'content': '''Today marks week 1 of building HireMeAI in public. Let me share what I learned.

## The Problem

Most job candidates panic during interviews. They know the answers but freeze under pressure. What if an AI could whisper the perfect answer in real-time?

## Technical Breakthrough

This week we achieved **92% speaker identification accuracy** using Picovoice Eagle. The system now knows when the interviewer is speaking vs when you are.

Why does this matter? Because the AI should only respond to interviewer questions - not your own voice. This was the hardest technical challenge.

## Key Metrics

- Voice recognition latency: **<1 second**
- Answer generation: **1.2 seconds average**
- Semantic matching accuracy: **88%**

## What's Next

Week 2 focus: Improving the STAR framework answer generation. Currently testing with 50 real interview scenarios.

Building in public keeps me accountable. More updates next week 🚀

---

Try the beta at https://interviewasssistant.com

Questions? Email liu.lucian6@gmail.com''',
        'publish_immediately': False  # 保存为草稿，测试时不立即发布
    }

    # 替换为你的Substack域名
    SUBSTACK_DOMAIN = "yourname.substack.com"

    poster = SubstackPoster(substack_url=SUBSTACK_DOMAIN)

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
            print("❌ 登录验证失败，请先运行 substack_login_and_save_auth.py")

    finally:
        try:
            input("\n按Enter关闭浏览器...")
        except EOFError:
            pass
        poster.close_browser()
