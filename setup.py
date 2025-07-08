#!/usr/bin/env python3
"""
Setup script for Claude TDD Wrapper
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="claude-tdd",
    version="1.0.0",
    author="Claude Code TDD Team",
    description="Test-Driven Development enforcement wrapper for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/claude-tdd",
    packages=find_packages(),
    py_modules=[
        "tdd_tracker",
        "tdd_config", 
        "tdd_import_hook"
    ],
    scripts=["tdd-python"],
    install_requires=[
        "pytest>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=2.10.0",
            "black>=21.0",
            "flake8>=3.8.0",
        ],
        "yaml": [
            "pyyaml>=5.3.0",
        ]
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="tdd test-driven-development testing claude-code",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/claude-tdd/issues",
        "Source": "https://github.com/yourusername/claude-tdd",
    },
)