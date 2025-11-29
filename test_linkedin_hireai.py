#!/usr/bin/env python3
"""
LinkedIn发布 - HireMeAI (即答侠) 产品介绍
"""
import sys
sys.path.insert(0, 'src')

from linkedin_poster import LinkedInPoster
import logging

logging.basicConfig(level=logging.INFO)

# HireMeAI产品LinkedIn帖子
linkedin_content = {
    'content': '''🚀 Introducing HireMeAI (即答侠) - Your AI Interview Assistant

Transform your interview preparation with the next-generation AI-powered interview assistance platform.

🎯 What Makes HireMeAI Different:

✅ Real-Time Voice Assistant
• 95%+ accuracy in speech recognition (Chinese + English)
• Intelligent speaker identification - distinguishes interviewer vs interviewee
• <1s first-word latency for instant responses
• Azure Speech + Picovoice Eagle technology

✅ Smart Resume Optimizer
• ATS scoring system with 4-dimensional analysis
• STAR framework enhancement
• Personalized versions for different companies
• 85%+ correlation with manual scoring

✅ Personalized Answer Templates
• Deep analysis based on your resume + job description
• 4-tier storage system (CORE/MEDIUM/SHORT/TEMPORARY)
• 1536-dimensional vector semantic matching
• 88%+ semantic matching accuracy

✅ Performance Optimization
• Embedding generation: 1.459s → 0.3s (80% improvement)
• First response latency: 2.7s → 1.0s (60% improvement)
• 90%+ cache hit rate for common questions
• 70%+ API cost savings

💡 Perfect For:
• Job seekers preparing for interviews
• Career training institutions
• HR teams standardizing interview processes

🔧 Tech Stack:
OpenAI GPT-4 | Azure Speech Services | Picovoice Eagle | ChromaDB | Python 3.8+

📊 Results:
• Reduce interview preparation time from days to hours
• Standardized professional answers
• Lower interview anxiety, boost confidence

🌐 Learn More: https://interviewasssistant.com
📧 Contact: liu.lucian6@gmail.com

Making every interview a success story.

#AI #InterviewPrep #CareerDevelopment #JobSearch #HRTech #MachineLearning #SpeechRecognition #NLP #TechInnovation #StartupLife''',
    'post_as': 'personal'
}

def main():
    print('=' * 80)
    print('🔵 LinkedIn - Posting HireMeAI (即答侠) Product Introduction')
    print('=' * 80)

    poster = LinkedInPoster()

    try:
        print('\n🌐 Setting up browser...')
        poster.setup_browser(headless=False)

        print('🔐 Verifying login...')
        if not poster.verify_login():
            print('❌ Login verification failed')
            print('   Please run: python3 linkedin_login_and_save_auth.py')
            return False

        print('✅ Login verified successfully')
        print(f'\n📝 Content preview ({len(linkedin_content["content"])} characters):')
        print('-' * 80)
        print(linkedin_content['content'][:200] + '...')
        print('-' * 80)

        print('\n📤 Posting to LinkedIn...')
        success = poster.create_post(linkedin_content)

        if success:
            print('\n' + '=' * 80)
            print('✅ HireMeAI (即答侠) posted successfully to LinkedIn!')
            print('=' * 80)
            return True
        else:
            print('\n❌ Posting failed')
            return False

    except Exception as e:
        print(f'\n❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            input('\n⏸️  Press Enter to close browser...')
        except EOFError:
            pass
        poster.close_browser()

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
