#!/usr/bin/env python3
"""
Hacker News Auto-Poster Test Script
====================================

Tests the HN posting logic WITHOUT actually submitting to Hacker News.

This script:
1. Generates sample Show HN and Ask HN posts using Claude
2. Displays the generated content for review
3. Validates the content quality (casual language, technical focus)
4. Shows what the monthly schedule would look like

Usage:
    python3 test_hackernews_poster.py

    # Or specify how many samples to generate
    python3 test_hackernews_poster.py --show-hn 2 --ask-hn 3
"""

import json
import os
import re
from datetime import datetime, timedelta
from anthropic import Anthropic

# ==================== Configuration ====================

# Product information
PRODUCT_URL = "https://interviewassistant.com"  # Update with real URL
PRODUCT_DESCRIPTION = """
AI面试实时辅助系统 (HireMeAI / 即答侠)
- Real-time interview assistance using GPT-4o
- First-byte latency: 2.7s → 1.0s (60% improvement)
- Azure Speech SDK for streaming ASR
- Picovoice Eagle for speaker recognition (95% accuracy)
- ChromaDB vector similarity search
- Dual-level caching architecture
"""

# API configuration
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', 'sk-ant-YOUR_ANTHROPIC_API_KEY_HERE')

# ==================== Content Generation ====================

class HackerNewsContentTester:
    """Test Hacker News content generation without posting"""

    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.product_url = PRODUCT_URL
        self.product_description = PRODUCT_DESCRIPTION

    def generate_show_hn_post(self) -> dict:
        """Generate a Show HN post sample"""

        prompt = f"""You are a technical founder building an AI interview assistant. You want to share it on Hacker News in a genuine, casual way.

Product context:
{self.product_description}

CRITICAL REQUIREMENTS:
1. **Tone**: Casual technical founder vibe (use lol, tbh, ngl, imo, glhf naturally)
2. **Authenticity**: Sound like you're sharing a side project, NOT selling a product
3. **Technical Focus**: Share engineering challenges you solved, not features
4. **HN Community Standards**:
   - NO marketing language ("best", "amazing", "revolutionary")
   - NO calls to action ("try it now", "sign up", "check it out")
   - YES technical details, honest reflections, asking for feedback

GOOD EXAMPLES (HN style):
✅ "Show HN: Real-time AI interview coach (tbh the latency was a nightmare)"
✅ "Show HN: Interview assistant using GPT-4o + Azure Speech (feedback welcome)"
✅ "Show HN: Built an AI interview helper (ngl the speaker recognition was hard)"

BAD EXAMPLES (marketing style):
❌ "Show HN: The Best AI Interview Tool You'll Ever Use!"
❌ "Show HN: Revolutionary Interview Assistant - Try it Free!"

Title requirements:
- Start with "Show HN: "
- 8-12 words max
- Include one technical detail or honest reflection
- Sound humble and authentic

Body structure (200-300 words):
1. **Context** (1-2 sentences): Honest intro
   - Example: "Been working on this for 3 months, ngl it's been quite a journey..."

2. **Technical Challenge** (2-3 sentences): Share 1-2 real problems you solved
   - Example: "The hardest part was getting sub-second latency. Started at 2.7s first-byte, which felt terrible. After adding dual-level caching and precomputing common answers, got it down to ~1s."

3. **Stack/Metrics** (2-3 sentences): Specific tech details
   - Example: "Stack: GPT-4o for generation, Azure Speech for real-time ASR, Picovoice Eagle for speaker diarization. Currently hitting 95% accuracy on voice recognition."

4. **Asking for Feedback** (1-2 sentences): Genuine question
   - Example: "tbh I'm not sure if 1s latency is good enough. Anyone here built real-time AI stuff? Any advice appreciated!"

Output ONLY valid JSON (no markdown code fences):
{{
  "title": "Show HN: Your title here",
  "url": "{self.product_url}",
  "text": "Your post body here..."
}}

IMPORTANT:
- Use casual language naturally (lol, tbh, ngl, imo, glhf)
- Sound like a real engineer sharing, not a marketer selling
- Focus on what you learned, not what the product does
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            temperature=0.9,  # Higher for natural variation
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text.strip()

        # Remove markdown code fences if present
        if response.startswith('```'):
            response = re.sub(r'^```(?:json)?\n', '', response)
            response = re.sub(r'\n```$', '', response)

        # Try direct parsing first
        try:
            post_data = json.loads(response)
            post_data['generated_at'] = datetime.now().isoformat()
            return post_data
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON with more lenient parsing
            # Claude sometimes puts unescaped newlines in strings
            try:
                # Use json5 approach: find the JSON structure manually
                import ast
                # Try to fix by replacing unescaped newlines in the text field
                fixed_response = response.replace('\n', '\\n')
                # Unescape the intentional structure newlines
                fixed_response = fixed_response.replace('{\\n', '{\n').replace('\\n}', '\n}')
                fixed_response = fixed_response.replace(',\\n', ',\n').replace('"\\n  "', '"\n  "')

                post_data = json.loads(fixed_response)
                post_data['generated_at'] = datetime.now().isoformat()
                return post_data
            except Exception as e:
                print(f"⚠️  JSON parsing error: {e}")
                print(f"Raw response:\n{response}")
                return None

    def generate_ask_hn_post(self) -> dict:
        """Generate an Ask HN post sample"""

        # Topic pool for Ask HN posts
        topics = [
            "real-time AI streaming latency optimization",
            "voice recognition in production (speaker diarization challenges)",
            "vector similarity search at scale (ChromaDB, FAISS, etc.)",
            "reducing GPT API costs with intelligent caching",
            "WebSocket vs SSE for real-time AI applications",
            "handling speech recognition in noisy environments",
            "building sub-second AI response systems",
            "dual-level caching strategies for AI apps"
        ]

        import random
        selected_topic = random.choice(topics)

        prompt = f"""You are a technical founder building an AI interview assistant. You want to ask the HN community for advice about: {selected_topic}

