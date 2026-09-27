"""
Tests for export service.
"""
import pytest
import csv
from pathlib import Path
from datetime import date
from decimal import Decimal

from spendwise.services.expense_service import ExpenseService
from spendwise.services.export_service import ExportService


class TestExportService:
    """Tests for the ExportService."""
    
    def test_export_to_csv(self, clean_db, tmp_path):
        """Test basic CSV export."""
        # Create test expenses
        ExpenseService.create_expense("Lunch", 12.50, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Gas", 40.00, "Travel", date(2024, 1, 16))
        
        # Export to CSV
        csv_file = tmp_path / "test_export.csv"
        count = ExportService.export_to_csv(csv_file)
        
        assert count == 2
        assert csv_file.exists()
        
        # Verify CSV content
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            assert len(rows) == 2
            # Check that both expenses are present (order may vary)
            descriptions = {row['Description'] for row in rows}
            assert 'Lunch' in descriptions
            assert 'Gas' in descriptions
            
            # Check amounts
            amounts = {row['Amount'] for row in rows}
            assert '12.50' in amounts
            assert '40.00' in amounts
    
    def test_export_adds_csv_extension(self, clean_db, tmp_path):
        """Test that .csv extension is added if missing."""
        ExpenseService.create_expense("Test", 10.00, "Food", date(2024, 1, 15))
        
        # Export without extension
        csv_file = tmp_path / "test_export"
        ExportService.export_to_csv(csv_file)
        
        # Should create file with .csv extension
        expected_file = tmp_path / "test_export.csv"
        assert expected_file.exists()
    
    def test_export_empty_expenses_raises_error(self, clean_db, tmp_path):
        """Test that exporting with no expenses raises an error."""
        csv_file = tmp_path / "test_export.csv"
        
        with pytest.raises(ValueError, match="No expenses to export"):
            ExportService.export_to_csv(csv_file)
    
    def test_export_with_date_filter(self, clean_db, tmp_path):
        """Test CSV export with date filtering."""
        # Create expenses in different months
        ExpenseService.create_expense("Jan", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Feb", 200.00, "Food", date(2024, 2, 15))
        ExpenseService.create_expense("Mar", 300.00, "Food", date(2024, 3, 15))
        
        # Export only February
        csv_file = tmp_path / "feb_export.csv"
        count = ExportService.export_to_csv(
            csv_file,
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 29)
        )
        
        assert count == 1
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 1
            assert rows[0]['Description'] == 'Feb'
    
    def test_export_with_category_filter(self, clean_db, tmp_path):
        """Test CSV export with category filtering."""
        ExpenseService.create_expense("Food 1", 50.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Travel 1", 100.00, "Travel", date(2024, 1, 16))
        ExpenseService.create_expense("Food 2", 75.00, "Food", date(2024, 1, 17))
        
        # Export only Food category
        csv_file = tmp_path / "food_export.csv"
        count = ExportService.export_to_csv(csv_file, category="Food")
        
        assert count == 2
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 2
            assert all(row['Category'] == 'Food' for row in rows)
    
    def test_export_with_notes(self, clean_db, tmp_path):
        """Test that notes are exported correctly."""
        ExpenseService.create_expense(
            "Lunch",
            12.50,
            "Food",
            date(2024, 1, 15),
            notes="Business lunch meeting"
        )
        
        csv_file = tmp_path / "notes_export.csv"
        ExportService.export_to_csv(csv_file)
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]['Notes'] == 'Business lunch meeting'
    
    def test_export_with_empty_notes(self, clean_db, tmp_path):
        """Test that empty notes are handled correctly."""
        ExpenseService.create_expense("Lunch", 12.50, "Food", date(2024, 1, 15))
        
        csv_file = tmp_path / "no_notes_export.csv"
        ExportService.export_to_csv(csv_file)
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert rows[0]['Notes'] == ''
    
    def test_export_csv_columns(self, clean_db, tmp_path):
        """Test that CSV has correct columns."""
        ExpenseService.create_expense("Test", 10.00, "Food", date(2024, 1, 15))
        
        csv_file = tmp_path / "columns_test.csv"
        ExportService.export_to_csv(csv_file)
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            columns = reader.fieldnames
            
            expected_columns = ['Date', 'Description', 'Category', 'Amount', 'Notes', 'Created At']
            assert columns == expected_columns
    
    def test_export_summary(self, clean_db):
        """Test export summary generation."""
        ExpenseService.create_expense("Item 1", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Item 2", 200.00, "Travel", date(2024, 2, 15))
        
        summary = ExportService.get_export_summary()
        
        assert summary['count'] == 2
        assert summary['total'] == Decimal('300.00')
        assert summary['earliest_date'].date() == date(2024, 1, 15)
        assert summary['latest_date'].date() == date(2024, 2, 15)
    
    def test_export_summary_empty(self, clean_db):
        """Test export summary with no expenses."""
        summary = ExportService.get_export_summary()
        
        assert summary['count'] == 0
        assert summary['total'] == 0
        assert summary['earliest_date'] is None
        assert summary['latest_date'] is None
    
    def test_export_summary_with_filters(self, clean_db):
        """Test export summary with filters."""
        ExpenseService.create_expense("Jan Food", 100.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Feb Food", 200.00, "Food", date(2024, 2, 15))
        ExpenseService.create_expense("Feb Travel", 150.00, "Travel", date(2024, 2, 20))
        
        # Get summary for February Food only
        summary = ExportService.get_export_summary(
            start_date=date(2024, 2, 1),
            end_date=date(2024, 2, 28),
            category="Food"
        )
        
        assert summary['count'] == 1
        assert summary['total'] == Decimal('200.00')
    
    def test_export_utf8_encoding(self, clean_db, tmp_path):
        """Test that CSV handles UTF-8 characters correctly."""
        ExpenseService.create_expense("Café ☕", 5.50, "Food", date(2024, 1, 15))
        
        csv_file = tmp_path / "utf8_test.csv"
        ExportService.export_to_csv(csv_file)
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Café ☕" in content
