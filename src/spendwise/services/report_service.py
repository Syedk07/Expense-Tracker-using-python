"""
Service for generating expense reports and insights.
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, Optional

from spendwise.services.expense_service import ExpenseService


class ReportService:
    """Service for generating expense reports."""
    
    @staticmethod
    def get_date_range_summary(
        start_date: date,
        end_date: date
    ) -> Dict:
        """
        Get expense summary for a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
        
        Returns:
            Dictionary with summary data
        """
        expenses = ExpenseService.get_all_expenses(
            start_date=start_date,
            end_date=end_date
        )
        
        total = sum(e.amount for e in expenses)
        count = len(expenses)
        
        # Calculate average daily spending
        days = (end_date - start_date).days + 1
        avg_daily = total / days if days > 0 else Decimal('0')
        
        # Category breakdown
        categories = {}
        for expense in expenses:
            cat = expense.category
            categories[cat] = categories.get(cat, Decimal('0')) + expense.amount
        
        # Sort categories by amount
        categories = dict(sorted(
            categories.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Top category
        top_category = None
        top_amount = Decimal('0')
        if categories:
            top_category = list(categories.keys())[0]
            top_amount = categories[top_category]
        
        return {
            'total': total,
            'count': count,
            'avg_daily': avg_daily,
            'categories': categories,
            'top_category': top_category,
            'top_amount': top_amount,
            'start_date': start_date,
            'end_date': end_date,
            'days': days
        }
    
    @staticmethod
    def get_monthly_summary(year: int, month: int) -> Dict:
        """
        Get expense summary for a specific month.
        
        Args:
            year: Year
            month: Month (1-12)
        
        Returns:
            Dictionary with monthly summary
        """
        # Calculate first and last day of month
        first_day = date(year, month, 1)
        
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        return ReportService.get_date_range_summary(first_day, last_day)
    
    @staticmethod
    def get_yearly_summary(year: int) -> Dict:
        """
        Get expense summary for a specific year.
        
        Args:
            year: Year
        
        Returns:
            Dictionary with yearly summary
        """
        first_day = date(year, 1, 1)
        last_day = date(year, 12, 31)
        
        summary = ReportService.get_date_range_summary(first_day, last_day)
        
        # Add monthly breakdown
        monthly_totals = []
        for month in range(1, 13):
            month_data = ReportService.get_monthly_summary(year, month)
            monthly_totals.append({
                'month': month,
                'total': month_data['total'],
                'count': month_data['count']
            })
        
        summary['monthly_breakdown'] = monthly_totals
        
        return summary
    
    @staticmethod
    def get_category_breakdown(
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Decimal]:
        """
        Get spending breakdown by category.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Dictionary mapping category names to total amounts
        """
        expenses = ExpenseService.get_all_expenses(
            start_date=start_date,
            end_date=end_date
        )
        
        categories = {}
        for expense in expenses:
            cat = expense.category
            categories[cat] = categories.get(cat, Decimal('0')) + expense.amount
        
        return dict(sorted(
            categories.items(),
            key=lambda x: x[1],
            reverse=True
        ))
    
    @staticmethod
    def get_spending_trend(months: int = 6) -> list[Dict]:
        """
        Get spending trend for the last N months.
        
        Args:
            months: Number of months to include
        
        Returns:
            List of monthly data dictionaries
        """
        today = date.today()
        trend_data = []
        
        for i in range(months - 1, -1, -1):
            # Calculate target month
            target_date = today - timedelta(days=i * 30)
            year = target_date.year
            month = target_date.month
            
            # Get month summary
            summary = ReportService.get_monthly_summary(year, month)
            
            trend_data.append({
                'year': year,
                'month': month,
                'month_name': date(year, month, 1).strftime('%B'),
                'total': summary['total'],
                'count': summary['count']
            })
        
        return trend_data
