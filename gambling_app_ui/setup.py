"""
Setup file for gambling_app_ui package.
"""

from setuptools import setup, find_packages

setup(
    name="gambling_app_ui",
    version="1.0.0",
    description="User Interface module for Gambling Simulation System - Provides console-based UI",
    author="Gambling App Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gambling_app_core>=1.0.0",
        "gambling_app_db>=1.0.0",
        "gambling_app_services>=1.0.0",
        "gambling_app_utils>=1.0.0",
    ],
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
