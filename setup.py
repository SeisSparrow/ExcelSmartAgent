"""
Setup script for Excel Smart Agent
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="excel-smart-agent",
    version="1.0.0",
    author="Excel Smart Agent Team",
    description="An AI-powered intelligent Excel data analysis system with natural language and voice support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ExcelSmartAgent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial :: Spreadsheet",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "websockets>=12.0",
        "pandas>=2.1.4",
        "openpyxl>=3.1.2",
        "openai>=1.10.0",
        "anthropic>=0.18.0",
        "langchain>=0.1.4",
        "matplotlib>=3.8.2",
        "seaborn>=0.13.1",
        "plotly>=5.18.0",
        "speechrecognition>=3.10.1",
        "pydantic>=2.5.3",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "excel-agent=backend.main:main",
        ],
    },
)

