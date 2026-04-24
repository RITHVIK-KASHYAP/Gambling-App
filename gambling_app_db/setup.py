"""
Setup file for gambling_app_db package.
"""

from setuptools import setup, find_packages

setup(
    name="gambling_app_db",
    version="1.0.0",
    description="Database module for Gambling Simulation System - Provides database connections and repository implementations",
    author="Gambling App Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mysql-connector-python>=8.0.0",
        "gambling_app_core>=1.0.0",
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
