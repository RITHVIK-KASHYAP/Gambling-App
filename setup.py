"""
Master setup file for Gambling Simulation System.
Installs all modules in the correct dependency order.
"""

from setuptools import setup, find_packages

setup(
    name="gambling_simulation_system",
    version="1.0.0",
    description="Complete Gambling Simulation System with modular architecture",
    author="Gambling App Team",
    url="https://github.com/yourusername/gambling_simulation_system",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "mysql-connector-python>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gambling-app=main:main",
            "init-db=init_database:setup_database",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Entertainment Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.14",
    ],
    long_description="A comprehensive, production-quality gambling simulation system built with Python using object-oriented design and clean architecture principles. Features modular structure for independent deployment.",
    keywords="gambling simulation betting system Python OOP",
)
