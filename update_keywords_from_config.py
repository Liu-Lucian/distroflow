#!/usr/bin/env python3
"""
从product_config.json读取产品描述，用AI生成Instagram关键词
然后自动更新配置文件
"""

import json
import os
from openai import OpenAI

def generate_keywords_with_ai(product_description: str, target_audience: list, pain_points: list) -> list:
    """用AI生成Instagram关键词"""

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    prompt = f"""Based on this product information, generate 15 Instagram hashtag keywords that will help find potential customers.

**Product**: {product_description}

**Target Audience**: {', '.join(target_audience)}

**Pain Points**: {', '.join(pain_points)}

**Requirements**:
1. Keywords must be popular on Instagram
2. Single words or concatenated phrases (no spaces)
3. In English
4. Related to job seeking, career development, interviews, etc.
5. Mix of broad and specific keywords

**Output Format**: Return ONLY a JSON array of strings, nothing else.

Example: ["jobsearch", "interviewtips", "careerdevelopment"]
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a social media marketing expert. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    response_text = response.choices[0].message.content.strip()

    # 提取JSON
    if "```json" in response_text:
        json_start = response_text.find("```json") + 7
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()
    elif "```" in response_text:
        json_start = response_text.find("```") + 3
        json_end = response_text.find("```", json_start)
        response_text = response_text[json_start:json_end].strip()

    keywords = json.loads(response_text)
    return keywords

def main():
    print("=" * 70)
    print("🤖 AI Keyword Generator for Instagram")
    print("=" * 70)

    # 读取配置
    try:
        with open('product_config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ product_config.json not found!")
        return

    product_description = config.get('product_description', '')
    detailed_description = config.get('detailed_description', '')
    target_audience = config.get('target_audience', [])
    pain_points = config.get('pain_points', [])

    print(f"\n📦 Product: {config.get('product_name', 'Unknown')}")
    print(f"📝 Description: {product_description}")
    print(f"🎯 Target: {', '.join(target_audience)}")
    print()

    # 使用详细描述（如果有）
    full_description = f"{product_description}\n\n{detailed_description}" if detailed_description else product_description

    # 生成关键词
    print("🤖 Asking AI to generate keywords...")
    try:
        keywords = generate_keywords_with_ai(full_description, target_audience, pain_points)

        print(f"\n✅ AI generated {len(keywords)} keywords:")
        for i, kw in enumerate(keywords, 1):
            print(f"   {i}. #{kw}")

        # 更新配置文件
        config['keywords_instagram'] = keywords

        with open('product_config.json', 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Updated product_config.json with new keywords")
        print("\nNext step: Run your Instagram campaign!")
        print("  python3 run_instagram_campaign_v2.py")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
