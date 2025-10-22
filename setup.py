from setuptools import setup, find_packages

setup(
    name="loinc-web-semantic-chunker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "click>=8.1.7",
        "lxml>=4.9.0",
    ],
    entry_points={
        "console_scripts": [
            "loinc-chunker=loinc_chunker.cli:main",
        ],
    },
    author="LOINC Chunker Team",
    description="CLI tool to download and chunk LOINC web content",
    python_requires=">=3.8",
)
