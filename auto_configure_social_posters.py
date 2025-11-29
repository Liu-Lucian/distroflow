#!/usr/bin/env python3
"""
自动配置社交媒体发布器 - AI视觉辅助
- 截图分析UI
- 自动找到发布按钮
- 生成平台特定的发布脚本
- 持续监控和自动修复
"""

import os
import sys
import json
import time
import base64
from pathlib import Path
from playwright.sync_api import sync_playwright
from openai import OpenAI

class AutoPosterConfigurator:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        self.platforms = {
            'twitter': {
                'url': 'https://twitter.com/home',
                'auth_file': 'auth.json',
                'post_action': 'Tweet',
                'auth_key_path': 'cookies'
            },
            'reddit': {
                'url': 'https://www.reddit.com/submit',
                'auth_file': 'reddit_auth.json',
                'post_action': 'Create Post',
                'auth_key_path': 'cookies'
            },
            'instagram': {
                'url': 'https://www.instagram.com',
                'auth_file': 'platforms_auth.json',
                'post_action': 'Create',
                'auth_key_path': 'instagram.cookies'
            },
            'tiktok': {
                'url': 'https://www.tiktok.com/upload',
                'auth_file': 'platforms_auth.json',
                'post_action': 'Upload',
                'auth_key_path': 'tiktok.sessionid'
            },
            'linkedin': {
                'url': 'https://www.linkedin.com/feed',
                'auth_file': 'linkedin_auth.json',
                'post_action': 'Start a post',
                'auth_key_path': 'cookies'
            }
        }
        self.config_output = "social_poster_configs.json"
        self.configs = self.load_configs()

    def load_configs(self):
        """加载已有配置"""
        if os.path.exists(self.config_output):
            with open(self.config_output, 'r') as f:
                return json.load(f)
        return {}

    def save_configs(self):
        """保存配置"""
        with open(self.config_output, 'w') as f:
            json.dump(self.configs, f, indent=2)

    def log(self, message, level="INFO"):
        """日志"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {"INFO": "ℹ️ ", "SUCCESS": "✅", "WARNING": "⚠️ ", "ERROR": "❌"}.get(level, "")
        print(f"[{timestamp}] {prefix} {message}")
        sys.stdout.flush()

    def analyze_screenshot_with_ai(self, screenshot_path: str, platform: str) -> dict:
        """使用GPT-4o Vision分析截图，找到发布按钮"""
        self.log(f"🤖 使用AI分析截图: {screenshot_path}")

        # 读取截图
        with open(screenshot_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()

        post_action = self.platforms[platform]['post_action']

        prompt = f"""You are analyzing a {platform.upper()} website screenshot to find the POST/CREATE button.

The button should allow users to create new content. Common names:
- Twitter: "Post", "Tweet", "What's happening"
- Reddit: "Create Post", "Submit"
- Instagram: "New post", "Create", "+"
- TikTok: "Upload", "Post a video"
- LinkedIn: "Start a post", "Share"

Target action: "{post_action}"

TASK: Identify the POST/CREATE button location and characteristics.

