"""
Expense data model and validation.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class Expense:
    """
    Represents a single expense transaction.
    
    Attributes:
        id: Unique identifier (None for new expenses)
        description: Short description of the expense
        amount: Expense amount as Decimal for precision
        category: Expense category
        expense_date: Date when the expense occurred
        notes: Optional additional notes
        created_at: Timestamp when the record was created
    """
    description: str
    amount: Decimal
    category: str
    expense_date: datetime
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate expense data after initialization."""
        # Convert amount to Decimal if it isn't already
        if not isinstance(self.amount, Decimal):
            self.amount = Decimal(str(self.amount))
        
        # Convert date strings to datetime if needed
        if isinstance(self.expense_date, str):
            self.expense_date = datetime.fromisoformat(self.expense_date)
        # Convert date to datetime if needed
        elif hasattr(self.expense_date, 'year') and not isinstance(self.expense_date, datetime):
            from datetime import date as date_type
            if isinstance(self.expense_date, date_type):
                self.expense_date = datetime.combine(self.expense_date, datetime.min.time())
        
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        # Validate
        errors = self.validate()
        if errors:
            raise ValueError("; ".join(errors))
    
    def validate(self) -> list[str]:
        """
        Validate expense data.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Description validation
        if not self.description or not self.description.strip():
            errors.append("Description cannot be empty")
        elif len(self.description) > 255:
            errors.append("Description must be 255 characters or less")
        
        # Amount validation
        if self.amount <= 0:
            errors.append("Amount must be greater than zero")
        elif self.amount > Decimal('999999999.99'):
            errors.append("Amount is too large")
        
        # Category validation
        if not self.category or not self.category.strip():
            errors.append("Category cannot be empty")
        
        # Date validation
        if not isinstance(self.expense_date, datetime):
            errors.append("Expense date must be a valid date")
        
        return errors
    
    def to_dict(self) -> dict:
        """
        Convert expense to dictionary format.
        
        Returns:
            Dictionary representation of the expense
        """
        return {
            'id': self.id,
            'description': self.description,
            'amount': float(self.amount),
            'category': self.category,
            'expense_date': self.expense_date.strftime('%Y-%m-%d'),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_db_row(cls, row: dict) -> 'Expense':
        """
        Create an Expense from a database row.
        
        Args:
            row: Dictionary or sqlite3.Row from database query
        
        Returns:
            Expense instance
        """
        return cls(
            id=row['id'],
            description=row['description'],
            amount=Decimal(str(row['amount'])),
            category=row['category'],
            expense_date=datetime.fromisoformat(row['expense_date']),
            notes=row['notes'] if row['notes'] else None,
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )


# Default expense categories
DEFAULT_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Education",
    "Shopping",
    "Bills & Utilities",
    "Health",
    "Entertainment",
    "Travel",
    "Personal Care",
    "Other"
]
