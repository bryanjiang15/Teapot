"""
Setup script for TeapotEngine.
"""
from setuptools import setup, find_packages

setup(
    name="teapot-engine",
    version="2.0.0",
    author="Teapot Team",
    author_email="team@teapot.com",
    description="A primitive-first, domain-agnostic game runtime",
    long_description=(
        "TeapotEngine is a pure Python game runtime. The engine has no "
        "opinion about game genre — turns, health, cards, and damage are all "
        "expressed as properties and events in AI-generated lifecycle scripts. "
        "Script generation lives in TeapotAPI; TeapotEngine only loads and "
        "executes pre-compiled scripts."
    ),
    url="https://github.com/teapot/teapot-engine",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Games/Entertainment",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
