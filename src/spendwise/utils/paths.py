"""
Path utilities for cross-platform file and directory handling.
"""
from pathlib import Path
from platformdirs import user_data_dir

from spendwise import __app_name__


def get_app_data_dir() -> Path:
    """
    Get the application data directory for storing user data.
    
    Returns a platform-appropriate directory:
    - Windows: C:/Users/<User>/AppData/Local/SpendWise
    - Linux: ~/.local/share/SpendWise
    - macOS: ~/Library/Application Support/SpendWise
    
    Creates the directory if it doesn't exist.
    """
    app_dir = Path(user_data_dir(__app_name__, appauthor=False))
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


def get_database_path() -> Path:
    """
    Get the path to the SQLite database file.
    
    Returns the full path to spendwise.db in the application data directory.
    """
    return get_app_data_dir() / "spendwise.db"
