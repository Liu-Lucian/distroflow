#!/usr/bin/env python3
"""
Product Hunt 发布流程测试脚本
使用虚拟测试产品验证发布流程，不会实际提交

⚠️ 重要：这是测试脚本，使用 producthunt_launch_TEST.json 数据
正式发布时使用 producthunt_launcher.py + producthunt_launch_data.json
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

class ProductHuntLaunchTester:
    def __init__(self, test_data_file: str = "producthunt_launch_TEST.json"):
        """
        初始化测试器

        Args:
            test_data_file: 测试数据配置文件
        """
        self.test_data_file = test_data_file
        self.test_data = self._load_test_data()
        self.commenter = ProductHuntCommenter()
        self.test_results = {
            'navigation': False,
            'basic_info': False,
            'description': False,
            'tags': False,
            'overall': False
        }

    def _load_test_data(self) -> dict:
        """加载测试数据"""
        try:
            with open(self.test_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ 测试数据已加载: {data['product_name']}")
            return data
        except FileNotFoundError:
            logger.error(f"❌ 测试数据文件不存在: {self.test_data_file}")
            raise
        except Exception as e:
            logger.error(f"❌ 加载测试数据失败: {str(e)}")
            raise

    def generate_product_description(self) -> str:
        """生成产品描述（与正式版相同逻辑）"""
        desc = self.test_data['product_description']
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
        """生成 First Comment（与正式版相同逻辑）"""
        fc = self.test_data['first_comment']
        special_features = "\n".join(fc['what_makes_special'])

        comment = f"""{fc['greeting']}

{fc['introduction']}

Here's what we tested:
{special_features}

{fc['engagement_question']}

