#!/usr/bin/env python3
"""
手动创建 auth.json 文件
Manually create auth.json file

只需要输入关键的 cookies（auth_token 和 ct0）即可
Only need key cookies (auth_token and ct0)
"""

import json
import os

def create_auth_from_manual_input():
    """通过手动输入创建 auth.json"""

    print("=" * 60)
    print("🔐 手动创建 Twitter Auth 文件")
    print("   Manually Create Twitter Auth File")
    print("=" * 60)
    print()

    print("📝 你需要提供以下 cookies：")
    print("   You need to provide the following cookies:")
    print()
    print("1. auth_token - Twitter 登录令牌（必需）")
    print("2. ct0 - CSRF 令牌（必需）")
    print("3. twid - 用户ID（可选但推荐）")
    print()

    print("=" * 60)
    print("📖 如何获取这些值？")
    print("=" * 60)
    print()
    print("方法1: 使用浏览器开发者工具")
    print("  1. 在 Chrome/Safari 中登录 Twitter")
    print("  2. 按 F12 或 Cmd+Option+I 打开开发者工具")
    print("  3. 点击 'Application' 或 '应用' 标签")
    print("  4. 左侧展开 'Cookies' → 选择 'https://twitter.com'")
    print("  5. 找到 auth_token 和 ct0，复制它们的值")
    print()

    print("方法2: 使用浏览器控制台")
    print("  1. 在 Twitter 页面按 Cmd+Option+J (Chrome) 或 Cmd+Option+C (Safari)")
    print("  2. 在控制台输入: document.cookie")
    print("  3. 在输出中找到 auth_token= 和 ct0= 后面的值")
    print()

    print("=" * 60)
    print()

    # 获取 auth_token
    print("请输入 auth_token 的值:")
    print("(通常是一个很长的字符串，40个字符左右)")
    auth_token = input("auth_token: ").strip()

    if not auth_token:
        print("❌ auth_token 不能为空")
        return False

    # 获取 ct0
    print()
    print("请输入 ct0 的值:")
    print("(通常是一个32位的十六进制字符串)")
    ct0 = input("ct0: ").strip()

    if not ct0:
        print("❌ ct0 不能为空")
        return False

    # 获取 twid（可选）
    print()
    print("请输入 twid 的值 (可选，直接按 Enter 跳过):")
    twid = input("twid: ").strip()

    # 创建 cookies
    cookies = [
        {
            "name": "auth_token",
            "value": auth_token,
            "domain": ".twitter.com",
            "path": "/",
            "expires": -1,
            "httpOnly": True,
            "secure": True,
            "sameSite": "None"
        },
        {
            "name": "ct0",
            "value": ct0,
            "domain": ".twitter.com",
            "path": "/",
            "expires": -1,
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax"
        }
    ]

    # 如果提供了 twid，添加它
    if twid:
        cookies.append({
            "name": "twid",
            "value": twid,
            "domain": ".twitter.com",
            "path": "/",
            "expires": -1,
            "httpOnly": False,
            "secure": True,
            "sameSite": "None"
        })

    # 创建完整的 auth state
    auth_state = {
        "cookies": cookies,
        "origins": [
            {
                "origin": "https://twitter.com",
                "localStorage": []
            }
        ]
    }

    # 保存到文件
    output_file = "auth.json"

    print()
    print("=" * 60)
    print("💾 保存到文件...")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(auth_state, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(output_file)

        print("=" * 60)
        print("✅ 成功创建 auth.json！")
        print("=" * 60)
        print(f"📄 文件: {output_file}")
        print(f"📊 大小: {file_size} bytes")
        print(f"🍪 Cookies: {len(cookies)} 个")
        print()
        print("包含的 cookies:")
        for cookie in cookies:
            value = cookie['value']
            display_value = value[:15] + '...' if len(value) > 15 else value
            print(f"  ✓ {cookie['name']}: {display_value}")
        print()
        print("=" * 60)
        print("🎉 完成！现在可以测试爬虫了：")
        print("   python quick_scrape_playwright.py elonmusk 10")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False

def main():
    try:
        success = create_auth_from_manual_input()
        if not success:
            print()
            print("⚠️  创建失败，请重试")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
