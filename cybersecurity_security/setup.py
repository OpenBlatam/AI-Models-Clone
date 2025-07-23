"""
Setup script for Cybersecurity Security Toolkit
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Cybersecurity Security Toolkit"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="cybersecurity-security",
    version="1.0.0",
    author="Cybersecurity Team",
    author_email="security@example.com",
    description="A comprehensive Python cybersecurity toolkit with modular architecture",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/example/cybersecurity-security",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "test": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "httpx>=0.25.2",
        ],
    },
    entry_points={
        "console_scripts": [
            "cybersecurity-security=cybersecurity_security.examples.usage_examples:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="cybersecurity security validation encryption network scanning logging",
    project_urls={
        "Bug Reports": "https://github.com/example/cybersecurity-security/issues",
        "Source": "https://github.com/example/cybersecurity-security",
        "Documentation": "https://github.com/example/cybersecurity-security/blob/main/README.md",
    },
) 