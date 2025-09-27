#!/usr/bin/env python3
"""
THEBOT - Trading Analysis Platform
Setup configuration
"""

from setuptools import setup, find_packages

setup(
    name="thebot",
    version="1.0.0",
    description="Advanced Trading Analysis Platform with AI Integration",
    author="Rono40230",
    author_email="",
    url="https://github.com/Rono40230/THEBOT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "sqlalchemy>=2.0.0",
        "requests>=2.31.0",
        "aiohttp>=3.8.0",
        "plotly>=5.15.0",
        "jupyter>=1.0.0",
        "scikit-learn>=1.3.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "loguru>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
        ],
        "ai": [
            "tensorflow>=2.13.0",
            "torch>=2.0.0",
            "openai>=0.27.0",
            "anthropic>=0.3.0",
        ],
        "performance": [
            "numba>=0.57.0",
            "cython>=0.29.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "thebot=thebot.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="trading, finance, indicators, ai, backtesting, crypto, forex",
    project_urls={
        "Bug Reports": "https://github.com/Rono40230/THEBOT/issues",
        "Source": "https://github.com/Rono40230/THEBOT",
        "Documentation": "https://github.com/Rono40230/THEBOT/docs",
    },
)