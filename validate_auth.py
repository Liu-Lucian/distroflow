#!/usr/bin/env python3
"""
验证 auth.json 文件
Validate auth.json file

检查格式是否正确，cookies 是否有效
Check if format is correct and cookies are valid
"""

import json
import os
from datetime import datetime

def validate_auth_file(filename="auth.json"):
    """验证 auth.json 文件"""

    print("=" * 60)
    print("🔍 验证 Auth 文件")
    print("   Validate Auth File")
    print("=" * 60)
    print()

    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        print()
        print("请先创建 auth.json 文件：")
        print("  方法1: python create_auth_manual.py")
        print("  方法2: python convert_cookies.py twitter_cookies.json")
        print("  方法3: python setup_login.py")
        return False

    print(f"✓ 找到文件: {filename}")

    # 读取文件
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            auth_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 格式错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return False

    print("✓ JSON 格式正确")

    # 检查结构
    if not isinstance(auth_data, dict):
        print("❌ 格式错误：应该是一个对象")
        return False

    if 'cookies' not in auth_data:
        print("❌ 缺少 'cookies' 字段")
        return False

    cookies = auth_data['cookies']

    if not isinstance(cookies, list):
        print("❌ 'cookies' 应该是一个数组")
        return False

    print(f"✓ 包含 {len(cookies)} 个 cookies")

    # 检查关键的 cookies
    print()
    print("检查关键 cookies:")

    required_cookies = {
        'auth_token': '登录令牌（必需）',
        'ct0': 'CSRF 令牌（必需）'
    }

    optional_cookies = {
        'twid': '用户ID',
        'kdt': '追踪ID',
        'guest_id': '访客ID'
    }

    all_cookies = {**required_cookies, **optional_cookies}

    found_cookies = {}
    missing_required = []

    for cookie in cookies:
        if not isinstance(cookie, dict):
            continue

        name = cookie.get('name', '')
        value = cookie.get('value', '')

        if name in all_cookies:
            found_cookies[name] = value

    # 检查必需的 cookies
    for name, description in required_cookies.items():
        if name in found_cookies:
            value = found_cookies[name]
            display_value = value[:20] + '...' if len(value) > 20 else value
            print(f"  ✓ {name}: {display_value}")
            print(f"    {description}")
        else:
            print(f"  ✗ {name}: 未找到")
            print(f"    {description}")
            missing_required.append(name)

    # 检查可选的 cookies
    print()
    print("可选 cookies:")
    for name, description in optional_cookies.items():
        if name in found_cookies:
            value = found_cookies[name]
            display_value = value[:20] + '...' if len(value) > 20 else value
            print(f"  ✓ {name}: {display_value}")
        else:
            print(f"  - {name}: 未找到 (可选)")

    # 检查 cookie 字段
    print()
    print("检查 cookie 格式:")

    sample_cookie = cookies[0] if cookies else {}
    required_fields = ['name', 'value', 'domain', 'path']

    for field in required_fields:
        if field in sample_cookie:
            print(f"  ✓ {field}")
        else:
            print(f"  ⚠️  {field}: 缺少（可能影响使用）")

    # 文件信息
    file_size = os.path.getsize(filename)
    file_time = datetime.fromtimestamp(os.path.getmtime(filename))

    print()
    print("=" * 60)
    print("文件信息:")
    print(f"  📄 文件名: {filename}")
    print(f"  📊 大小: {file_size} bytes")
    print(f"  🕐 修改时间: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  🍪 Cookies 数量: {len(cookies)}")

    # 总结
    print()
    print("=" * 60)

    if missing_required:
        print("❌ 验证失败")
        print(f"   缺少必需的 cookies: {', '.join(missing_required)}")
        print()
        print("请重新创建 auth.json:")
        print("  python create_auth_manual.py")
        return False
    else:
        print("✅ 验证通过！")
        print()
        print("auth.json 格式正确，包含所有必需的 cookies")
        print()
        print("🎉 现在可以开始爬取了：")
        print("   python quick_scrape_playwright.py elonmusk 50")

    print("=" * 60)

    return True

def main():
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else "auth.json"

    try:
        validate_auth_file(filename)
    except Exception as e:
        print(f"\n❌ 验证出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
