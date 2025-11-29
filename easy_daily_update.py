#!/usr/bin/env python3
"""
每日 30 秒更新 - 最简单的实用方案
步骤：
1. 打开浏览器到 Product Hunt
2. 用户在浏览器 Console 中粘贴一行代码
3. 自动复制 JSON 到剪贴板
4. 粘贴到终端即可
"""
import json
import sys
from datetime import datetime

print("""
╔════════════════════════════════════════════════════════════════╗
║  Product Hunt 每日更新（30秒完成）                             ║
╚════════════════════════════════════════════════════════════════╝

步骤：

1. 打开浏览器访问: https://www.producthunt.com

2. 按 F12 打开开发者工具 → Console 标签页

3. 粘贴以下代码并按回车：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
copy(JSON.stringify(Array.from(document.querySelectorAll('a[href]'))
.filter(a=>a.href.includes('/posts/')&&!a.href.includes('/new'))
.slice(0,10).map(a=>({url:a.href.split('?')[0],name:a.textContent.trim()||'Product',
tagline:'Product from Product Hunt',category:'Various',description:'Auto',votes:0}))));
console.log('✅ 已复制！粘贴到 Python 脚本');
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. 浏览器会显示 "✅ 已复制！粘贴到 Python 脚本"

5. 回到这个终端，粘贴（Cmd+V）并按回车
""")

print("\n⏳ 等待粘贴产品数据...\n")
print("提示：如果浏览器中没有产品，等待 10 秒让页面加载后再试\n")

try:
    # 读取用户粘贴的 JSON
    user_input = input("请粘贴从浏览器复制的数据: ")

    if not user_input or user_input.strip() == '':
        print("\n❌ 未检测到数据")
        print("   请确保在浏览器 Console 中运行了上面的代码")
        sys.exit(1)

    # 解析 JSON
    products = json.loads(user_input)

    if not products or len(products) == 0:
        print("\n❌ 产品列表为空")
        print("   这通常说明页面还在加载中，请：")
        print("   1. 等待页面完全加载（约 10-15 秒）")
        print("   2. 滚动页面到产品列表")
        print("   3. 再次运行浏览器中的代码")
        sys.exit(1)

    # 保存到文件
    data = {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "source": "Browser Console Extraction",
        "products": products,
        "updated_at": datetime.now().isoformat()
    }

    with open('todays_producthunt_products.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ 成功保存 {len(products)} 个产品！")
    print("\n📋 产品列表:")
    for i, p in enumerate(products[:5], 1):
        print(f"   {i}. {p.get('name', 'Unknown')[:50]}")
        print(f"      {p.get('url', '')}")

    if len(products) > 5:
        print(f"   ... 还有 {len(products)-5} 个产品")

    print("\n✅ 更新完成！现在可以运行:")
    print("   python3 auto_producthunt_forever.py")
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 统计: 耗时约 30 秒，系统可全自动运行 24 小时")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

except json.JSONDecodeError:
    print("\n❌ JSON 格式错误")
    print("   请确保完整复制了浏览器中的内容")
    print("   不要手动修改任何字符")
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
