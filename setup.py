from setuptools import setup, find_packages

setup(
    name="mcp-tools-loader",
    version="0.1.0",
    description="A tool loader for MCP tools with caching and filtering",
    author="Your Name",
    author_email="your-email@example.com",
    url="https://github.com/YOUR_USERNAME/mcp-tools-loader",
    packages=find_packages(),
    install_requires=[
        "crewai-tools",  # Replace with actual dependency list
    ],
    entry_points={
        "console_scripts": [
            "mcp-tools-loader = cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
