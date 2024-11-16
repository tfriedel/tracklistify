"""
Setup configuration for Tracklistify package.
"""

from setuptools import setup, find_packages

setup(
    name="tracklistify",
    version="0.3.6",
    packages=find_packages(),
    install_requires=[
        "pydub>=0.25.1",
        "pyacrcloud>=1.0.7",
        "yt-dlp>=2023.7.6",
        "requests>=2.31.0",
        "configparser>=5.3.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "tracklistify=tracklistify.__main__:main",
        ],
    },
    author="Tracklistify Team",
    description="Automatically identify and catalog tracks from DJ mixes and audio streams",
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
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
    ],
    python_requires=">=3.7",
)
