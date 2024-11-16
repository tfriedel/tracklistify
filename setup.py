"""
Setup configuration for Tracklistify package.
"""

from setuptools import setup, find_packages

setup(
    name="tracklistify",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "acrcloud>=1.0.0",
        "python-dotenv>=1.0.0",
        "yt-dlp>=2023.10.13",
    ],
    entry_points={
        "console_scripts": [
            "tracklistify=tracklistify.__main__:main",
        ],
    },
    author="Tracklistify Team",
    description="A tool for identifying tracks in DJ mixes and audio files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tracklistify",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)
