"""
Tests for expense model and service operations.
"""
import pytest
from datetime import datetime, date
from decimal import Decimal

from spendwise.models.expense import Expense, DEFAULT_CATEGORIES
from spendwise.services.expense_service import ExpenseService


class TestExpenseModel:
    """Tests for the Expense model."""
    
    def test_create_valid_expense(self):
        """Test creating a valid expense."""
        expense = Expense(
            description="Grocery shopping",
            amount=Decimal("50.00"),
            category="Food & Dining",
            expense_date=datetime(2024, 1, 15)
        )
        
        assert expense.description == "Grocery shopping"
        assert expense.amount == Decimal("50.00")
        assert expense.category == "Food & Dining"
        assert expense.expense_date == datetime(2024, 1, 15)
    
    def test_expense_with_notes(self):
        """Test creating an expense with notes."""
        expense = Expense(
            description="Bus ticket",
            amount=Decimal("2.50"),
            category="Transportation",
            expense_date=datetime(2024, 1, 15),
            notes="Monthly bus pass"
        )
        
        assert expense.notes == "Monthly bus pass"
    
    def test_empty_description_raises_error(self):
        """Test that empty description raises validation error."""
        with pytest.raises(ValueError, match="Description cannot be empty"):
            Expense(
                description="",
                amount=Decimal("50.00"),
                category="Food",
                expense_date=datetime(2024, 1, 15)
            )
    
    def test_zero_amount_raises_error(self):
        """Test that zero amount raises validation error."""
        with pytest.raises(ValueError, match="Amount must be greater than zero"):
            Expense(
                description="Test",
                amount=Decimal("0"),
                category="Food",
                expense_date=datetime(2024, 1, 15)
            )
    
    def test_negative_amount_raises_error(self):
        """Test that negative amount raises validation error."""
        with pytest.raises(ValueError, match="Amount must be greater than zero"):
            Expense(
                description="Test",
                amount=Decimal("-10.00"),
                category="Food",
                expense_date=datetime(2024, 1, 15)
            )
    
    def test_empty_category_raises_error(self):
        """Test that empty category raises validation error."""
        with pytest.raises(ValueError, match="Category cannot be empty"):
            Expense(
                description="Test",
                amount=Decimal("50.00"),
                category="",
                expense_date=datetime(2024, 1, 15)
            )
    
    def test_expense_to_dict(self):
        """Test converting expense to dictionary."""
        expense = Expense(
            id=1,
            description="Test",
            amount=Decimal("25.50"),
            category="Food",
            expense_date=datetime(2024, 1, 15),
            notes="Test note",
            created_at=datetime(2024, 1, 15, 10, 30)
        )
        
        result = expense.to_dict()
        
        assert result['id'] == 1
        assert result['description'] == "Test"
        assert result['amount'] == 25.50
        assert result['category'] == "Food"
        assert result['expense_date'] == "2024-01-15"
        assert result['notes'] == "Test note"
    
    def test_default_categories_exist(self):
        """Test that default categories are defined."""
        assert len(DEFAULT_CATEGORIES) > 0
        assert "Food & Dining" in DEFAULT_CATEGORIES
        assert "Transportation" in DEFAULT_CATEGORIES
        assert "Other" in DEFAULT_CATEGORIES


