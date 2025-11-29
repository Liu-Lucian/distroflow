"""
文档解析器 - Document Parser
支持 PDF, DOCX, MD, TXT, URL
Parse various document formats for product information
"""

import os
import re
import logging
from typing import List, Dict, Optional
from pathlib import Path

# PDF parsing
try:
    from pdfminer.high_level import extract_text as pdf_extract_text
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("pdfminer not available. Install: pip install pdfminer.six")

# DOCX parsing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    logging.warning("python-docx not available. Install: pip install python-docx")

# Web scraping
try:
    from bs4 import BeautifulSoup
    import requests
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False
    logging.warning("BeautifulSoup not available. Install: pip install beautifulsoup4 requests")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentParser:
    """Parse various document formats"""

    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.md', '.txt', '.html']

    def parse_document(self, path: str) -> str:
        """
        Parse document and return text content

        Args:
            path: File path or URL

        Returns:
            Extracted text content
        """
        # Check if it's a URL
        if path.startswith('http://') or path.startswith('https://'):
            return self._parse_url(path)

        # Check if file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        # Get file extension
        ext = Path(path).suffix.lower()

        # Parse based on extension
        if ext == '.pdf':
            return self._parse_pdf(path)
        elif ext == '.docx':
            return self._parse_docx(path)
        elif ext in ['.md', '.txt']:
            return self._parse_text(path)
        elif ext in ['.html', '.htm']:
            return self._parse_html_file(path)
        else:
            raise ValueError(f"Unsupported format: {ext}")

    def _parse_pdf(self, path: str) -> str:
        """Parse PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("pdfminer.six not installed")

        try:
            text = pdf_extract_text(path)
            logger.info(f"✓ Parsed PDF: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise

    def _parse_docx(self, path: str) -> str:
        """Parse DOCX file"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not installed")

        try:
            doc = docx.Document(path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            logger.info(f"✓ Parsed DOCX: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise

    def _parse_text(self, path: str) -> str:
        """Parse text/markdown file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"✓ Parsed text file: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error parsing text file: {e}")
            raise

    def _parse_html_file(self, path: str) -> str:
        """Parse HTML file"""
        if not WEB_AVAILABLE:
            raise ImportError("beautifulsoup4 not installed")

        try:
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            text = self._clean_text(text)
            logger.info(f"✓ Parsed HTML file: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error parsing HTML file: {e}")
            raise

    def _parse_url(self, url: str) -> str:
        """Parse web page from URL"""
        if not WEB_AVAILABLE:
            raise ImportError("beautifulsoup4 and requests not installed")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text()
            text = self._clean_text(text)
            logger.info(f"✓ Parsed URL: {len(text)} characters from {url}")
            return text
        except Exception as e:
            logger.error(f"Error parsing URL: {e}")
            raise

    def _clean_text(self, text: str) -> str:
        """Clean extracted text"""
        # Remove excessive whitespace
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        text = '\n'.join(lines)

        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks

        Args:
            text: Input text
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)

                if break_point > chunk_size * 0.5:  # At least 50% of chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1

            chunks.append(chunk.strip())
            start = end - overlap

        logger.info(f"✓ Split into {len(chunks)} chunks")
        return chunks


# Example usage
if __name__ == "__main__":
    parser = DocumentParser()

    # Test with markdown
    test_text = """
    # My Product

    We provide fleet management solutions for electric vehicles.
    Our target customers are:
    - Fleet managers
    - Car dealerships
    - EV enthusiasts

    Contact: info@myproduct.com
    """

    print("Test text:")
    print(test_text)

    print("\nChunking:")
    chunks = parser.chunk_text(test_text, chunk_size=100, overlap=20)
    for i, chunk in enumerate(chunks, 1):
        print(f"\nChunk {i}:")
        print(chunk)
