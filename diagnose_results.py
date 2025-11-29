#!/usr/bin/env python3
"""
诊断Hunter系统结果 - 找出邮箱率低的原因
"""

import json
import sys
from pathlib import Path

def diagnose_results(json_file: str):
    """诊断结果文件，找出问题"""

    with open(json_file, 'r', encoding='utf-8') as f:
        leads = json.load(f)

    print("=" * 60)
    print("🔍 Hunter系统诊断报告")
    print("=" * 60)
    print(f"\n📊 基础统计:")
    print(f"  总leads: {len(leads)}")

    # 统计各种情况
    with_email_bio = 0
    with_email_deep = 0
    with_email_guessed = 0
    with_website = 0
    with_name = 0
    deep_scraped = 0
    has_external_links = 0

    # 详细分析
    no_email_reasons = {
        'no_website': [],
        'no_name': [],
        'website_scrape_failed': [],
        'no_external_links': [],
        'pattern_guess_failed': []
    }

    for lead in leads:
        username = lead.get('username')
        name = lead.get('name', '')
        website = lead.get('website')
        bio = lead.get('bio', '')
        contacts = lead.get('all_contacts', {})
        emails = contacts.get('emails', [])

        # 统计
        if emails:
            source = lead.get('email_source', 'found')
            if source == 'found':
                with_email_bio += 1
            elif source == 'website':
                with_email_deep += 1
            elif source in ['pattern_guessed', 'llm_inferred']:
                with_email_guessed += 1

        if website:
            with_website += 1
        if name and len(name.split()) >= 2:
            with_name += 1
        if lead.get('deep_scraped'):
            deep_scraped += 1
        if lead.get('external_links'):
            has_external_links += 1

        # 分析没有邮箱的原因
        if not emails:
            if not website:
                no_email_reasons['no_website'].append(username)
            elif not name or len(name.split()) < 2:
                no_email_reasons['no_name'].append(username)
            elif not lead.get('external_links'):
                no_email_reasons['no_external_links'].append(username)
            else:
                no_email_reasons['pattern_guess_failed'].append(username)

    # 打印统计
    print(f"\n📧 邮箱来源:")
    print(f"  Bio中找到: {with_email_bio}")
    print(f"  深度爬取找到: {with_email_deep}")
    print(f"  推测/推断: {with_email_guessed}")
    print(f"  总计: {with_email_bio + with_email_deep + with_email_guessed}")

    print(f"\n🔍 深度爬取:")
    print(f"  深度爬取的leads: {deep_scraped}")
    print(f"  有外部链接: {has_external_links}")

    print(f"\n📊 数据完整性:")
    print(f"  有网站: {with_website} ({with_website/len(leads)*100:.1f}%)")
    print(f"  有完整姓名: {with_name} ({with_name/len(leads)*100:.1f}%)")

    # 分析问题
    print(f"\n❌ 没有邮箱的原因分析:")
    no_email_total = len(leads) - (with_email_bio + with_email_deep + with_email_guessed)

    if no_email_reasons['no_website']:
        print(f"  缺少网站: {len(no_email_reasons['no_website'])} ({len(no_email_reasons['no_website'])/no_email_total*100:.1f}%)")
        print(f"    示例: {', '.join(['@' + u for u in no_email_reasons['no_website'][:3]])}")

    if no_email_reasons['no_name']:
        print(f"  缺少姓名: {len(no_email_reasons['no_name'])} ({len(no_email_reasons['no_name'])/no_email_total*100:.1f}%)")
        print(f"    示例: {', '.join(['@' + u for u in no_email_reasons['no_name'][:3]])}")

    if no_email_reasons['no_external_links']:
        print(f"  没有外部链接: {len(no_email_reasons['no_external_links'])} ({len(no_email_reasons['no_external_links'])/no_email_total*100:.1f}%)")
        print(f"    示例: {', '.join(['@' + u for u in no_email_reasons['no_external_links'][:3]])}")

    if no_email_reasons['pattern_guess_failed']:
        print(f"  推测失败: {len(no_email_reasons['pattern_guess_failed'])} ({len(no_email_reasons['pattern_guess_failed'])/no_email_total*100:.1f}%)")
        print(f"    示例: {', '.join(['@' + u for u in no_email_reasons['pattern_guess_failed'][:3]])}")

    # 检查推测功能是否工作
    print(f"\n🔧 功能检查:")

    # 检查是否有可以推测但没推测的
    can_guess = 0
    for lead in leads:
        if not lead.get('all_contacts', {}).get('emails'):
            name = lead.get('name', '')
            website = lead.get('website')
            if name and len(name.split()) >= 2 and website:
                can_guess += 1

    if can_guess > 0:
        print(f"  ⚠️ 有 {can_guess} 个leads可以推测邮箱但没有推测")
        print(f"     原因: 邮箱推断模块可能没有正确执行")

    # 检查深度爬取
    if deep_scraped == 0:
        print(f"  ⚠️ 没有深度爬取任何lead")
        print(f"     原因: 深度爬取模块可能没有启用")

    # 建议
    print(f"\n💡 优化建议:")

    if no_email_reasons['no_website']:
        print(f"  1. 从bio中提取更多网站 (当前有 {len(no_email_reasons['no_website'])} 个缺少网站)")

    if can_guess > 0:
        print(f"  2. 启用邮箱推断功能 ({can_guess} 个可推测)")

    if deep_scraped < len(leads) * 0.5:
        print(f"  3. 增加深度爬取比例 (当前只爬了 {deep_scraped}/{len(leads)})")

    if has_external_links < len(leads) * 0.3:
        print(f"  4. 改进外部链接发现 (当前只有 {has_external_links}/{len(leads)} 有外部链接)")

    print("\n" + "=" * 60)

    # 展示成功案例
    print(f"\n✅ 成功案例分析:")
    success_cases = [l for l in leads if l.get('all_contacts', {}).get('emails')]
    if success_cases:
        for case in success_cases[:3]:
            print(f"\n  @{case['username']}:")
            print(f"    姓名: {case.get('name')}")
            print(f"    邮箱: {', '.join(case.get('all_contacts', {}).get('emails', []))}")
            print(f"    来源: {case.get('email_source', 'found')}")
            print(f"    网站: {case.get('website', 'N/A')}")
            print(f"    深度爬取: {'是' if case.get('deep_scraped') else '否'}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_results.py <hunter_leads_json_file>")
        print("\nExample:")
        print("  python diagnose_results.py hunter_leads/leads_20251016_153145.json")
        sys.exit(1)

    diagnose_results(sys.argv[1])
