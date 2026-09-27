# Contributing to SpendWise

Thank you for your interest in contributing to SpendWise! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project aims to be welcoming and inclusive. Please be respectful and considerate in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or newer
- Git
- A code editor (VS Code, PyCharm, etc.)
- Basic knowledge of Python and Tkinter

### Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/SpendWise.git
   cd SpendWise
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   # Activate it (OS-specific)
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Making Changes

1. **Create a branch** for your feature or bug fix:
   ```bash
   git checkout -b feature/my-new-feature
   # or
   git checkout -b fix/bug-description
   ```

2. **Make your changes** following the code style guidelines

3. **Write or update tests** for your changes

4. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

7. **Create a Pull Request** on GitHub

### Branch Naming Convention

- **Features:** `feature/description`
- **Bug fixes:** `fix/description`
- **Documentation:** `docs/description`
- **Refactoring:** `refactor/description`

## Code Style

### General Guidelines

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Keep functions focused and concise (ideally under 50 lines)
- Add docstrings to all functions, classes, and modules
- Use type hints where appropriate

### Python Style Examples

```python
def calculate_monthly_total(year: int, month: int) -> Decimal:
    """
    Calculate total expenses for a specific month.
    
    Args:
        year: Four-digit year
        month: Month number (1-12)
    
    Returns:
        Total expense amount as Decimal
    """
    expenses = get_expenses_for_month(year, month)
    return sum(e.amount for e in expenses)
```

### Import Organization

Group imports in this order:
1. Standard library imports
2. Related third-party imports
3. Local application imports

```python
# Standard library
from datetime import datetime
from decimal import Decimal

# Third-party
from platformdirs import user_data_dir

# Local
from spendwise.models.expense import Expense
```

### UI Guidelines

- Use the constants defined in `ui/styles.py` for colors and fonts
- Maintain consistent spacing using `SPACING` constants
- Follow the existing layout patterns for new views
- Test UI changes on different screen sizes

## Testing

### Writing Tests

- Write tests for all new features
- Ensure existing tests pass before submitting PR
- Aim for high test coverage (>80%)
- Use descriptive test names

### Test Structure

```python
def test_feature_description(clean_db):
    """Test that feature works correctly."""
    # Arrange
    test_data = create_test_data()
    
    # Act
    result = function_under_test(test_data)
    
    # Assert
    assert result == expected_value
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_expenses.py

# Run with coverage
pytest --cov=spendwise --cov-report=html

# Run verbose
pytest -v
```

### Test Guidelines

- Use the `clean_db` fixture for database tests
- Use temporary directories (`tmp_path`) for file operations
- Mock external dependencies when appropriate
- Test both success and failure cases
- Test edge cases and boundary conditions

## Pull Request Process

### Before Submitting

1. ✅ All tests pass
2. ✅ Code follows style guidelines
3. ✅ New tests added for new features
4. ✅ Documentation updated if needed
5. ✅ No merge conflicts with main branch

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe the tests you ran

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex sections
- [ ] Updated documentation
- [ ] Added tests
- [ ] All tests pass
```

### Review Process

1. A maintainer will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged

## Reporting Issues

### Bug Reports

When reporting bugs, include:
- **Description:** Clear description of the bug
- **Steps to Reproduce:** Detailed steps to reproduce the issue
- **Expected Behavior:** What should happen
- **Actual Behavior:** What actually happens
- **Environment:**
  - OS and version
  - Python version
  - SpendWise version
- **Screenshots:** If applicable
- **Error Messages:** Full error text if any

### Feature Requests

When suggesting features, include:
- **Description:** Clear description of the feature
- **Use Case:** Why is this feature needed?
- **Proposed Solution:** How should it work?
- **Alternatives:** Alternative approaches considered

### Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed

## Project-Specific Guidelines

### Database Changes

- Always create database migrations
- Test with fresh database
- Test with existing data
- Document schema changes

### UI Changes

- Test on different operating systems if possible
- Ensure consistent styling with existing UI
- Test with different window sizes
- Check color contrast for accessibility

### Adding Dependencies

- Justify the need for new dependencies
- Prefer standard library when possible
- Update `requirements.txt` and `pyproject.toml`
- Document usage in README if significant

## Communication

- **Issues:** GitHub Issues for bugs and features
- **Discussions:** GitHub Discussions for questions
- **Code:** Pull Requests with clear descriptions

## Recognition

Contributors will be acknowledged in the project. Significant contributions may be highlighted in release notes.

## Questions?

If you have questions about contributing:
1. Check existing issues and discussions
2. Review this document thoroughly
3. Open a new discussion on GitHub

Thank you for contributing to SpendWise! 🎉
