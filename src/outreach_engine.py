"""AI-powered personalized outreach message generator"""

from typing import Dict, Optional
from anthropic import Anthropic
from openai import OpenAI
from .config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OutreachEngine:
    """Generate personalized outreach messages"""

    def __init__(self):
        self.provider = config.get_llm_provider()

        if self.provider == "anthropic":
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        elif self.provider == "openai":
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            raise ValueError("No valid LLM API key found")

    def generate_connection_message(
        self,
        lead_data: Dict,
        product_description: str,
        tone: str = "professional"
    ) -> str:
        """
        Generate a personalized connection/follow message

        Args:
            lead_data: Dictionary with lead information
            product_description: Your product/service description
            tone: Message tone (professional, casual, friendly)

        Returns:
            Personalized message text
        """
        name = lead_data.get('name', 'there')
        bio = lead_data.get('description', '')
        username = lead_data.get('username', '')

        prompt = f"""Generate a personalized Twitter connection message.

Target Person:
- Name: {name}
- Username: @{username}
- Bio: {bio}

Our Product/Service:
{product_description}

Requirements:
1. Keep it under 280 characters (Twitter DM limit)
2. Be {tone} and authentic
3. Reference something specific from their bio if possible
4. Briefly mention how our product could help them
5. Include a soft call-to-action
6. Do NOT be salesy or pushy
7. Make it feel personal, not automated

Generate only the message text, no quotes or extra formatting.
"""

        if self.provider == "anthropic":
            return self._generate_with_anthropic(prompt)
        else:
            return self._generate_with_openai(prompt)

    def generate_intro_dm(
        self,
        lead_data: Dict,
        product_description: str,
        common_interest: Optional[str] = None
    ) -> str:
        """
        Generate a personalized intro DM after connection

        Args:
            lead_data: Lead information
            product_description: Product description
            common_interest: Any common interest identified

        Returns:
            DM text
        """
        name = lead_data.get('name', 'there')
        bio = lead_data.get('description', '')

        interest_context = f"\nCommon Interest: {common_interest}" if common_interest else ""

        prompt = f"""Generate a personalized intro direct message for Twitter.

Recipient:
- Name: {name}
- Bio: {bio}{interest_context}

Our Product/Service:
{product_description}

Requirements:
1. Start with a friendly greeting
2. Keep the entire message under 400 characters
3. Mention why you're reaching out specifically to them
4. Briefly explain what we do and the value we provide
5. Ask an engaging question or suggest a conversation starter
6. Be conversational, not promotional
7. End with your name/company

Generate only the message text.
"""

        if self.provider == "anthropic":
            return self._generate_with_anthropic(prompt)
        else:
            return self._generate_with_openai(prompt)

    def generate_email(
        self,
        lead_data: Dict,
        product_description: str,
        subject_line: bool = True
    ) -> Dict[str, str]:
        """
        Generate a personalized email

        Args:
            lead_data: Lead information
            product_description: Product description
            subject_line: Whether to generate subject line

        Returns:
            Dictionary with 'subject' and 'body'
        """
        name = lead_data.get('name', 'there')
        bio = lead_data.get('description', '')
        company = lead_data.get('company', '')

        prompt = f"""Generate a personalized cold email.

Recipient:
- Name: {name}
- Bio: {bio}
- Company: {company if company else 'Unknown'}

Our Product/Service:
{product_description}

Requirements:
1. {"Generate a compelling subject line (max 50 chars)" if subject_line else ""}
2. Keep email body concise (200-300 words)
3. Use a professional but friendly tone
4. Personalize based on their background
5. Clearly explain the value proposition
6. Include a clear call-to-action
7. Format in plain text, not HTML

Return format:
Subject: [subject line]

[email body]
"""

        response = None
        if self.provider == "anthropic":
            response = self._generate_with_anthropic(prompt)
        else:
            response = self._generate_with_openai(prompt)

        # Parse subject and body
        if "Subject:" in response:
            parts = response.split("\n", 1)
            subject = parts[0].replace("Subject:", "").strip()
            body = parts[1].strip() if len(parts) > 1 else ""
        else:
            subject = f"Quick question for {name}"
            body = response

        return {
            "subject": subject,
            "body": body
        }

    def _generate_with_anthropic(self, prompt: str) -> str:
        """Generate with Claude"""
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text.strip()

    def _generate_with_openai(self, prompt: str) -> str:
        """Generate with GPT"""
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at writing personalized, effective outreach messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()


# Example usage
if __name__ == "__main__":
    engine = OutreachEngine()

    sample_lead = {
        'name': 'Sarah Johnson',
        'username': 'sarahj_tech',
        'description': 'Product Manager at SaaS startup. Passionate about AI and automation. Building better tools for teams.',
    }

    product = """
    AI-powered customer service automation for e-commerce.
    Reduce support costs by 60% while improving customer satisfaction.
    """

    # Generate connection message
    connection_msg = engine.generate_connection_message(sample_lead, product, "friendly")
    print("Connection Message:")
    print(connection_msg)
    print(f"\nLength: {len(connection_msg)} characters")

    # Generate intro DM
    intro_dm = engine.generate_intro_dm(sample_lead, product)
    print("\n\nIntro DM:")
    print(intro_dm)

    # Generate email
    email = engine.generate_email(sample_lead, product)
    print("\n\nEmail:")
    print(f"Subject: {email['subject']}")
    print(f"\n{email['body']}")
