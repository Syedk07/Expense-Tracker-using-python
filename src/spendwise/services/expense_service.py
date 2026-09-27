"""
Business logic for expense management.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from spendwise.database.db import get_connection
from spendwise.models.expense import Expense


class ExpenseService:
    """Service for managing expense operations."""
    
    @staticmethod
    def create_expense(
        description: str,
        amount: Decimal | float,
        category: str,
        expense_date: datetime | date,
        notes: Optional[str] = None
    ) -> Expense:
        """
        Create a new expense.
        
        Args:
            description: Expense description
            amount: Expense amount
            category: Expense category
            expense_date: Date of expense
            notes: Optional notes
        
        Returns:
            Created Expense with ID
        
        Raises:
            ValueError: If validation fails
        """
        # Convert date to datetime if needed
        if isinstance(expense_date, date) and not isinstance(expense_date, datetime):
            expense_date = datetime.combine(expense_date, datetime.min.time())
        
        # Create and validate expense
        expense = Expense(
            description=description.strip(),
            amount=amount,
            category=category,
            expense_date=expense_date,
            notes=notes.strip() if notes else None
        )
        
        # Insert into database
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (description, amount, category, expense_date, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                expense.description,
                float(expense.amount),
                expense.category,
                expense.expense_date.strftime('%Y-%m-%d'),
                expense.notes
            ))
            
            expense.id = cursor.lastrowid
            
            # Get the created_at timestamp
            cursor.execute("SELECT created_at FROM expenses WHERE id = ?", (expense.id,))
            row = cursor.fetchone()
            expense.created_at = datetime.fromisoformat(row['created_at'])
            
            conn.commit()
        
        return expense
    
    @staticmethod
    def get_expense(expense_id: int) -> Optional[Expense]:
        """
        Get an expense by ID.
        
        Args:
            expense_id: The expense ID
        
        Returns:
            Expense if found, None otherwise
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            row = cursor.fetchone()
            
            if row:
                return Expense.from_db_row(row)
            return None
    
    @staticmethod
    def get_all_expenses(
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        search_term: Optional[str] = None
    ) -> list[Expense]:
        """
        Get all expenses with optional filtering.
        
        Args:
            category: Filter by category
            start_date: Filter by start date (inclusive)
            end_date: Filter by end date (inclusive)
            search_term: Search in description
        
        Returns:
            List of expenses matching the filters
        """
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND expense_date >= ?"
            params.append(start_date.strftime('%Y-%m-%d'))
        
        if end_date:
            query += " AND expense_date <= ?"
            params.append(end_date.strftime('%Y-%m-%d'))
        
        if search_term:
            query += " AND description LIKE ?"
            params.append(f"%{search_term}%")
        
        query += " ORDER BY expense_date DESC, created_at DESC"
        
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [Expense.from_db_row(row) for row in rows]
    
    @staticmethod
    def update_expense(
        expense_id: int,
        description: Optional[str] = None,
        amount: Optional[Decimal | float] = None,
        category: Optional[str] = None,
        expense_date: Optional[datetime | date] = None,
        notes: Optional[str] = None
    ) -> Optional[Expense]:
        """
        Update an existing expense.
        
        Args:
            expense_id: The expense ID to update
            description: New description (if provided)
            amount: New amount (if provided)
            category: New category (if provided)
            expense_date: New date (if provided)
            notes: New notes (if provided)
        
        Returns:
            Updated expense if found, None otherwise
        
        Raises:
            ValueError: If validation fails
        """
        # Get existing expense
        existing = ExpenseService.get_expense(expense_id)
        if not existing:
            return None
        
        # Update fields
        if description is not None:
            existing.description = description.strip()
        if amount is not None:
            existing.amount = Decimal(str(amount))
        if category is not None:
            existing.category = category
        if expense_date is not None:
            if isinstance(expense_date, date) and not isinstance(expense_date, datetime):
                expense_date = datetime.combine(expense_date, datetime.min.time())
            existing.expense_date = expense_date
        if notes is not None:
            existing.notes = notes.strip() if notes else None
        
        # Validate
        errors = existing.validate()
        if errors:
            raise ValueError("; ".join(errors))
        
        # Update in database
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE expenses
                SET description = ?, amount = ?, category = ?, expense_date = ?, notes = ?
                WHERE id = ?
            """, (
                existing.description,
                float(existing.amount),
                existing.category,
                existing.expense_date.strftime('%Y-%m-%d'),
                existing.notes,
                expense_id
            ))
            conn.commit()
        
        return existing
    
    @staticmethod
    def delete_expense(expense_id: int) -> bool:
        """
        Delete an expense.
        
        Args:
            expense_id: The expense ID to delete
        
        Returns:
            True if deleted, False if not found
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    @staticmethod
    def get_expense_count() -> int:
        """
        Get total number of expenses.
        
        Returns:
            Total expense count
        """
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM expenses")
            row = cursor.fetchone()
            return row['count']
