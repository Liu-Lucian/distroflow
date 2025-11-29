#!/usr/bin/env python3
"""
测试无中文品牌内容生成
"""
import sys
sys.path.insert(0, 'src')
from social_content_transformer import SocialContentTransformer
import json

print('🔄 Generating NEW test content with updated branding...')
print('   ✅ Removed Chinese text (即答侠)')
print('   ✅ Using only "HireMeAI"')
print()

transformer = SocialContentTransformer()

# Generate Twitter test content
test_article = '''
# Top AI Tools for Job Seekers to Ace Interviews

In today's competitive job market, standing out is crucial. AI-powered interview preparation tools are transforming how job seekers prepare for interviews.

## Why Use AI for Interview Prep?

1. **Personalized Practice**: AI analyzes your responses and provides tailored feedback
2. **Real-time Coaching**: Get instant suggestions during practice sessions
3. **Industry-Specific Questions**: Practice with questions relevant to your field
4. **Data-Driven Insights**: Understand what employers are looking for

These tools help job seekers build confidence and improve their interview performance significantly.
'''

print('📝 Generating Twitter thread...')
twitter_result = transformer.transform_for_twitter(test_article, 'Top AI Tools for Job Seekers')

print('✅ Twitter content generated!')
print()
print('=' * 80)
print('SAMPLE TWITTER THREAD (No Chinese Text)')
print('=' * 80)
for i, tweet in enumerate(twitter_result['tweets'], 1):
    print(f'\nTweet {i}/{len(twitter_result["tweets"])}:')
    print(tweet)
    print('-' * 40)

# Save to file
output = {'twitter': twitter_result}
with open('test_brand_no_chinese.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print()
print('✅ Saved to test_brand_no_chinese.json')
print()
print('🔍 Verification:')
full_text = ' '.join(twitter_result['tweets'])
if '即答侠' in full_text:
    print('   ❌ WARNING: Chinese text still found!')
else:
    print('   ✅ NO Chinese text found - branding is clean!')

if 'HireMeAI' in full_text:
    print('   ✅ "HireMeAI" mentioned correctly')
else:
    print('   ⚠️  "HireMeAI" not found in content')

if 'https://interviewasssistant.com' in full_text:
    print('   ✅ Correct URL: https://interviewasssistant.com')
else:
    print('   ⚠️  Correct URL not found')