Product context (for reference only):
{self.product_description}

CRITICAL REQUIREMENTS:
1. **Tone**: Casual, genuinely curious (use lol, tbh, ngl, imo, glhf naturally)
2. **Purpose**: REAL technical question, not disguised marketing
3. **Share Context**: Briefly mention what you're building, focus on the challenge
4. **HN Standards**:
   - Ask genuine questions that help other builders too
   - Share specific numbers/metrics
   - Be humble and curious
   - DON'T pitch your product features

GOOD EXAMPLES:
✅ "Ask HN: How to get sub-1s latency with GPT-4o streaming? (currently at 1.2s)"
✅ "Ask HN: Best practices for speaker diarization in production?"
✅ "Ask HN: WebSockets vs SSE for real-time AI? (tbh not sure which)"

BAD EXAMPLES:
❌ "Ask HN: What do you think of my amazing interview assistant?"
❌ "Ask HN: How can I market my AI product better?"

Title requirements:
- Start with "Ask HN: "
- Specific question about {selected_topic}
- Include context or metric if possible
- 10-15 words max

Body structure (150-250 words):
1. **Context** (2-3 sentences): What you're building and why this matters
   - Example: "I'm building a real-time interview assistant, tbh sub-1s first-byte is hard. Currently using GPT-4o + Azure Speech."

2. **Current Approach** (2-4 sentences): Share what you've tried with metrics
   - Example: "We've gotten first-byte from 2.7s → 1.0s through:
     - Precomputing answers (80% hit rate)
     - Dual-level caching
     - Streaming SSE responses

     But 1s still feels slow for voice interactions."

3. **Specific Question** (1-2 sentences): What you want advice on
   - Example: "Anyone here hit sub-500ms with GPT-4o? Is switching to WebSockets worth it, or should I focus on better prompt caching?"

