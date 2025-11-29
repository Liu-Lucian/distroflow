#!/usr/bin/env python3
"""
Cookies 格式转换工具
Convert cookies from EditThisCookie format to Playwright format

支持多种格式：
- EditThisCookie 导出格式
- 浏览器控制台导出格式
- 简单的 JSON 数组格式
"""

import json
import sys
import os
from datetime import datetime

def convert_editthiscookie_to_playwright(cookies):
    """
    转换 EditThisCookie 格式到 Playwright 格式
    Convert EditThisCookie format to Playwright format
    """
    playwright_cookies = []

    for cookie in cookies:
        # EditThisCookie 格式
        playwright_cookie = {
            'name': cookie.get('name', ''),
            'value': cookie.get('value', ''),
            'domain': cookie.get('domain', '.twitter.com'),
            'path': cookie.get('path', '/'),
            'expires': cookie.get('expirationDate', -1),
            'httpOnly': cookie.get('httpOnly', False),
            'secure': cookie.get('secure', True),
            'sameSite': cookie.get('sameSite', 'None')
        }
        playwright_cookies.append(playwright_cookie)

    return playwright_cookies

def create_playwright_auth_state(cookies):
    """
    创建完整的 Playwright auth state
    Create complete Playwright auth state
    """
    # Playwright 需要的完整格式
    auth_state = {
        'cookies': cookies,
        'origins': [
            {
                'origin': 'https://twitter.com',
                'localStorage': []
            }
        ]
    }

    return auth_state

def validate_cookies(cookies):
    """验证 cookies 是否包含必要的字段"""
    if not cookies:
        return False, "Cookies 列表为空"

    # 检查是否有 auth_token（Twitter 最重要的 cookie）
    has_auth_token = any(c.get('name') == 'auth_token' for c in cookies)

    if not has_auth_token:
        return False, "缺少 auth_token cookie（Twitter 登录必需）"

    return True, f"找到 {len(cookies)} 个 cookies"

def main():
    print("=" * 60)
    print("🍪 Cookies 格式转换工具")
    print("   Cookie Format Converter")
    print("=" * 60)
    print()

    # 获取输入文件
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        print("用法 / Usage:")
        print("  python convert_cookies.py <cookies_file.json>")
        print()
        print("示例 / Example:")
        print("  python convert_cookies.py twitter_cookies.json")
        print()

        input_file = input("请输入 cookies 文件路径: ").strip()

    # 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误：文件不存在: {input_file}")
        sys.exit(1)

    print(f"📂 读取文件: {input_file}")

    try:
        # 读取 cookies 文件
        with open(input_file, 'r', encoding='utf-8') as f:
            cookies_data = json.load(f)

        # 如果是数组，直接使用
        if isinstance(cookies_data, list):
            cookies = cookies_data
        # 如果已经是 Playwright 格式
        elif isinstance(cookies_data, dict) and 'cookies' in cookies_data:
            print("✓ 检测到已是 Playwright 格式")
            cookies = cookies_data['cookies']
        else:
            print("❌ 错误：无法识别的 cookies 格式")
            sys.exit(1)

        print(f"✓ 成功读取 {len(cookies)} 个 cookies")

        # 验证 cookies
        valid, message = validate_cookies(cookies)
        if not valid:
            print(f"⚠️  警告: {message}")
            print()
            confirm = input("是否继续？(y/n): ").strip().lower()
            if confirm != 'y':
                sys.exit(0)
        else:
            print(f"✓ {message}")

        # 显示重要的 cookies
        print()
        print("重要的 cookies:")
        important_cookies = ['auth_token', 'ct0', 'twid', 'kdt']
        for name in important_cookies:
            cookie = next((c for c in cookies if c.get('name') == name), None)
            if cookie:
                value = cookie.get('value', '')
                display_value = value[:20] + '...' if len(value) > 20 else value
                print(f"  ✓ {name}: {display_value}")
            else:
                print(f"  ✗ {name}: 未找到")

        # 转换为 Playwright 格式
        print()
        print("🔄 转换为 Playwright 格式...")
        playwright_cookies = convert_editthiscookie_to_playwright(cookies)
        auth_state = create_playwright_auth_state(playwright_cookies)

        # 保存到 auth.json
        output_file = "auth.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(auth_state, f, indent=2, ensure_ascii=False)

        print(f"✓ 已保存到: {output_file}")

        # 显示文件信息
        file_size = os.path.getsize(output_file)
        print()
        print("=" * 60)
        print("✅ 转换完成！")
        print("=" * 60)
        print(f"📄 文件: {output_file}")
        print(f"📊 大小: {file_size} bytes")
        print(f"🍪 Cookies: {len(playwright_cookies)} 个")
        print()
        print("🎉 现在可以开始爬取了：")
        print("   python quick_scrape_playwright.py elonmusk 50")
        print("=" * 60)

    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        print()
        print("请确保文件是有效的 JSON 格式")
        print("如果从 EditThisCookie 导出，直接粘贴即可")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
