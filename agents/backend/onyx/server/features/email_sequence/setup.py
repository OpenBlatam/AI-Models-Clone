#!/usr/bin/env python3
"""
Setup script for Email Sequence AI System
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Email Sequence AI System with Advanced Optimization and Profiling"

# Read requirements
def read_requirements(filename):
    requirements_path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="email-sequence-ai",
    version="1.0.0",
    author="Blatam Academy",
    author_email="contact@blatamacademy.com",
    description="Advanced Email Sequence AI System with Optimization and Profiling",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/blatamacademy/email-sequence-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Email",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": read_requirements("requirements-dev.txt"),
        "minimal": read_requirements("requirements-minimal.txt"),
        "gpu": [
            "torch>=2.0.0+cu118",
            "torchvision>=0.15.0+cu118",
            "torchaudio>=2.0.0+cu118",
        ],
        "distributed": [
            "torch>=2.0.0",
            "horovod>=0.28.0",
        ],
        "cloud": [
            "boto3>=1.28.0",
            "google-cloud-storage>=2.10.0",
            "azure-storage-blob>=12.17.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
            "grafana-api>=1.0.3",
            "sentry-sdk>=1.28.0",
        ],
        "profiling": [
            "memory-profiler>=0.61.0",
            "line-profiler>=4.1.0",
            "py-spy>=0.3.0",
            "pyinstrument>=4.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "email-sequence-ai=email_sequence.cli:main",
            "email-sequence-train=email_sequence.training:main",
            "email-sequence-demo=email_sequence.demo:main",
            "email-sequence-profile=email_sequence.profiling:main",
        ],
    },
    include_package_data=True,
    package_data={
        "email_sequence": [
            "configs/*.yaml",
            "configs/*.json",
            "models/*.pkl",
            "data/*.csv",
            "data/*.json",
        ],
    },
    keywords=[
        "email",
        "sequence",
        "ai",
        "machine-learning",
        "nlp",
        "optimization",
        "profiling",
        "gradio",
        "pytorch",
        "transformers",
    ],
    project_urls={
        "Bug Reports": "https://github.com/blatamacademy/email-sequence-ai/issues",
        "Source": "https://github.com/blatamacademy/email-sequence-ai",
        "Documentation": "https://email-sequence-ai.readthedocs.io/",
    },
    zip_safe=False,
) 