"""
Database initialization and connection management.
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

from spendwise.utils.paths import get_database_path


def initialize_database() -> None:
    """
    Initialize the SQLite database with required tables and indexes.
    
    Creates the expenses table if it doesn't exist.
    Safe to call multiple times - will not overwrite existing data.
    """
    db_path = get_database_path()
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Create expenses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                expense_date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_expense_date 
            ON expenses(expense_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON expenses(category)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON expenses(created_at)
        """)
        
        conn.commit()


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    
    Automatically handles connection opening, committing, and closing.
    Rolls back on exceptions.
    
    Usage:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses")
    """
    db_path = get_database_path()
    conn = sqlite3.Connection(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