Provide a JSON response with:
{{
  "button_found": true/false,
  "button_location": "description of where button is (e.g., 'top-left sidebar', 'bottom-right FAB')",
  "button_text": "exact text on button",
  "button_type": "primary-button / link / icon / FAB",
  "selectors": [
    "CSS selector option 1",
    "CSS selector option 2",
    "data-testid or aria-label selector"
  ],
  "confidence": 0-100,
  "notes": "any additional observations"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_data}"}
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )

            result_text = response.choices[0].message.content

            # 提取JSON
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group(0))
                self.log(f"   ✅ AI分析完成 (置信度: {analysis.get('confidence', 0)}%)", "SUCCESS")
                return analysis
            else:
                self.log(f"   ⚠️  无法解析AI响应", "WARNING")
                return {"button_found": False, "error": "Failed to parse AI response"}

        except Exception as e:
            self.log(f"   ❌ AI分析失败: {str(e)}", "ERROR")
            return {"button_found": False, "error": str(e)}

    def configure_platform(self, platform: str) -> bool:
        """配置单个平台"""
        self.log("="*60)
        self.log(f"🔧 配置平台: {platform.upper()}")
        self.log("="*60)

        config = self.platforms[platform]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )

            # 加载cookies
            auth_file = config['auth_file']
            if os.path.exists(auth_file):
                try:
                    with open(auth_file, 'r') as f:
                        auth_data = json.load(f)

                    # 处理不同的auth格式
                    auth_key_path = config['auth_key_path'].split('.')
                    cookies_data = auth_data
                    for key in auth_key_path:
                        if key in cookies_data:
                            cookies_data = cookies_data[key]
                        else:
                            break

                    if isinstance(cookies_data, list):
                        context.add_cookies(cookies_data)
                        self.log(f"   ✅ 已加载cookies from {auth_file}")
                    elif isinstance(cookies_data, str):
                        # sessionid格式
                        self.log(f"   ℹ️  使用sessionid模式")
                except Exception as e:
                    self.log(f"   ⚠️  加载cookies失败: {e}", "WARNING")

            page = context.new_page()

            # 访问页面
            self.log(f"   🌐 访问: {config['url']}")
            page.goto(config['url'])
            time.sleep(5)

            # 截图1 - 初始状态
            screenshot1 = f"{platform}_config_initial.png"
            page.screenshot(path=screenshot1, full_page=True)
            self.log(f"   📸 截图: {screenshot1}")

            # AI分析截图
            analysis = self.analyze_screenshot_with_ai(screenshot1, platform)

            if analysis.get('button_found'):
                self.log(f"   🎯 找到发布按钮: {analysis.get('button_text')}", "SUCCESS")
                self.log(f"   📍 位置: {analysis.get('button_location')}")

                # 测试selectors
                working_selector = None
                for selector in analysis.get('selectors', []):
                    try:
                        self.log(f"   🧪 测试selector: {selector}")
                        elements = page.query_selector_all(selector)
                        if elements:
                            self.log(f"      ✅ 找到 {len(elements)} 个元素", "SUCCESS")
                            # 验证是否可见
                            visible_count = sum(1 for e in elements if e.is_visible())
                            if visible_count > 0:
                                working_selector = selector
                                self.log(f"      ✅ {visible_count} 个可见元素", "SUCCESS")
                                break
                    except Exception as e:
                        self.log(f"      ❌ 失败: {e}", "ERROR")

                if working_selector:
                    # 保存配置
                    self.configs[platform] = {
                        'url': config['url'],
                        'post_button_selector': working_selector,
                        'button_text': analysis.get('button_text'),
                        'button_location': analysis.get('button_location'),
                        'confidence': analysis.get('confidence'),
                        'configured_at': time.time(),
                        'all_selectors': analysis.get('selectors', [])
                    }
                    self.save_configs()
                    self.log(f"   ✅ 配置已保存", "SUCCESS")

                    browser.close()
                    return True
                else:
                    self.log(f"   ⚠️  所有selector测试失败", "WARNING")

            else:
                self.log(f"   ⚠️  AI未找到发布按钮", "WARNING")
                self.log(f"   💡 建议: 请手动检查截图 {screenshot1}")

            # 等待用户检查
            self.log(f"   ⏸️  浏览器将保持打开10秒...")
            time.sleep(10)

            browser.close()
            return False

    def configure_all_platforms(self):
        """配置所有平台"""
        self.log("🚀 开始自动配置所有平台发布器")
        self.log("="*60)

        results = {}
        for platform in ['twitter', 'reddit', 'instagram', 'linkedin']:
            try:
                success = self.configure_platform(platform)
                results[platform] = 'success' if success else 'failed'
                time.sleep(3)
            except Exception as e:
                self.log(f"❌ {platform} 配置错误: {str(e)}", "ERROR")
                results[platform] = f'error: {str(e)}'

        # 总结
        self.log("\n" + "="*60)
        self.log("📊 配置总结:")
        self.log("="*60)
        for platform, status in results.items():
            icon = "✅" if status == 'success' else "❌"
            self.log(f"   {icon} {platform.upper()}: {status}")

        self.log(f"\n💾 配置已保存到: {self.config_output}")

        return results

if __name__ == "__main__":
    configurator = AutoPosterConfigurator()
    configurator.configure_all_platforms()
