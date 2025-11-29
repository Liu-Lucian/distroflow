#!/usr/bin/env python3
"""
调试 Product Hunt 页面 - 查看实际HTML结构
"""
import sys
sys.path.insert(0, 'src')

from producthunt_commenter import ProductHuntCommenter
import time

commenter = ProductHuntCommenter()
commenter.setup_browser(headless=False)  # 非无头模式，可以看到浏览器

if not commenter.verify_login():
    print("❌ 未登录")
    commenter.close_browser()
    sys.exit(1)

print("🌐 访问 Product Hunt /today 页面...")
commenter.page.goto("https://www.producthunt.com/today", timeout=60000)

print("⏳ 等待 10 秒让页面完全加载...")
time.sleep(10)

# 滚动以触发懒加载
print("📜 滚动页面...")
commenter.page.evaluate("window.scrollTo(0, 1500)")
time.sleep(3)
commenter.page.evaluate("window.scrollTo(0, 0)")
time.sleep(2)

# 获取页面HTML并保存
print("💾 保存页面HTML...")
html = commenter.page.content()
with open('debug_ph_today_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"   已保存到 debug_ph_today_page.html ({len(html)} 字符)")

# 截图
print("📸 截图...")
commenter.page.screenshot(path='debug_ph_today_page.png', full_page=True)
print("   已保存到 debug_ph_today_page.png")

# 获取所有链接
print("\n🔗 查找所有包含 /posts/ 的链接...")
all_post_links = commenter.page.query_selector_all('a')
post_links = []
for link in all_post_links:
    href = link.get_attribute('href')
    if href and '/posts/' in href:
        post_links.append(href)

print(f"   找到 {len(post_links)} 个包含 /posts/ 的链接:")
unique_links = list(set(post_links))[:20]
for i, link in enumerate(unique_links, 1):
    print(f"   {i}. {link}")

print("\n✅ 浏览器将保持打开状态，按 Enter 关闭...")
input()

commenter.close_browser()
