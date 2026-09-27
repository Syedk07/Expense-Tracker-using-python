"""
Service for exporting expense data.
"""
import csv
from pathlib import Path
from typing import Optional, List
from datetime import date

from spendwise.models.expense import Expense
from spendwise.services.expense_service import ExpenseService


class ExportService:
    """Service for exporting expense data to various formats."""
    
    @staticmethod
    def export_to_csv(
        file_path: str | Path,
        expenses: Optional[List[Expense]] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> int:
        """
        Export expenses to a CSV file.
        
        Args:
            file_path: Destination file path
            expenses: List of expenses to export (if None, fetches all with filters)
            start_date: Optional start date filter
            end_date: Optional end date filter
            category: Optional category filter
        
        Returns:
            Number of expenses exported
        
        Raises:
            IOError: If file cannot be written
            ValueError: If no expenses to export
        """
        # Get expenses if not provided
        if expenses is None:
            expenses = ExpenseService.get_all_expenses(
                category=category,
                start_date=start_date,
                end_date=end_date
            )
        
        if not expenses:
            raise ValueError("No expenses to export")
        
        # Ensure file path is a Path object
        file_path = Path(file_path)
        
        # Ensure .csv extension
        if file_path.suffix.lower() != '.csv':
            file_path = file_path.with_suffix('.csv')
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                # Define CSV columns
                fieldnames = [
                    'Date',
                    'Description',
                    'Category',
                    'Amount',
                    'Notes',
                    'Created At'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write expense rows
                for expense in expenses:
                    writer.writerow({
                        'Date': expense.expense_date.strftime('%Y-%m-%d'),
                        'Description': expense.description,
                        'Category': expense.category,
                        'Amount': f"{expense.amount:.2f}",
                        'Notes': expense.notes or '',
                        'Created At': expense.created_at.strftime('%Y-%m-%d %H:%M:%S') if expense.created_at else ''
                    })
            
            return len(expenses)
            
        except IOError as e:
            raise IOError(f"Failed to write CSV file: {str(e)}")
    
    @staticmethod
    def get_export_summary(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> dict:
        """
        Get summary information about what would be exported.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            category: Optional category filter
        
        Returns:
            Dictionary with export summary information
        """
        expenses = ExpenseService.get_all_expenses(
            category=category,
            start_date=start_date,
            end_date=end_date
        )
        
        total = sum(e.amount for e in expenses)
        
        # Date range
        if expenses:
            dates = [e.expense_date for e in expenses]
            earliest = min(dates)
            latest = max(dates)
        else:
            earliest = None
            latest = None
        
        return {
            'count': len(expenses),
            'total': total,
            'earliest_date': earliest,
            'latest_date': latest
        }
