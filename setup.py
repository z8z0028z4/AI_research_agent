"""
AI Research Agent Setup
======================

安裝配置文件，用於正確的包管理和模組導入
"""

from setuptools import setup, find_packages
import os

# 讀取 README 文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "AI Research Agent - 基於檢索增強生成的AI研究助手"

# 讀取 requirements.txt
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="ai-research-agent",
    version="1.0.0",
    description="基於檢索增強生成的AI研究助手",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="AI Research Team",
    author_email="ai-research@example.com",
    url="https://github.com/ai-research/ai-research-agent",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="ai research assistant rag llm",
    project_urls={
        "Bug Reports": "https://github.com/ai-research/ai-research-agent/issues",
        "Source": "https://github.com/ai-research/ai-research-agent",
        "Documentation": "https://github.com/ai-research/ai-research-agent/wiki",
    },
    entry_points={
        "console_scripts": [
            "ai-research-agent=app.main:main",
        ],
    },
)
