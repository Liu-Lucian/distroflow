"""AI-powered keyword extraction from product descriptions"""

from typing import List, Dict
from anthropic import Anthropic
from openai import OpenAI
from .config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordExtractor:
    """Extract relevant keywords and search terms using LLM"""

    def __init__(self):
        self.provider = config.get_llm_provider()

        if self.provider == "anthropic":
            self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        elif self.provider == "openai":
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            raise ValueError("No valid LLM API key found")

    def extract_keywords(self, product_description: str) -> Dict[str, List[str]]:
        """
        Extract keywords from product description

        Args:
            product_description: Description of the product/service

        Returns:
            Dictionary with keywords, hashtags, and target personas
        """
        prompt = f"""Analyze this product/service description and extract:
1. 10-15 relevant keywords for Twitter search
2. 5-10 relevant hashtags (without #)
3. 5 target persona descriptions (who would be interested)

Product Description:
{product_description}

IMPORTANT: Return ONLY valid JSON, no explanations or markdown. Use this exact format:
{{
    "keywords": ["keyword1", "keyword2", ...],
    "hashtags": ["hashtag1", "hashtag2", ...],
    "personas": ["persona1", "persona2", ...]
}}

Return the JSON now:"""

        if self.provider == "anthropic":
            return self._extract_with_anthropic(prompt)
        else:
            return self._extract_with_openai(prompt)

    def _extract_with_anthropic(self, prompt: str) -> Dict[str, List[str]]:
        """Use Claude to extract keywords"""
        import json
        import re

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            content = message.content[0].text
        except Exception as e:
            logger.warning(f"Anthropic API error: {e}. Trying OpenAI fallback...")
            # Fallback to OpenAI if Anthropic fails
            if config.OPENAI_API_KEY:
                return self._extract_with_openai(prompt)
            else:
                raise

        # Parse JSON response

        # Extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Try to find JSON object in the content
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            content = json_match.group(0)

        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            # If JSON parsing fails, return a default structure
            logger.error(f"Failed to parse JSON from Claude response: {e}")
            logger.debug(f"Response content: {content}")

            # Return basic keywords based on simple analysis
            return {
                "keywords": ["product", "service", "business", "solution", "platform"],
                "hashtags": ["business", "tech", "innovation"],
                "personas": ["business owners", "entrepreneurs", "professionals"]
            }

    def _extract_with_openai(self, prompt: str) -> Dict[str, List[str]]:
        """Use GPT to extract keywords"""
        import json

        if not hasattr(self, 'client') or not isinstance(self.client, OpenAI):
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Cheaper and faster
                messages=[
                    {"role": "system", "content": "You are a marketing expert. Return responses in valid JSON format only, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=1024
            )

            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Return basic fallback
            return {
                "keywords": ["product", "service", "business", "solution", "platform"],
                "hashtags": ["business", "tech", "innovation"],
                "personas": ["business owners", "entrepreneurs", "professionals"]
            }

    def generate_search_queries(self, keywords: List[str], hashtags: List[str]) -> List[str]:
        """
        Generate Twitter search queries from keywords and hashtags

        Args:
            keywords: List of keywords
            hashtags: List of hashtags

        Returns:
            List of search query strings
        """
        queries = []

        # Single keyword queries
        for keyword in keywords[:10]:
            queries.append(keyword)

        # Hashtag queries
        for hashtag in hashtags[:5]:
            queries.append(f"#{hashtag}")

        # Combined queries
        if len(keywords) >= 2:
            queries.append(f"{keywords[0]} {keywords[1]}")

        return queries


# Example usage
if __name__ == "__main__":
    extractor = KeywordExtractor()

    sample_description = """
    We provide AI-powered customer service automation for e-commerce businesses.
    Our platform helps online stores reduce support costs by 60% while improving
    customer satisfaction through intelligent chatbots and automated workflows.
    """

    results = extractor.extract_keywords(sample_description)
    print("Keywords:", results["keywords"])
    print("Hashtags:", results["hashtags"])
    print("Personas:", results["personas"])

    queries = extractor.generate_search_queries(
        results["keywords"],
        results["hashtags"]
    )
    print("\nSearch Queries:", queries)