4. **Humble Close** (1 sentence):
   - Example: "ngl this is my first time building real-time AI stuff, any advice appreciated!"

Output ONLY valid JSON (no markdown code fences):
{{
  "title": "Ask HN: Your question here",
  "text": "Your post body here..."
}}

IMPORTANT:
- Use casual language naturally (lol, tbh, ngl, imo)
- Ask questions that genuinely help you AND the community
- Share real metrics and technical details
- DON'T mention product features, only technical challenges
"""

        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=600,
            temperature=0.9,
            messages=[{"role": "user", "content": prompt}]
        )

        response = message.content[0].text.strip()

        # Remove markdown code fences if present
        if response.startswith('```'):
            response = re.sub(r'^```(?:json)?\n', '', response)
            response = re.sub(r'\n```$', '', response)

        # Try direct parsing first
        try:
            post_data = json.loads(response)
            post_data['generated_at'] = datetime.now().isoformat()
            post_data['topic'] = selected_topic
            return post_data
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON with more lenient parsing
            try:
                # Fix unescaped newlines in strings
                fixed_response = response.replace('\n', '\\n')
                # Unescape the intentional structure newlines
                fixed_response = fixed_response.replace('{\\n', '{\n').replace('\\n}', '\n}')
                fixed_response = fixed_response.replace(',\\n', ',\n').replace('"\\n  "', '"\n  "')

                post_data = json.loads(fixed_response)
                post_data['generated_at'] = datetime.now().isoformat()
                post_data['topic'] = selected_topic
                return post_data
            except Exception as e:
                print(f"⚠️  JSON parsing error: {e}")
                print(f"Raw response:\n{response}")
                return None

    def validate_content(self, post_data: dict, post_type: str) -> dict:
        """Validate if generated content meets HN standards"""

        validation = {
            'passed': True,
            'warnings': [],
            'insights': []
        }

        title = post_data.get('title', '')
        text = post_data.get('text', '')
        combined = f"{title} {text}".lower()

        # Check for marketing language (bad)
        marketing_words = ['best', 'amazing', 'revolutionary', 'incredible', 'game-changing',
                          'try it', 'sign up', 'check out', 'click here', 'free trial']
        found_marketing = [word for word in marketing_words if word in combined]
        if found_marketing:
            validation['warnings'].append(f"⚠️  Marketing language detected: {', '.join(found_marketing)}")
            validation['passed'] = False

        # Check for casual language (good)
        casual_words = ['lol', 'tbh', 'ngl', 'imo', 'glhf', 'imho', 'afaik', 'fwiw']
        found_casual = [word for word in casual_words if word in combined]
        if found_casual:
            validation['insights'].append(f"✅ Casual language used: {', '.join(found_casual)}")
        else:
            validation['warnings'].append("⚠️  No casual internet slang detected (add lol, tbh, ngl, etc.)")

        # Check for technical terms (good)
        tech_terms = ['latency', 'api', 'stack', 'caching', 'performance', 'ms', 'accuracy',
                     'streaming', 'real-time', 'optimization', 'architecture']
        found_tech = [term for term in tech_terms if term in combined]
        if found_tech:
            validation['insights'].append(f"✅ Technical terms: {', '.join(found_tech[:3])}...")

        # Check title length
        title_words = len(title.split())
        if title_words > 15:
            validation['warnings'].append(f"⚠️  Title too long ({title_words} words, recommend 8-12)")
        else:
            validation['insights'].append(f"✅ Title length OK ({title_words} words)")

        # Check for metrics (good)
        if re.search(r'\d+(\.\d+)?\s*(s|ms|%)', combined):
            validation['insights'].append("✅ Specific metrics included")

        return validation

# ==================== Test Execution ====================

def print_separator(title: str):
    """Print a nice separator"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def print_post(post_data: dict, post_type: str, index: int = None):
    """Pretty print a generated post"""

    header = f"{post_type}"
    if index is not None:
        header += f" #{index}"

    print(f"\n{'─' * 80}")
    print(f"📝 {header}")
    print(f"{'─' * 80}\n")

    print(f"**Title:**")
    print(f"  {post_data['title']}\n")

    if post_data.get('url'):
        print(f"**URL:**")
        print(f"  {post_data['url']}\n")

    print(f"**Body:**")
    for line in post_data['text'].split('\n'):
        print(f"  {line}")

    print(f"\n**Metadata:**")
    print(f"  Generated at: {post_data.get('generated_at', 'N/A')}")
    if post_data.get('topic'):
        print(f"  Topic: {post_data['topic']}")