class TestExpenseService:
    """Tests for the ExpenseService."""
    
    def test_create_expense(self, clean_db):
        """Test creating a new expense."""
        expense = ExpenseService.create_expense(
            description="Coffee",
            amount=4.50,
            category="Food & Dining",
            expense_date=date(2024, 1, 15)
        )
        
        assert expense.id is not None
        assert expense.description == "Coffee"
        assert expense.amount == Decimal("4.50")
        assert expense.created_at is not None
    
    def test_create_expense_with_notes(self, clean_db):
        """Test creating an expense with notes."""
        expense = ExpenseService.create_expense(
            description="Taxi",
            amount=15.00,
            category="Transportation",
            expense_date=date(2024, 1, 15),
            notes="Airport trip"
        )
        
        assert expense.notes == "Airport trip"
    
    def test_create_expense_strips_whitespace(self, clean_db):
        """Test that whitespace is stripped from inputs."""
        expense = ExpenseService.create_expense(
            description="  Test  ",
            amount=10.00,
            category="Food",
            expense_date=date(2024, 1, 15),
            notes="  Note  "
        )
        
        assert expense.description == "Test"
        assert expense.notes == "Note"
    
    def test_get_expense(self, clean_db):
        """Test retrieving an expense by ID."""
        created = ExpenseService.create_expense(
            description="Lunch",
            amount=12.00,
            category="Food",
            expense_date=date(2024, 1, 15)
        )
        
        retrieved = ExpenseService.get_expense(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.description == "Lunch"
    
    def test_get_nonexistent_expense(self, clean_db):
        """Test retrieving a non-existent expense returns None."""
        result = ExpenseService.get_expense(99999)
        assert result is None
    
    def test_get_all_expenses(self, clean_db):
        """Test retrieving all expenses."""
        ExpenseService.create_expense("Item 1", 10.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Item 2", 20.00, "Travel", date(2024, 1, 16))
        ExpenseService.create_expense("Item 3", 30.00, "Food", date(2024, 1, 17))
        
        expenses = ExpenseService.get_all_expenses()
        
        assert len(expenses) == 3
    
    def test_get_expenses_by_category(self, clean_db):
        """Test filtering expenses by category."""
        ExpenseService.create_expense("Food 1", 10.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Travel 1", 20.00, "Travel", date(2024, 1, 16))
        ExpenseService.create_expense("Food 2", 30.00, "Food", date(2024, 1, 17))
        
        food_expenses = ExpenseService.get_all_expenses(category="Food")
        
        assert len(food_expenses) == 2
        assert all(e.category == "Food" for e in food_expenses)
    
    def test_get_expenses_by_date_range(self, clean_db):
        """Test filtering expenses by date range."""
        ExpenseService.create_expense("Item 1", 10.00, "Food", date(2024, 1, 10))
        ExpenseService.create_expense("Item 2", 20.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Item 3", 30.00, "Food", date(2024, 1, 20))
        
        expenses = ExpenseService.get_all_expenses(
            start_date=date(2024, 1, 12),
            end_date=date(2024, 1, 18)
        )
        
        assert len(expenses) == 1
        assert expenses[0].description == "Item 2"
    
    def test_search_expenses(self, clean_db):
        """Test searching expenses by description."""
        ExpenseService.create_expense("Coffee shop", 5.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Grocery shopping", 50.00, "Food", date(2024, 1, 16))
        ExpenseService.create_expense("Gas station", 40.00, "Travel", date(2024, 1, 17))
        
        results = ExpenseService.get_all_expenses(search_term="shop")
        
        assert len(results) == 2
        assert any("Coffee" in e.description for e in results)
        assert any("Grocery" in e.description for e in results)
    
    def test_update_expense(self, clean_db):
        """Test updating an expense."""
        expense = ExpenseService.create_expense(
            description="Original",
            amount=10.00,
            category="Food",
            expense_date=date(2024, 1, 15)
        )
        
        updated = ExpenseService.update_expense(
            expense_id=expense.id,
            description="Updated",
            amount=20.00
        )
        
        assert updated is not None
        assert updated.description == "Updated"
        assert updated.amount == Decimal("20.00")
        assert updated.category == "Food"  # Unchanged
    
    def test_update_nonexistent_expense(self, clean_db):
        """Test updating a non-existent expense returns None."""
        result = ExpenseService.update_expense(
            expense_id=99999,
            description="Test"
        )
        assert result is None
    
    def test_delete_expense(self, clean_db):
        """Test deleting an expense."""
        expense = ExpenseService.create_expense(
            description="To delete",
            amount=10.00,
            category="Food",
            expense_date=date(2024, 1, 15)
        )
        
        deleted = ExpenseService.delete_expense(expense.id)
        assert deleted is True
        
        # Verify it's gone
        result = ExpenseService.get_expense(expense.id)
        assert result is None
    
    def test_delete_nonexistent_expense(self, clean_db):
        """Test deleting a non-existent expense returns False."""
        result = ExpenseService.delete_expense(99999)
        assert result is False
    
    def test_get_expense_count(self, clean_db):
        """Test getting total expense count."""
        assert ExpenseService.get_expense_count() == 0
        
        ExpenseService.create_expense("Item 1", 10.00, "Food", date(2024, 1, 15))
        ExpenseService.create_expense("Item 2", 20.00, "Travel", date(2024, 1, 16))
        
        assert ExpenseService.get_expense_count() == 2
    
    def test_invalid_expense_raises_error(self, clean_db):
        """Test that invalid expense data raises validation error."""
        with pytest.raises(ValueError):
            ExpenseService.create_expense(
                description="",
                amount=10.00,
                category="Food",
                expense_date=date(2024, 1, 15)
            )
