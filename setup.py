"""Setup configuration for SpendWise."""
from setuptools import setup, find_packages

setup(
    name="spendwise",
    version="1.0.0",
    description="A personal expense tracking desktop application",
    author="Syedk07",
    url="https://github.com/Syedk07/Expense-Tracker-using-python",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "platformdirs>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "spendwise=spendwise.app:run_app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
    ],
)
