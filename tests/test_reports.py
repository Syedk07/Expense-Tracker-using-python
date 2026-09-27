"""
Tests for report service.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from spendwise.services.expense_service import ExpenseService
from spendwise.services.report_service import ReportService


class TestReportService:
    """Tests for the ReportService."""
    
    def test_date_range_summary_empty(self, clean_db):
        """Test date range summary with no expenses."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        
        summary = ReportService.get_date_range_summary(start, end)
        
        assert summary['total'] == 0
        assert summary['count'] == 0
        assert summary['avg_daily'] == 0
        assert summary['categories'] == {}
        assert summary['top_category'] is None
    
    def test_date_range_summary_with_expenses(self, clean_db):
        """Test date range summary with expenses."""
        # Create test expenses
        ExpenseService.create_expense("Item 1", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Item 2", 50.00, "Food", date(2024, 1, 20))
        ExpenseService.create_expense("Item 3", 75.00, "Travel", date(2024, 1, 25))
        
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)
        
        summary = ReportService.get_date_range_summary(start, end)
        
        assert summary['total'] == Decimal('225.00')
        assert summary['count'] == 3
        assert summary['days'] == 31
        assert 'Food' in summary['categories']
        assert 'Travel' in summary['categories']
        assert summary['categories']['Food'] == Decimal('150.00')
        assert summary['categories']['Travel'] == Decimal('75.00')
        assert summary['top_category'] == 'Food'
        assert summary['top_amount'] == Decimal('150.00')
    
    def test_date_range_filters_correctly(self, clean_db):
        """Test that date range filtering works correctly."""
        # Create expenses in different months
        ExpenseService.create_expense("Jan", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Feb", 200.00, "Food", date(2024, 2, 15))
        ExpenseService.create_expense("Mar", 300.00, "Food", date(2024, 3, 15))
        
        # Query only February
        summary = ReportService.get_date_range_summary(
            date(2024, 2, 1),
            date(2024, 2, 29)
        )
        
        assert summary['total'] == Decimal('200.00')
        assert summary['count'] == 1
    
    def test_monthly_summary(self, clean_db):
        """Test monthly summary report."""
        # Create expenses
        ExpenseService.create_expense("Item 1", 50.00, "Food", date(2024, 3, 10))
        ExpenseService.create_expense("Item 2", 75.00, "Travel", date(2024, 3, 20))
        
        summary = ReportService.get_monthly_summary(2024, 3)
        
        assert summary['total'] == Decimal('125.00')
        assert summary['count'] == 2
        assert summary['start_date'] == date(2024, 3, 1)
        assert summary['end_date'] == date(2024, 3, 31)
    
    def test_monthly_summary_december(self, clean_db):
        """Test monthly summary for December (edge case)."""
        ExpenseService.create_expense("Dec item", 100.00, "Food", date(2024, 12, 25))
        
        summary = ReportService.get_monthly_summary(2024, 12)
        
        assert summary['total'] == Decimal('100.00')
        assert summary['start_date'] == date(2024, 12, 1)
        assert summary['end_date'] == date(2024, 12, 31)
    
    def test_yearly_summary(self, clean_db):
        """Test yearly summary report."""
        # Create expenses across multiple months
        ExpenseService.create_expense("Jan", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Jun", 200.00, "Travel", date(2024, 6, 15))
        ExpenseService.create_expense("Dec", 150.00, "Food", date(2024, 12, 15))
        
        summary = ReportService.get_yearly_summary(2024)
        
        assert summary['total'] == Decimal('450.00')
        assert summary['count'] == 3
        assert 'monthly_breakdown' in summary
        assert len(summary['monthly_breakdown']) == 12
    
    def test_yearly_summary_monthly_breakdown(self, clean_db):
        """Test yearly summary monthly breakdown."""
        # Create expenses
        ExpenseService.create_expense("Jan", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Feb", 200.00, "Food", date(2024, 2, 15))
        
        summary = ReportService.get_yearly_summary(2024)
        breakdown = summary['monthly_breakdown']
        
        # Check January
        jan_data = [m for m in breakdown if m['month'] == 1][0]
        assert jan_data['total'] == Decimal('100.00')
        assert jan_data['count'] == 1
        
        # Check February
        feb_data = [m for m in breakdown if m['month'] == 2][0]
        assert feb_data['total'] == Decimal('200.00')
        assert feb_data['count'] == 1
        
        # Check empty month
        mar_data = [m for m in breakdown if m['month'] == 3][0]
        assert mar_data['total'] == Decimal('0')
        assert mar_data['count'] == 0
    
    def test_category_breakdown(self, clean_db):
        """Test category breakdown."""
        ExpenseService.create_expense("Food 1", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Food 2", 50.00, "Food", date(2024, 1, 20))
        ExpenseService.create_expense("Travel", 200.00, "Travel", date(2024, 1, 25))
        
        categories = ReportService.get_category_breakdown()
        
        assert categories['Travel'] == Decimal('200.00')
        assert categories['Food'] == Decimal('150.00')
        # Should be sorted by amount (descending)
        assert list(categories.keys())[0] == 'Travel'
    
    def test_category_breakdown_with_date_range(self, clean_db):
        """Test category breakdown with date filtering."""
        ExpenseService.create_expense("Jan Food", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Feb Food", 200.00, "Food", date(2024, 2, 15))
        
        categories = ReportService.get_category_breakdown(
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 29)
        )
        
        # Should only include February expense
        assert categories['Food'] == Decimal('200.00')
        assert len(categories) == 1
    
    def test_average_daily_calculation(self, clean_db):
        """Test average daily spending calculation."""
        # Create 3 expenses totaling $300 over 10 days
        ExpenseService.create_expense("Item 1", 100.00, "Food", date(2024, 1, 1))
        ExpenseService.create_expense("Item 2", 100.00, "Food", date(2024, 1, 5))
        ExpenseService.create_expense("Item 3", 100.00, "Food", date(2024, 1, 10))
        
        summary = ReportService.get_date_range_summary(
            date(2024, 1, 1),
            date(2024, 1, 10)
        )
        
        expected_avg = Decimal('300') / 10
        assert summary['avg_daily'] == expected_avg
