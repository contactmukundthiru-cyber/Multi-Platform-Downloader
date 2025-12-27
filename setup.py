#!/usr/bin/env python3
"""
NeonTube - Setup Script
For building and distributing the application
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neontube",
    version="2.0.0",
    author="NeonTube Team",
    author_email="contact@neontube.app",
    description="A futuristic YouTube downloader with modern UI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neontube/neontube",
    py_modules=["youtube_downloader"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Environment :: Win32 (MS Windows)",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
    ],
    python_requires=">=3.8",
    install_requires=[
        "customtkinter>=5.2.0",
        "yt-dlp>=2023.12.30",
        "Pillow>=10.0.0",
        "packaging>=23.0",
    ],
    entry_points={
        "console_scripts": [
            "neontube=youtube_downloader:main",
        ],
        "gui_scripts": [
            "neontube-gui=youtube_downloader:main",
        ],
    },
)
