"""
Setup script for TruthGPT Specifications
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
README_FILE = Path(__file__).parent / "README.md"
readme_text = README_FILE.read_text(encoding="utf-8") if README_FILE.exists() else ""

# Read requirements
REQUIREMENTS_FILE = Path(__file__).parent / "requirements.txt"
requirements = []
if REQUIREMENTS_FILE.exists():
    requirements = REQUIREMENTS_FILE.read_text(encoding="utf-8").strip().split("\n")

setup(
    name="truthgpt-spec",
    version="1.0.0",
    author="TruthGPT Team",
    author_email="team@truthgpt.ai",
    description="TruthGPT Optimization Core Specifications",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    url="https://github.com/truthgpt/truthgpt-spec",
    packages=find_packages(exclude=["tests", "docs", "examples"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.22.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "mkdocs>=1.5.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings>=0.22.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)



