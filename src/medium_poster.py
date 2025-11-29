#!/usr/bin/env python3
"""
Medium 发布器 - 自动发布技术博客
支持 Markdown 格式，自动处理标题、标签
"""

try:
    from .social_media_poster_base import SocialMediaPosterBase
except ImportError:
    from social_media_poster_base import SocialMediaPosterBase

import time
import logging

logger = logging.getLogger(__name__)

class MediumPoster(SocialMediaPosterBase):
    def __init__(self, auth_file: str = "medium_auth.json"):
        super().__init__("medium", auth_file)
        self.home_url = "https://medium.com/"
        self.write_url = "https://medium.com/new-story"

    def find_post_button(self) -> bool:
        """查找Medium发布按钮"""
        try:
            publish_selectors = [
                'button:has-text("Publish")',
                'button[data-action="publish"]',
                '[aria-label*="Publish"]',
                'button:has-text("发布")'
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
        """验证Medium登录状态"""
        try:
            logger.info("🔐 验证 Medium 登录状态...")
            self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # 检查是否已登录的标志
            login_indicators = [
                'img[alt*="avatar"]',
                'button:has-text("Write")',
                'a[href*="/me/"]',
                'div[data-testid="headerAvatar"]',
                '[data-testid="mastheadAvatar"]'
            ]

            for indicator in login_indicators:
                try:
                    element = self.page.wait_for_selector(indicator, timeout=3000)
                    if element and element.is_visible():
                        logger.info("   ✅ Medium 登录状态正常")
                        return True
                except:
                    continue

            logger.error("   ❌ Medium 未登录")
            return False

        except Exception as e:
            logger.error(f"   ❌ Medium 登录验证失败: {str(e)}")
            return False

    def create_post(self, content: dict) -> bool:
        """
        创建 Medium 文章

        content 格式:
        {
            'title': '文章标题',
            'content': '完整的 Markdown 内容',
            'tags': ['tag1', 'tag2', 'tag3'],  # 最多5个标签
            'subtitle': '副标题（可选）'
        }
        """
        try:
            logger.info("📝 开始发布 Medium 文章...")

            # 步骤1: 访问 Medium 首页
            logger.info(f"🌐 访问 Medium 首页...")
            self.page.goto(self.home_url, wait_until="domcontentloaded", timeout=30000)
            self._random_delay(2, 3)

            # 步骤2: 点击 Write 按钮进入写作页面
            logger.info(f"   📍 查找并点击 Write 按钮...")
            write_button_found = False
            write_button_selectors = [
                'a[href*="/new-story"]',
                'a:has-text("Write")',
                'button:has-text("Write")',
                '[aria-label*="Write"]',
                'a[data-action="new-post"]'
            ]

            for selector in write_button_selectors:
                try:
                    write_btn = self.page.wait_for_selector(selector, timeout=3000)
                    if write_btn and write_btn.is_visible():
                        logger.info(f"      ✅ 找到 Write 按钮: {selector}")
                        write_btn.click()
                        write_button_found = True
                        break
                except:
                    continue

            if not write_button_found:
                logger.error("   ❌ 未找到 Write 按钮")
                self.take_screenshot("medium_write_button_not_found")
                return False

            # 等待写作页面加载
            logger.info(f"   ⏳ 等待写作页面加载...")
            self._random_delay(3, 5)

            # 处理"Start writing in the Medium app"弹窗
            # 策略：直接忽略弹窗，Medium 编辑器在弹窗后面仍然可用
            # 当我们开始在编辑器中输入时，弹窗会自动消失
            logger.info(f"   📍 检查是否有应用提示弹窗...")
            try:
                maybe_later = self.page.query_selector('a:has-text("Maybe later")')
                if maybe_later and maybe_later.is_visible():
                    logger.info(f"      ✅ 发现应用提示弹窗，将忽略它并直接使用后面的编辑器")
            except:
                pass

            # 截图1 - 写作页面状态（可能有弹窗）
            self.take_screenshot("medium_write_page_loaded")

            # 步骤1: 填写标题
            title = content.get('title', '')
            logger.info(f"   📍 步骤1: 填写标题...")

            title_filled = False
            title_selectors = [
                'h1[data-testid="storyTitle"]',
                'h3[data-testid="storyTitle"]',
                'h1.pw-multi-line-heading',
                'h3.pw-multi-line-heading',
                '[data-slate-editor="true"]:first-of-type',
                'div[data-contents="true"]:first-of-type'
            ]

            for selector in title_selectors:
                try:
                    title_input = self.page.wait_for_selector(selector, timeout=3000)
                    if title_input:
                        # 强制点击，即使元素被弹窗遮挡
                        title_input.click(force=True)
                        self._random_delay(0.5, 1)
                        # 使用 force 参数填写内容
                        title_input.fill(title)
                        logger.info(f"      ✅ 标题已填写: {title[:50]}...")
                        title_filled = True
                        break
                except Exception as e:
                    logger.debug(f"      尝试选择器 {selector} 失败: {str(e)}")
                    continue

            if not title_filled:
                logger.error("   ❌ 无法填写标题")
                self.take_screenshot("medium_title_not_found")
                return False

            self._random_delay(1, 2)

            # 步骤2: 填写正文内容
            article_content = content.get('content', '')
            logger.info(f"   📍 步骤2: 填写正文 ({len(article_content)} 字符)...")

            # 按下 Enter 进入正文区域
            self.page.keyboard.press('Enter')
            self._random_delay(0.5, 1)

            # 分段输入正文
            paragraphs = article_content.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    # 检查是否是标题（# 开头）
                    if paragraph.strip().startswith('#'):
                        self.page.keyboard.type(paragraph.strip())
                    else:
                        # 普通段落
                        self.page.keyboard.type(paragraph.strip())

                    # 段落间换行
                    if i < len(paragraphs) - 1:
                        self.page.keyboard.press('Enter')
                        self.page.keyboard.press('Enter')

                    # 每隔3段延迟一下
                    if i % 3 == 0:
                        self._random_delay(0.2, 0.5)

            logger.info(f"      ✅ 正文已填写")
            self._random_delay(2, 3)

            # 截图2 - 内容填写完成
            self.take_screenshot("medium_content_filled")

            # 步骤3: 点击 Publish 按钮
            logger.info(f"   📍 步骤3: 准备发布...")

            publish_clicked = False
            publish_selectors = [
                'button:has-text("Publish")',
                'button[data-action="publish"]',
                '[aria-label*="Publish"]',
                'button:has-text("发布")'
            ]

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
                logger.warning("   ⚠️  未找到 Publish 按钮（可能已自动保存为草稿）")
                self.take_screenshot("medium_publish_button_not_found")
                # 这不是错误，Medium 会自动保存草稿

            self._random_delay(2, 3)

            # 步骤4: 处理发布对话框（如果有）
            try:
                # 检查是否有发布对话框
                dialog_exists = self.page.query_selector('text="Story Preview"')
                if dialog_exists:
                    logger.info("   📍 步骤4: 处理发布对话框...")

                    # 添加标签（如果有）
                    tags = content.get('tags', [])
                    if tags:
                        logger.info(f"      添加标签: {', '.join(tags[:5])}")
                        for tag in tags[:5]:  # Medium 最多5个标签
                            try:
                                tag_input = self.page.wait_for_selector('input[placeholder*="tag"]', timeout=2000)
                                if tag_input:
                                    tag_input.type(tag)
                                    self.page.keyboard.press('Enter')
                                    self._random_delay(0.3, 0.5)
                            except:
                                pass

                    # 点击最终的 Publish now 按钮
                    try:
                        final_publish = self.page.wait_for_selector('button:has-text("Publish now")', timeout=3000)
                        if final_publish:
                            final_publish.click()
                            logger.info("      ✅ 点击 Publish now")
                    except:
                        pass

                    self._random_delay(3, 5)
            except:
                pass

            # 截图3 - 发布后
            self.take_screenshot("medium_after_publish")

            logger.info(f"   ✅ Medium 文章发布完成！")
            return True

        except Exception as e:
            logger.error(f"   ❌ Medium 发布失败: {str(e)}")
            self.take_screenshot("medium_error")
            import traceback
            logger.error(traceback.format_exc())
            return False


if __name__ == "__main__":
    # 测试
    import sys
    import os

    logging.basicConfig(level=logging.INFO)

    test_content = {
        'title': 'Building HireMeAI: Day 1 - The Vision',
        'subtitle': 'Why we need AI-powered interview assistance',
        'content': '''Today marks the beginning of an exciting journey: building HireMeAI (即答侠), an AI-powered real-time interview assistant.

## The Problem

Job seekers face immense pressure during interviews. They need to answer questions instantly, showcase their experience, and maintain composure—all while being evaluated. What if there was a way to have an AI assistant that could help in real-time?

## The Solution

HireMeAI provides:
- Real-time voice recognition (95%+ accuracy)
- Intelligent speaker identification
- Instant answer suggestions based on your resume
- <1s response latency

## Technical Architecture

We're using:
- OpenAI GPT-4 for intelligent responses
- Azure Speech Services for recognition
- Picovoice Eagle for speaker identification
- ChromaDB for vector semantic matching

## What's Next

Tomorrow, I'll dive deep into the speech recognition pipeline and how we achieved 95%+ accuracy.

Stay tuned! 🚀

https://interviewasssistant.com
liu.lucian6@gmail.com''',
        'tags': ['AI', 'BuildInPublic', 'InterviewPrep', 'TechStartup', 'MachineLearning']
    }

    poster = MediumPoster()

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
            print("❌ 登录验证失败，请先运行 medium_login_and_save_auth.py")

    finally:
        try:
            input("\n按Enter关闭浏览器...")
        except EOFError:
            pass
        poster.close_browser()
