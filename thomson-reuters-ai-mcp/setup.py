#!/usr/bin/env python3
"""
Setup script for MCP AI Portal Agent
"""

from setuptools import setup, find_packages

setup(
    name="thomson-reuters-ai-mcp",
    version="1.0.0",
    description="MCP AI Portal Agent for Thomson Reuters AI Platform",
    author="Thomson Reuters",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "mcp>=0.5.0",
        "python-dotenv>=1.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-ai-portal=cli.terminal_interface:cli",
            "mcp-ai-server=mcp_server.server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)