def print_validation(validation: dict):
    """Print validation results"""

    print(f"\n{'─' * 80}")
    print("🔍 Validation Results")
    print(f"{'─' * 80}\n")

    if validation['passed']:
        print("✅ **Overall Status:** PASSED")
    else:
        print("⚠️  **Overall Status:** NEEDS IMPROVEMENT")

    if validation['insights']:
        print("\n**Positive Signals:**")
        for insight in validation['insights']:
            print(f"  {insight}")

    if validation['warnings']:
        print("\n**Warnings:**")
        for warning in validation['warnings']:
            print(f"  {warning}")

def test_content_generation(num_show_hn: int = 1, num_ask_hn: int = 3):
    """Test the content generation logic"""

    print_separator("Hacker News Auto-Poster Test")

    print("Testing content generation WITHOUT actually posting to HN...\n")
    print(f"Configuration:")
    print(f"  - Show HN samples: {num_show_hn}")
    print(f"  - Ask HN samples: {num_ask_hn}")
    print(f"  - Product URL: {PRODUCT_URL}")
    print(f"  - API Key: {ANTHROPIC_API_KEY[:20]}...")

    tester = HackerNewsContentTester()

    # Generate Show HN samples
    print_separator("Show HN Samples")

    for i in range(num_show_hn):
        print(f"\n🎯 Generating Show HN sample {i+1}/{num_show_hn}...")

        post_data = tester.generate_show_hn_post()
        if post_data:
            print_post(post_data, "Show HN", i+1)

            validation = tester.validate_content(post_data, "Show HN")
            print_validation(validation)
        else:
            print(f"❌ Failed to generate Show HN sample {i+1}")

    # Generate Ask HN samples
    print_separator("Ask HN Samples")

    for i in range(num_ask_hn):
        print(f"\n🎯 Generating Ask HN sample {i+1}/{num_ask_hn}...")

        post_data = tester.generate_ask_hn_post()
        if post_data:
            print_post(post_data, "Ask HN", i+1)

            validation = tester.validate_content(post_data, "Ask HN")
            print_validation(validation)
        else:
            print(f"❌ Failed to generate Ask HN sample {i+1}")

    # Summary
    print_separator("Test Summary")

    print("✅ Content generation test complete!\n")
    print("**Next Steps:**")
    print("1. Review the generated content above")
    print("2. Check if the tone is casual and authentic (lol, tbh, ngl, etc.)")
    print("3. Verify technical focus (not marketing language)")
    print("4. If satisfied, run the actual poster:")
    print("   python3 hackernews_auto_poster.py --generate-schedule")
    print("\n**Cost Estimate:**")
    print(f"  - This test: ~${0.002 * (num_show_hn + num_ask_hn):.4f}")
    print(f"  - Monthly schedule (1 Show HN + 4 Ask HN): ~$0.01")

# ==================== Main ====================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test HN Auto-Poster content generation")
    parser.add_argument('--show-hn', type=int, default=1, help='Number of Show HN samples (default: 1)')
    parser.add_argument('--ask-hn', type=int, default=3, help='Number of Ask HN samples (default: 3)')

    args = parser.parse_args()

    test_content_generation(num_show_hn=args.show_hn, num_ask_hn=args.ask_hn)
