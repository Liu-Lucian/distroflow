#!/usr/bin/env python3
"""
调试工具：查找各平台的发布按钮
帮助定位post/tweet/upload按钮的selectors
"""

from playwright.sync_api import sync_playwright
import json
import time
import sys

class PostButtonFinder:
    def __init__(self, platform: str):
        self.platform = platform
        self.urls = {
            'twitter': 'https://twitter.com/home',
            'reddit': 'https://www.reddit.com',
            'instagram': 'https://www.instagram.com',
            'tiktok': 'https://www.tiktok.com/upload',
            'linkedin': 'https://www.linkedin.com/feed',
            'github': 'https://github.com/new'
        }
        self.auth_files = {
            'twitter': 'auth.json',
            'reddit': 'reddit_auth.json',
            'instagram': 'platforms_auth.json',
            'tiktok': 'platforms_auth.json',
            'linkedin': 'linkedin_auth.json',
            'github': 'github_auth.json'  # 假设存在
        }

    def find_buttons(self):
        """查找所有可能的发布按钮"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            # 加载cookies
            auth_file = self.auth_files.get(self.platform)
            if auth_file:
                try:
                    with open(auth_file, 'r') as f:
                        auth_data = json.load(f)

                    if self.platform in ['instagram', 'tiktok']:
                        # platforms_auth.json格式
                        if self.platform in auth_data and 'cookies' in auth_data[self.platform]:
                            context.add_cookies(auth_data[self.platform]['cookies'])
                    elif 'cookies' in auth_data:
                        context.add_cookies(auth_data['cookies'])

                    print(f"✅ Cookies已加载: {auth_file}")
                except Exception as e:
                    print(f"⚠️  无法加载cookies: {e}")

            page = context.new_page()

            # 访问页面
            url = self.urls.get(self.platform, 'https://google.com')
            print(f"\n🌐 访问: {url}")
            page.goto(url)
            time.sleep(5)  # 等待页面加载

            # 截图1 - 初始状态
            screenshot1 = f"{self.platform}_buttons_initial.png"
            page.screenshot(path=screenshot1)
            print(f"📸 初始截图: {screenshot1}")

            # 查找常见的发布按钮关键词
            button_keywords = [
                'post', 'tweet', 'share', 'publish', 'upload', 'create',
                'new', 'submit', 'compose', '发布', '发送', '创建', '上传',
                'write', 'add'
            ]

            print(f"\n🔍 查找发布按钮...")
            print("=" * 60)

            found_buttons = []

            # 方法1: 查找所有按钮
            all_buttons = page.query_selector_all('button, a[role="button"], [role="button"]')
            print(f"\n📊 找到 {len(all_buttons)} 个按钮元素")

            for idx, btn in enumerate(all_buttons[:50]):  # 只检查前50个
                try:
                    text = btn.inner_text().strip().lower()
                    aria_label = btn.get_attribute('aria-label') or ''
                    btn_class = btn.get_attribute('class') or ''
                    data_testid = btn.get_attribute('data-testid') or ''

                    # 检查是否包含发布相关关键词
                    if any(kw in text for kw in button_keywords) or \
                       any(kw in aria_label.lower() for kw in button_keywords) or \
                       any(kw in data_testid.lower() for kw in button_keywords):

                        visible = btn.is_visible()
                        enabled = not btn.is_disabled()

                        info = {
                            'index': idx,
                            'text': text[:50],
                            'aria_label': aria_label[:50],
                            'class': btn_class[:100],
                            'data_testid': data_testid,
                            'visible': visible,
                            'enabled': enabled
                        }

                        found_buttons.append(info)

                        status = "✅" if (visible and enabled) else "⚠️ "
                        print(f"\n{status} 按钮 #{idx}:")
                        print(f"   文本: {text[:50]}")
                        print(f"   Aria-label: {aria_label[:50]}")
                        print(f"   Data-testid: {data_testid}")
                        print(f"   可见: {visible} | 可用: {enabled}")
                except:
                    pass

            # 方法2: 特定平台的选择器
            print(f"\n\n🎯 {self.platform.upper()} 特定选择器:")
            print("=" * 60)

            platform_selectors = {
                'twitter': [
                    'a[data-testid="SideNav_NewTweet_Button"]',
                    'a[aria-label*="Post"]',
                    'button[data-testid="tweetButtonInline"]',
                    '[data-testid="toolBar"]'
                ],
                'reddit': [
                    'button:has-text("Create Post")',
                    'a[href*="/submit"]',
                    'button[data-click-id="create_post"]',
                    '.create-post-button'
                ],
                'instagram': [
                    'a[href="#"]>svg[aria-label*="New post"]',
                    'button:has-text("New post")',
                    'a[href="/create/story"]',
                    '[aria-label*="Create"]'
                ],
                'tiktok': [
                    'button:has-text("Upload")',
                    'a[href="/upload"]',
                    '.upload-btn',
                    '[data-e2e="upload-btn"]'
                ],
                'linkedin': [
                    'button:has-text("Start a post")',
                    '.share-box-feed-entry',
                    'button[data-control-name="share_box.open"]',
                    '[aria-label*="Start a post"]'
                ],
                'github': [
                    'a:has-text("New repository")',
                    'button:has-text("New")',
                    'a[href="/new"]',
                    '[data-ga-click*="new"]'
                ]
            }

            selectors = platform_selectors.get(self.platform, [])
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    if elements:
                        print(f"\n✅ 找到: {selector}")
                        for idx, elem in enumerate(elements):
                            text = elem.inner_text()[:50] if elem.is_visible() else "[不可见]"
                            print(f"   元素 {idx}: {text}")
                    else:
                        print(f"❌ 未找到: {selector}")
                except Exception as e:
                    print(f"❌ 错误 {selector}: {str(e)[:50]}")

            # 截图2 - 标注后
            screenshot2 = f"{self.platform}_buttons_annotated.png"
            page.screenshot(path=screenshot2, full_page=True)
            print(f"\n📸 完整截图: {screenshot2}")

            # 保存结果
            result = {
                'platform': self.platform,
                'url': url,
                'found_buttons': found_buttons,
                'platform_selectors_tested': selectors
            }

            result_file = f"{self.platform}_button_analysis.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"💾 结果已保存: {result_file}")

            print(f"\n\n{'='*60}")
            print(f"📊 总结:")
            print(f"   找到可能的发布按钮: {len(found_buttons)} 个")
            print(f"   截图已保存: {screenshot1}, {screenshot2}")
            print(f"   分析已保存: {result_file}")
            print(f"{'='*60}\n")

            # 等待用户查看
            print("⏸️  浏览器将保持打开10秒，请手动检查...")
            time.sleep(10)

            browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 debug_post_buttons.py <platform>")
        print("平台: twitter, reddit, instagram, tiktok, linkedin, github")
        sys.exit(1)

    platform = sys.argv[1].lower()
    if platform not in ['twitter', 'reddit', 'instagram', 'tiktok', 'linkedin', 'github']:
        print(f"❌ 不支持的平台: {platform}")
        sys.exit(1)

    finder = PostButtonFinder(platform)
    finder.find_buttons()
