"""
Setup file for gambling_app_core package.
"""

from setuptools import setup, find_packages

setup(
    name="gambling_app_core",
    version="1.0.0",
    description="Core module for Gambling Simulation System - Contains shared configuration, exceptions, and entity models",
    author="Gambling App Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
