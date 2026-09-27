# SpendWise - Personal Expense Tracker

A lightweight, offline-first desktop application for tracking personal expenses built with Python and Tkinter.

<img src="docs/screenshots/placeholder.png" alt="SpendWise Screenshot" width="800">

## Features

- 📊 **Dashboard** - View spending summaries with today, monthly, and yearly totals
- 💰 **Expense Management** - Add, edit, delete, and search expenses
- 📁 **Categories** - Organize expenses into 10 predefined categories
- 📈 **Reports & Insights** - Generate monthly, yearly, and custom date range reports
- 📤 **CSV Export** - Export your data to CSV for use in spreadsheet applications
- 💾 **Local Storage** - All data stored locally in SQLite (no internet required)
- 🖥️ **Cross-Platform** - Works on Windows, Linux, and macOS
- 🎨 **Modern UI** - Clean, professional interface with intuitive navigation

## Screenshots

<table>
<tr>
<td><img src="docs/screenshots/placeholder.png" width="400"></td>
<td><img src="docs/screenshots/placeholder.png" width="400"></td>
</tr>
<tr>
<td align="center">Dashboard</td>
<td align="center">Transactions</td>
</tr>
</table>

## Requirements

- **Python 3.11** or newer
- **pip** (Python package manager)
- **tkinter** (usually included with Python)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Syedk07/Expense-Tracker-using-python.git
cd Expense-Tracker-using-python
```

### 2. Create a virtual environment

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python -m spendwise
```

## Usage

### Adding Expenses

1. Click the **"+ Add Expense"** button in the Transactions view
2. Fill in the expense details:
   - Description (required)
   - Amount (required, must be positive)
   - Category (required)
   - Date (required, format: YYYY-MM-DD)
   - Notes (optional)
3. Click **Save**

### Viewing Reports

1. Navigate to the **Reports** section
2. Select report type:
   - **Monthly** - View expenses for a specific month
   - **Yearly** - View annual summary with monthly breakdown
   - **Custom Range** - Specify start and end dates
3. Review spending summaries and category breakdowns

### Exporting Data

1. Go to **Settings**
2. In the "Export Data" section:
   - Optionally filter by category or date range
   - Click **"Export to CSV"**
3. Choose a location to save your file

## Project Structure

```
SpendWise/
├── src/
│   └── spendwise/           # Main application package
│       ├── database/        # Database management
│       │   ├── __init__.py
│       │   └── db.py        # SQLite connection and initialization
│       ├── models/          # Data models
│       │   ├── __init__.py
│       │   └── expense.py   # Expense model and validation
│       ├── services/        # Business logic
│       │   ├── __init__.py
│       │   ├── expense_service.py   # CRUD operations
│       │   ├── report_service.py    # Report generation
│       │   └── export_service.py    # CSV export
│       ├── ui/              # User interface
│       │   ├── __init__.py
│       │   ├── styles.py            # UI styling constants
│       │   ├── main_window.py       # Main window and navigation
│       │   ├── dashboard.py         # Dashboard view
│       │   ├── transactions.py      # Transactions view
│       │   ├── reports.py           # Reports view
│       │   └── settings.py          # Settings view
│       ├── utils/           # Utility functions
│       │   ├── __init__.py
│       │   └── paths.py     # Cross-platform path handling
│       ├── __init__.py
│       ├── __main__.py      # Module entry point
│       └── app.py           # Application initialization
├── tests/                   # Automated tests
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_database.py
│   ├── test_expenses.py
│   ├── test_reports.py
│   └── test_export.py
├── docs/                    # Documentation
│   └── screenshots/
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
├── README.md
├── requirements.txt         # Python dependencies
└── pyproject.toml          # Project configuration
```

## Development

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage report:
```bash
pytest --cov=spendwise --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_expenses.py -v
```

### Code Organization

- **Models** - Data structures and validation logic
- **Services** - Business logic and database operations
- **UI** - User interface components (Tkinter)
- **Utils** - Helper functions and utilities

### Technology Stack

- **Python 3.11+** - Core language
- **Tkinter/ttk** - GUI framework
- **SQLite** - Local database
- **platformdirs** - Cross-platform directory paths
- **pytest** - Testing framework
- **Decimal** - Precise monetary calculations

## Data Storage

SpendWise stores your data locally in a SQLite database. The database location varies by operating system:

- **Windows:** `C:\Users\<YourUsername>\AppData\Local\SpendWise\spendwise.db`
- **Linux:** `~/.local/share/SpendWise/spendwise.db`
- **macOS:** `~/Library/Application Support/SpendWise/spendwise.db`

Your data never leaves your computer unless you explicitly export it.

## Features in Detail

### Expense Categories

- Food & Dining
- Transportation
- Education
- Shopping
- Bills & Utilities
- Health
- Entertainment
- Travel
- Personal Care
- Other

### Reports Available

1. **Monthly Summary** - Total spending, transaction count, average daily spending, and category breakdown for a selected month
2. **Yearly Summary** - Annual overview with monthly breakdown and spending trends
3. **Custom Range** - Flexible date range analysis with category insights

### Data Export

Export your expenses to CSV format with:
- Optional category filtering
- Custom date range selection
- UTF-8 encoding for special characters
- Compatible with Excel, Google Sheets, and other spreadsheet applications

## Troubleshooting

### Application won't start

1. Verify Python version: `python --version` (should be 3.11 or newer)
2. Ensure virtual environment is activated
3. Reinstall dependencies: `pip install -r requirements.txt`

### Database errors

The application will create the database automatically. If you encounter database errors:
1. Check that the application data directory is writable
2. Try deleting the database file (you'll lose your data)
3. Restart the application to create a fresh database

### Import errors

Make sure you're running the application from the project root directory:
```bash
python -m spendwise
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Code style guidelines
- Testing requirements
- Pull request process
- Reporting issues

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and Tkinter
- Inspired by the need for simple, privacy-focused expense tracking
- Designed for beginner programmers learning software development

## Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review existing issues on GitHub
3. Open a new issue with details about your problem

## Roadmap

Future enhancements under consideration:
- Budget tracking and alerts
- Recurring expense support
- Data backup and restore
- Additional chart visualizations
- Multi-currency support

---

**Note:** SpendWise is a personal project designed for learning and practical use. It prioritizes simplicity, privacy, and ease of use over advanced features.
