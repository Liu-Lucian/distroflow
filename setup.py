"""
DistroFlow Setup Configuration
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file) as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "playwright>=1.40.0",
        "openai>=1.0.0",
        "anthropic>=0.7.0",
        "click>=8.1.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "aiofiles>=23.2.0",
    ]

setup(
    name="distroflow",
    version="0.1.0",
    author="Lucian Liu",
    author_email="lucian@uci.edu",
    description="Open-source cross-platform distribution infrastructure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Liu-Lucian/distroflow",
    packages=find_packages(exclude=["tests", "examples", "archive"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "distroflow=distroflow.cli:cli",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
