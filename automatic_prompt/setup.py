"""
自动提示词优化系统 (Automatic Prompt Optimizer)
基于论文实现的提示词优化框架

安装方式:
    pip install -e .                    # 开发模式安装
    pip install -e ".[dev]"            # 包含开发工具
    pip install -e ".[all]"            # 安装所有依赖
"""
from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, encoding="utf-8") as f:
            return f.read()
    return ""

# 读取 requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if line and not line.startswith("#"):
                    requirements.append(line)
    return requirements

setup(
    name="automatic-prompt-optimizer",
    version="0.1.0",
    author="Lu Ming",
    author_email="your.email@example.com",
    description="Automatic Prompt Optimization (APO) - 提示词自动优化系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/automatic-prompt-optimizer",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/automatic-prompt-optimizer/issues",
        "Documentation": "https://github.com/yourusername/automatic-prompt-optimizer/blob/main/README.md",
        "Source Code": "https://github.com/yourusername/automatic-prompt-optimizer",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "dashscope>=1.14.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.3.0"],
        "local": ["transformers>=4.30.0", "torch>=2.0.0"],
        "metrics": ["nltk>=3.8", "rouge-score>=0.1.2", "bert-score>=0.3.13"],
    },
    entry_points={
        "console_scripts": [
            "apo-optimize=main:main",  # 命令行工具（如果需要）
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
