"""
Convenience script to run SpendWise without installation.

Usage: python run.py
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Run the application
from spendwise.app import run_app

if __name__ == "__main__":
    run_app()
