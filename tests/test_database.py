"""
Tests for database initialization and connection management.
"""
import sqlite3
from pathlib import Path

from spendwise.database.db import initialize_database, get_connection


def test_database_initialization(temp_db):
    """Test that database is initialized with correct schema."""
    # Database should already be initialized by temp_db fixture
    assert temp_db.exists()
    
    # Check that expenses table exists
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='expenses'
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result['name'] == 'expenses'


def test_expenses_table_structure(temp_db):
    """Test that expenses table has correct columns."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(expenses)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        # Verify all required columns exist
        assert 'id' in columns
        assert 'description' in columns
        assert 'amount' in columns
        assert 'category' in columns
        assert 'expense_date' in columns
        assert 'notes' in columns
        assert 'created_at' in columns


def test_database_indexes(temp_db):
    """Test that proper indexes are created."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='expenses'
        """)
        indexes = [row['name'] for row in cursor.fetchall()]
        
        assert 'idx_expense_date' in indexes
        assert 'idx_category' in indexes
        assert 'idx_created_at' in indexes


def test_connection_context_manager(temp_db):
    """Test that connection context manager works correctly."""
    # Test successful operation
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert result[0] == 1


def test_connection_rollback_on_error(clean_db):
    """Test that connection rolls back on errors."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            # Insert valid data
            cursor.execute("""
                INSERT INTO expenses (description, amount, category, expense_date)
                VALUES (?, ?, ?, ?)
            """, ("Test", 10.0, "Food", "2024-01-01"))
            
            # Cause an error
            cursor.execute("INVALID SQL")
    except sqlite3.OperationalError:
        pass
    
    # Verify the insert was rolled back
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM expenses")
        count = cursor.fetchone()['count']
        assert count == 0