{fc['closing']}"""

        return comment

    def preview_test_content(self):
        """预览测试内容"""
        logger.info("\n" + "=" * 80)
        logger.info("🧪 Product Hunt 发布流程测试 - 内容预览")
        logger.info("=" * 80)
        logger.info("⚠️  这是测试模式，不会实际提交产品\n")

        print("🏷  测试产品信息:")
        print(f"   Product Name: {self.test_data['product_name']}")
        print(f"   Tagline: {self.test_data['tagline']}")
        print(f"   Website: {self.test_data['website']}")
        print(f"   Pricing: {self.test_data['pricing_model']}")
        print(f"   Tags: {', '.join(self.test_data['topic_tags'])}")

        print("\n📖 产品描述:")
        description = self.generate_product_description()
        print(f"   字数: {len(description)} 字符")
        print("\n" + "-" * 80)
        print(description)
        print("-" * 80)

        print("\n💬 First Comment:")
        first_comment = self.generate_first_comment()
        print(f"   字数: {len(first_comment)} 字符")
        print("\n" + "-" * 80)
        print(first_comment)
        print("-" * 80)

        logger.info("\n" + "=" * 80)

    def test_navigation(self):
        """测试1: 导航到提交页面"""
        logger.info("\n🧪 测试 1/4: 导航到提交页面...")

        try:
            self.commenter.page.goto("https://www.producthunt.com/posts/new", timeout=30000)
            time.sleep(3)

            # 检查页面是否加载
            page_loaded = False
            submit_indicators = [
                'input[name="name"]',
                'input[placeholder*="Product name"]',
                'h1:has-text("Submit")',
                'form'
            ]

            for selector in submit_indicators:
                try:
                    element = self.commenter.page.wait_for_selector(selector, timeout=5000)
                    if element:
                        page_loaded = True
                        break
                except:
                    continue

            if page_loaded:
                logger.info("   ✅ 提交页面加载成功")
                self.commenter.take_screenshot("test_1_page_loaded")
                self.test_results['navigation'] = True
                return True
            else:
                logger.error("   ❌ 提交页面加载失败")
                self.commenter.take_screenshot("test_1_page_failed")
                return False

        except Exception as e:
            logger.error(f"   ❌ 导航失败: {str(e)}")
            self.commenter.take_screenshot("test_1_error")
            return False

    def test_basic_info_filling(self):
        """测试2: 填写基础信息"""
        logger.info("\n🧪 测试 2/4: 填写基础信息...")

        fields_filled = 0
        total_fields = 3

        try:
            # Product Name
            logger.info("   测试 Product Name 输入...")
            name_selectors = [
                'input[name="name"]',
                'input[placeholder*="Product name"]',
                'input[placeholder*="Name"]',
            ]
            for selector in name_selectors:
                try:
                    name_input = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if name_input:
                        name_input.fill(self.test_data['product_name'])
                        logger.info(f"      ✅ Product Name 填写成功")
                        fields_filled += 1
                        break
                except:
                    continue

            time.sleep(1)

            # Tagline
            logger.info("   测试 Tagline 输入...")
            tagline_selectors = [
                'input[name="tagline"]',
                'input[placeholder*="Tagline"]',
                'input[placeholder*="tagline"]',
            ]
            for selector in tagline_selectors:
                try:
                    tagline_input = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if tagline_input:
                        tagline_input.fill(self.test_data['tagline'])
                        logger.info(f"      ✅ Tagline 填写成功")
                        fields_filled += 1
                        break
                except:
                    continue

            time.sleep(1)

            # Website
            logger.info("   测试 Website 输入...")
            website_selectors = [
                'input[name="website"]',
                'input[type="url"]',
                'input[placeholder*="Website"]',
            ]
            for selector in website_selectors:
                try:
                    website_input = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if website_input:
                        website_input.fill(self.test_data['website'])
                        logger.info(f"      ✅ Website 填写成功")
                        fields_filled += 1
                        break
                except:
                    continue

            logger.info(f"\n   填写结果: {fields_filled}/{total_fields} 个字段成功")
            self.commenter.take_screenshot("test_2_basic_info_filled")

            if fields_filled >= 2:  # 至少填写2个字段才算成功
                logger.info("   ✅ 基础信息填写测试通过")
                self.test_results['basic_info'] = True
                return True
            else:
                logger.warning(f"   ⚠️  基础信息填写不完整 ({fields_filled}/{total_fields})")
                return False

        except Exception as e:
            logger.error(f"   ❌ 基础信息填写失败: {str(e)}")
            self.commenter.take_screenshot("test_2_error")
            return False

    def test_description_filling(self):
        """测试3: 填写产品描述"""
        logger.info("\n🧪 测试 3/4: 填写产品描述...")

        try:
            description = self.generate_product_description()

            desc_selectors = [
                'textarea[name="description"]',
                'textarea[placeholder*="Description"]',
                'div[contenteditable="true"][data-test*="description"]',
                'textarea[placeholder*="Tell us"]',
            ]

            for selector in desc_selectors:
                try:
                    desc_box = self.commenter.page.wait_for_selector(selector, timeout=3000)
                    if desc_box:
                        desc_box.fill(description)
                        logger.info(f"      ✅ 描述填写成功 ({len(description)} 字符)")
                        self.commenter.take_screenshot("test_3_description_filled")
                        self.test_results['description'] = True
                        return True
                except:
                    continue

            logger.warning("   ⚠️  未找到描述输入框（可能需要手动操作）")
            self.commenter.take_screenshot("test_3_no_desc_box")
            return False

        except Exception as e:
            logger.error(f"   ❌ 描述填写失败: {str(e)}")
            self.commenter.take_screenshot("test_3_error")
            return False

    def test_tags_adding(self):
        """测试4: 添加 Topic Tags"""
        logger.info("\n🧪 测试 4/4: 添加 Topic Tags...")

        tags_added = 0

        try:
            for tag in self.test_data['topic_tags']:
                logger.info(f"   测试添加标签: {tag}")

                tag_selectors = [
                    'input[placeholder*="Add topics"]',
                    'input[placeholder*="tags"]',
                    'input[name="topics"]',
                    'input[placeholder*="Topics"]',
                ]

                for selector in tag_selectors:
                    try:
                        tag_input = self.commenter.page.wait_for_selector(selector, timeout=2000)
                        if tag_input:
                            tag_input.type(tag)
                            time.sleep(0.5)
                            self.commenter.page.keyboard.press("Enter")
                            time.sleep(1)
                            logger.info(f"      ✅ {tag}")
                            tags_added += 1
                            break
                    except:
                        continue

            logger.info(f"\n   添加结果: {tags_added}/{len(self.test_data['topic_tags'])} 个标签成功")
            self.commenter.take_screenshot("test_4_tags_added")

            if tags_added > 0:
                logger.info("   ✅ 标签添加测试通过")
                self.test_results['tags'] = True
                return True
            else:
                logger.warning("   ⚠️  未能添加任何标签")
                return False

        except Exception as e:
            logger.error(f"   ❌ 标签添加失败: {str(e)}")
            self.commenter.take_screenshot("test_4_error")
            return False

    def generate_test_report(self):
        """生成测试报告"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 测试报告")
        logger.info("=" * 80)

        print("\n测试结果:")
        print(f"  1. 导航到提交页面:   {'✅ 通过' if self.test_results['navigation'] else '❌ 失败'}")
        print(f"  2. 填写基础信息:     {'✅ 通过' if self.test_results['basic_info'] else '❌ 失败'}")
        print(f"  3. 填写产品描述:     {'✅ 通过' if self.test_results['description'] else '❌ 失败'}")
        print(f"  4. 添加 Topic Tags:  {'✅ 通过' if self.test_results['tags'] else '❌ 失败'}")

        passed_tests = sum(self.test_results.values())
        total_tests = len(self.test_results) - 1  # 减去 overall

        print(f"\n总计: {passed_tests}/{total_tests} 测试通过")

        if passed_tests == total_tests:
            logger.info("\n✅ 所有测试通过！发布流程验证成功")
            logger.info("   可以使用 producthunt_launcher.py 进行正式发布")
            self.test_results['overall'] = True
        elif passed_tests >= total_tests - 1:
            logger.warning("\n⚠️  大部分测试通过，但有个别问题需要解决")
            logger.info("   检查上方的警告信息，修复后再次测试")
        else:
            logger.error("\n❌ 多个测试失败，发布流程可能无法正常工作")
            logger.info("   检查 Product Hunt 页面结构是否变化")
            logger.info("   查看截图文件排查问题")

        # 保存测试报告
        report = {
            'test_time': datetime.now().isoformat(),
            'test_data_file': self.test_data_file,
            'product_name': self.test_data['product_name'],
            'results': self.test_results,
            'passed_tests': passed_tests,
            'total_tests': total_tests
        }

        with open('producthunt_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logger.info("\n📄 测试报告已保存: producthunt_test_report.json")

    def run_test(self):
        """执行完整测试"""
        logger.info("\n" + "=" * 80)
        logger.info("🧪 Product Hunt 发布流程测试")
        logger.info("=" * 80)
        logger.info("⚠️  这是测试模式，使用虚拟产品数据")
        logger.info("⚠️  不会实际提交产品到 Product Hunt\n")

        # 预览内容
        self.preview_test_content()

        # 确认继续
        print("\n⚠️  即将开始测试 Product Hunt 发布流程")
        print("测试将:")
        print("  1. 导航到提交页面")
        print("  2. 填写基础信息（测试数据）")
        print("  3. 填写产品描述")
        print("  4. 添加 Topic Tags")
        print("  5. 生成测试报告")
        print("\n⚠️  测试不会实际提交产品")
        print("⚠️  浏览器将保持打开状态供你检查")

        response = input("\n是否继续测试？(y/N): ")
        if response.lower() != 'y':
            logger.info("❌ 用户取消测试")
            return False

        # 设置浏览器
        logger.info("\n🌐 启动浏览器...")
        self.commenter.setup_browser(headless=False)

        # 验证登录
        if not self.commenter.verify_login():
            logger.error("❌ Product Hunt 未登录")
            logger.info("   请先运行: python3 producthunt_login_and_save_auth.py")
            self.commenter.close_browser()
            return False

        # 执行测试
        logger.info("\n开始执行测试...\n")

        # 测试1: 导航
        self.test_navigation()
        time.sleep(2)

        # 测试2: 基础信息
        self.test_basic_info_filling()
        time.sleep(2)

        # 测试3: 描述
        self.test_description_filling()
        time.sleep(2)

        # 测试4: 标签
        self.test_tags_adding()
        time.sleep(2)

        # 生成报告
        self.generate_test_report()

        # 保持浏览器打开
        logger.info("\n" + "=" * 80)
        logger.info("🔍 测试完成！浏览器将保持打开状态")
        logger.info("=" * 80)
        logger.info("\n请检查:")
        logger.info("  1. 页面上的填写内容是否正确")
        logger.info("  2. 所有字段是否正确显示")
        logger.info("  3. 截图文件（test_*_*.png）")
        logger.info("\n⚠️  请勿点击 Submit - 这只是测试")
        logger.info("\n检查完成后按 Enter 关闭浏览器...")
        input()

        # 关闭浏览器
        self.commenter.close_browser()
        logger.info("✅ 测试流程结束")

        return self.test_results['overall']


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 发布流程测试工具                                 ║
╚════════════════════════════════════════════════════════════════╝

⚠️  重要说明:
  • 这是测试脚本，使用虚拟测试数据
  • 不会实际提交产品到 Product Hunt
  • 用于验证发布流程是否正常工作

测试内容:
  ✅ 导航到提交页面
  ✅ 填写产品名称、Tagline、Website
  ✅ 填写产品描述
  ✅ 添加 Topic Tags
  ✅ 生成测试报告

测试完成后:
  • 检查浏览器中的填写内容
  • 查看生成的截图文件
  • 阅读测试报告（producthunt_test_report.json）
  • 如果测试通过，即可使用正式脚本发布

正式发布时使用:
  python3 producthunt_launcher.py
""")

    tester = ProductHuntLaunchTester()
    success = tester.run_test()

    if success:
        print("\n" + "=" * 80)
        print("✅ 测试全部通过！")
        print("=" * 80)
        print("\n下一步:")
        print("  1. 准备真实产品素材（封面图、Gallery、视频）")
        print("  2. 检查 producthunt_launch_data.json 配置")
        print("  3. 运行正式发布: python3 producthunt_launcher.py")
    else:
        print("\n" + "=" * 80)
        print("⚠️  测试未完全通过")
        print("=" * 80)
        print("\n建议:")
        print("  1. 检查测试报告: cat producthunt_test_report.json")
        print("  2. 查看截图文件排查问题")
        print("  3. 修复问题后重新测试")
