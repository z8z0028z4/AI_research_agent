from setuptools import setup, find_packages

with open("research_agent/README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("research_agent/requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-research-assistant",
    version="2.0.0",
    author="AI Research Assistant Team",
    author_email="your.email@example.com",
    description="A comprehensive AI-powered research assistant for materials science and chemistry",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AI-research-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-research-assistant=research_agent.app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "research_agent": ["*.md", "*.txt", "*.bat"],
    },
    keywords="ai research assistant materials science chemistry rag vector database",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/AI-research-agent/issues",
        "Source": "https://github.com/yourusername/AI-research-agent",
        "Documentation": "https://github.com/yourusername/AI-research-agent/blob/main/research_agent/app/ARCHITECTURE_OVERVIEW.md",
    },
) 