#!/usr/bin/env python3
"""
Product Hunt 产品发布器
自动发布产品到 Product Hunt，遵循标准 Launch 格式
"""

import sys
sys.path.insert(0, 'src')
from producthunt_commenter import ProductHuntCommenter
import json
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductHuntLauncher:
    def __init__(self, launch_data_file: str = "producthunt_launch_data.json"):
        """
        初始化 Product Hunt Launcher

        Args:
            launch_data_file: Launch 数据配置文件
        """
        self.launch_data_file = launch_data_file
        self.launch_data = self._load_launch_data()
        self.commenter = ProductHuntCommenter()

    def _load_launch_data(self) -> dict:
        """加载 Launch 数据"""
        try:
            with open(self.launch_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Launch 数据已加载: {data['product_name']}")
            return data
        except FileNotFoundError:
            logger.error(f"❌ Launch 数据文件不存在: {self.launch_data_file}")
            raise
        except Exception as e:
            logger.error(f"❌ 加载 Launch 数据失败: {str(e)}")
            raise

    def generate_product_description(self) -> str:
        """
        生成完整的产品描述

        格式：
        [Hook paragraph]

        [What it is paragraph]

        💡 How it works:
        - Feature 1
        - Feature 2
        ...

        🎯 Why we built it:
        [Reason paragraph]

        🚀 [Call to action]
        """
        desc = self.launch_data['product_description']

        # 构建 How it works 列表
        how_it_works_items = "\n".join(desc['how_it_works'])

        description = f"""{desc['hook']}

{desc['what_it_is']}

💡 How it works:
{how_it_works_items}

🎯 Why we built it:
{desc['why_we_built']}

{desc['call_to_action']}"""

        return description

    def generate_first_comment(self) -> str:
        """
        生成 First Comment（置顶留言）

        格式：
        Hey Product Hunters 👋

        [Introduction]

        What makes it special:
        - Point 1
        - Point 2
        ...

        [Engagement question]

        [Closing]
        """
        fc = self.launch_data['first_comment']

        # 构建特色功能列表
        special_features = "\n".join(fc['what_makes_special'])

        comment = f"""{fc['greeting']}

{fc['introduction']}

We're launching our first beta today. Here's what makes it special:
{special_features}

{fc['engagement_question']}

{fc['closing']}"""

        return comment

    def preview_launch_content(self):
        """预览 Launch 内容"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 Product Hunt Launch 内容预览")
        logger.info("=" * 80)

        print("\n🏷  基础信息:")
        print(f"   Product Name: {self.launch_data['product_name']}")
        print(f"   Tagline: {self.launch_data['tagline']}")
        print(f"   Website: {self.launch_data['website']}")
        print(f"   Pricing: {self.launch_data['pricing_model']}")
        print(f"   Tags: {', '.join(self.launch_data['topic_tags'])}")
        print(f"   Makers: {', '.join(self.launch_data['makers'])}")

        print("\n📖 产品描述:")
        description = self.generate_product_description()
        print(f"   字数: {len(description)} 字符")
        print("\n" + "-" * 80)
        print(description)
        print("-" * 80)

        print("\n💬 First Comment (置顶留言):")
        first_comment = self.generate_first_comment()
        print(f"   字数: {len(first_comment)} 字符")
        print("\n" + "-" * 80)
        print(first_comment)
        print("-" * 80)

        print("\n✨ Key Features:")
        for i, feature in enumerate(self.launch_data['key_features'], 1):
            print(f"   {i}. {feature}")

        print(f"\n🧠 Tech Stack: {self.launch_data['tech_stack']}")

        print("\n🖼  Gallery Images:")
        for img in self.launch_data['gallery_images']:
            print(f"   - {img}")

        print(f"\n🎥 Demo Video: {self.launch_data.get('demo_video', 'N/A')}")

        logger.info("\n" + "=" * 80)

    def navigate_to_submit_page(self):
        """导航到产品提交页面"""
        logger.info("🌐 访问 Product Hunt 提交页面...")

        try:
            self.commenter.page.goto("https://www.producthunt.com/posts/new", timeout=30000)
            time.sleep(3)

            logger.info("   ✅ 提交页面加载成功")
            self.commenter.take_screenshot("submit_page_loaded")
            return True

        except Exception as e:
            logger.error(f"   ❌ 导航失败: {str(e)}")
            return False

    def fill_basic_info(self):
        """填写基础信息"""
        logger.info("📝 填写基础信息...")

        try:
            # Product Name
            logger.info("   输入 Product Name...")
            name_selectors = [
                'input[name="name"]',
                'input[placeholder*="Product name"]',
                'input[placeholder*="Name"]',
            ]
            for selector in name_selectors:
                try:
                    name_input = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if name_input:
                        name_input.fill(self.launch_data['product_name'])
                        logger.info(f"      ✅ Product Name: {self.launch_data['product_name']}")
                        break
                except:
                    continue

            time.sleep(1)

            # Tagline
            logger.info("   输入 Tagline...")
            tagline_selectors = [
                'input[name="tagline"]',
                'input[placeholder*="Tagline"]',
                'input[placeholder*="tagline"]',
            ]
            for selector in tagline_selectors:
                try:
                    tagline_input = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if tagline_input:
                        tagline_input.fill(self.launch_data['tagline'])
                        logger.info(f"      ✅ Tagline: {self.launch_data['tagline']}")
                        break
                except:
                    continue

            time.sleep(1)

            # Website
            logger.info("   输入 Website...")
            website_selectors = [
                'input[name="website"]',
                'input[type="url"]',
                'input[placeholder*="Website"]',
            ]
            for selector in website_selectors:
                try:
                    website_input = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if website_input:
                        website_input.fill(self.launch_data['website'])
                        logger.info(f"      ✅ Website: {self.launch_data['website']}")
                        break
                except:
                    continue

            logger.info("   ✅ 基础信息填写完成")
            self.commenter.take_screenshot("basic_info_filled")
            return True

        except Exception as e:
            logger.error(f"   ❌ 填写基础信息失败: {str(e)}")
            self.commenter.take_screenshot("basic_info_error")
            return False

    def fill_description(self):
        """填写产品描述"""
        logger.info("📖 填写产品描述...")

        try:
            description = self.generate_product_description()

            desc_selectors = [
                'textarea[name="description"]',
                'textarea[placeholder*="Description"]',
                'div[contenteditable="true"][data-test*="description"]',
            ]

            for selector in desc_selectors:
                try:
                    desc_box = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if desc_box:
                        desc_box.fill(description)
                        logger.info(f"      ✅ 描述已填写 ({len(description)} 字符)")
                        break
                except:
                    continue

            self.commenter.take_screenshot("description_filled")
            return True

        except Exception as e:
            logger.error(f"   ❌ 填写描述失败: {str(e)}")
            return False

    def add_topic_tags(self):
        """添加 Topic Tags"""
        logger.info("🏷  添加 Topic Tags...")

        try:
            for tag in self.launch_data['topic_tags']:
                logger.info(f"   添加标签: {tag}")

                # 查找标签输入框
                tag_selectors = [
                    'input[placeholder*="Add topics"]',
                    'input[placeholder*="tags"]',
                    'input[name="topics"]',
                ]

                for selector in tag_selectors:
                    try:
                        tag_input = self.commenter.page.wait_for_selector(selector, timeout=2000)
                        if tag_input:
                            tag_input.type(tag)
                            time.sleep(0.5)
                            # 按 Enter 或等待下拉菜单
                            self.commenter.page.keyboard.press("Enter")
                            time.sleep(1)
                            logger.info(f"      ✅ {tag}")
                            break
                    except:
                        continue

            logger.info("   ✅ 标签添加完成")
            return True

        except Exception as e:
            logger.error(f"   ❌ 添加标签失败: {str(e)}")
            return False

    def launch_product(self, headless: bool = False):
        """
        执行完整的 Launch 流程

        Args:
            headless: 是否无头模式

        Returns:
            是否发布成功
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"🚀 开始发布 {self.launch_data['product_name']} 到 Product Hunt")
        logger.info("=" * 80)

        # 预览内容
        self.preview_launch_content()

        # 确认发布
        print("\n⚠️  即将发布产品到 Product Hunt")
        print("请确认以上内容无误")
        response = input("\n是否继续？(y/N): ")
        if response.lower() != 'y':
            logger.info("❌ 用户取消发布")
            return False

        # 设置浏览器
        logger.info("\n🌐 启动浏览器...")
        self.commenter.setup_browser(headless=headless)

        # 验证登录
        if not self.commenter.verify_login():
            logger.error("❌ Product Hunt 未登录，请先运行 producthunt_login_and_save_auth.py")
            self.commenter.close_browser()
            return False

        # 导航到提交页面
        if not self.navigate_to_submit_page():
            self.commenter.close_browser()
            return False

        time.sleep(2)

        # 填写基础信息
        if not self.fill_basic_info():
            logger.warning("⚠️  基础信息填写可能不完整，请检查截图")

        time.sleep(2)

        # 填写描述
        if not self.fill_description():
            logger.warning("⚠️  描述填写可能失败，请检查截图")

        time.sleep(2)

        # 添加标签
        if not self.add_topic_tags():
            logger.warning("⚠️  标签添加可能不完整，请检查截图")

        time.sleep(2)

        # ⚠️ 注意：
        # Product Hunt 发布需要上传图片/视频，这部分需要手动操作
        # 因为 Playwright 处理文件上传比较复杂

        logger.info("\n" + "=" * 80)
        logger.info("⚠️  自动填写已完成！")
        logger.info("=" * 80)
        logger.info("\n接下来需要手动完成：")
        logger.info("  1. 上传封面图（512x512 PNG）")
        logger.info("  2. 上传 Gallery 图片（3-5张）")
        logger.info("  3. 上传 Demo 视频（可选）")
        logger.info("  4. 设置 Pricing 模式")
        logger.info("  5. 添加 Makers")
        logger.info("  6. 检查所有信息")
        logger.info("  7. 点击 'Submit' 或 'Schedule'")
        logger.info("\n发布后，记得立即发 First Comment（置顶留言）：\n")

        first_comment = self.generate_first_comment()
        print("-" * 80)
        print(first_comment)
        print("-" * 80)

        logger.info("\n浏览器将保持打开状态，手动完成剩余步骤...")
        logger.info("完成后按 Enter 关闭浏览器...")
        input()

        # 关闭浏览器
        self.commenter.close_browser()
        logger.info("✅ 发布流程结束")

        return True

    def generate_launch_checklist(self):
        """生成 Launch Checklist"""
        logger.info("\n" + "=" * 80)
        logger.info("📋 Product Hunt Launch Checklist")
        logger.info("=" * 80)

        checklist = f"""
🎯 发布前准备（T-3天）
□ 准备封面图（512x512 PNG，简洁 Logo + Tagline）
□ 准备 Gallery 截图（3-5张，展示核心功能）
□ 录制 Demo 视频（30-60秒，展示产品流程）
□ 在 Twitter/LinkedIn 预热："We're launching on Product Hunt soon!"
□ 邀请朋友准备好在发布日点赞评论

📝 发布当天（Launch Day）
□ 选择最佳时间：太平洋时间上午 12:00-1:00 AM
□ 填写基础信息：
   - Product name: {self.launch_data['product_name']}
   - Tagline: {self.launch_data['tagline']}
   - Website: {self.launch_data['website']}
□ 上传封面图
□ 上传 Gallery 图片
□ 上传 Demo 视频
□ 填写产品描述（{len(self.generate_product_description())} 字符）
□ 添加 Topic tags: {', '.join(self.launch_data['topic_tags'])}
□ 设置 Pricing: {self.launch_data['pricing_model']}
□ 添加 Makers: {', '.join(self.launch_data['makers'])}
□ 检查所有信息无误
□ 点击 Submit/Schedule

🚀 发布后（24小时内）
□ 立即发 First Comment（置顶留言）
□ 同步分享到 Twitter/LinkedIn/Reddit
□ 回复所有评论（15分钟内响应）
□ 感谢所有点赞和评论的人
□ 更新进展："We just hit #X on PH!"
□ 监控排名，争取进入 Top 5

💬 First Comment 内容：
{self.generate_first_comment()}

📊 成功指标
□ 进入当天 Top 10
□ 获得 100+ upvotes
□ 获得 20+ 有价值的评论
□ 带来 500+ 网站访问
□ 获得 Product of the Day（最佳目标）

🛠️ 工具推荐
□ Typefully - 同步分享到 Twitter
□ Canva - 制作封面图
□ Loom - 录制 Demo 视频
□ Buffer - 定时发布社交媒体
"""

        print(checklist)

        # 保存到文件
        with open("producthunt_launch_checklist.txt", 'w', encoding='utf-8') as f:
            f.write(checklist)

        logger.info("✅ Checklist 已保存到: producthunt_launch_checklist.txt")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 产品发布器 - HireMeAI Launch                    ║
╚════════════════════════════════════════════════════════════════╝

功能：
  1. 生成 Launch Checklist
  2. 预览 Launch 内容
  3. 自动填写基础信息（半自动发布）

⚠️  注意：
  - Product Hunt 发布需要手动上传图片/视频
  - 建议首次发布时仔细检查每一步
  - 最佳发布时间：太平洋时间上午 12:00-1:00 AM
""")

    print("\n请选择操作：")
    print("  1. 生成 Launch Checklist")
    print("  2. 预览 Launch 内容")
    print("  3. 开始发布流程（半自动）")
    print("  4. 退出")

    choice = input("\n请输入选项 (1-4): ")

    launcher = ProductHuntLauncher()

    if choice == "1":
        launcher.generate_launch_checklist()

    elif choice == "2":
        launcher.preview_launch_content()

    elif choice == "3":
        launcher.launch_product(headless=False)

    else:
        print("退出")
