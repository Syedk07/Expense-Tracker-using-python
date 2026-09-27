"""
Pytest configuration and fixtures.
"""
import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
import sqlite3
import tempfile
from unittest.mock import patch

from spendwise.database.db import initialize_database, get_connection


@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    """
    Create a temporary database for testing.
    
    This fixture ensures tests don't modify the user's real database.
    """
    test_db_path = tmp_path / "test_spendwise.db"
    
    # Mock the database path
    monkeypatch.setattr(
        "spendwise.database.db.get_database_path",
        lambda: test_db_path
    )
    monkeypatch.setattr(
        "spendwise.services.expense_service.get_connection",
        get_connection
    )
    
    # Initialize the test database
    initialize_database()
    
    yield test_db_path
    
    # Cleanup happens automatically with tmp_path


@pytest.fixture
def clean_db(temp_db):
    """
    Provide a clean database for each test.
    
    Clears all data between tests.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses")
        conn.commit()
    
    yield temp_db
