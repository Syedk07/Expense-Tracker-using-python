# SpendWise Quick Start Guide

## For Users Who Just Cloned the Repository

### Method 1: Quick Start (Easiest)

1. **Open terminal in the project folder**
   ```bash
   cd Expense-Tracker-using-python
   ```

2. **Create virtual environment** (first time only)
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   **Windows:**
   ```powershell
   .\venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies** (first time only)
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app**
   ```bash
   python run.py
   ```

### Method 2: Install as Package (For Development)

1-4. Follow steps 1-4 from Method 1

5. **Install in development mode**
   ```bash
   pip install -e .
   ```

6. **Run the app (multiple ways)**
   ```bash
   # Method A
   python -m spendwise
   
   # Method B
   spendwise
   ```

## Troubleshooting

### "No module named 'platformdirs'"
Make sure you:
1. Activated the virtual environment
2. Installed dependencies: `pip install -r requirements.txt`

### "No module named 'spendwise'"
Use one of these:
- `python run.py` (always works)
- OR install first: `pip install -e .`

### Virtual environment not activating
**Windows:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

## What's Next?

Once the app is running:
1. **Dashboard** - See your spending overview
2. **Transactions** - Click "+ Add Expense" to add your first expense
3. **Reports** - View spending analytics
4. **Settings** - Export data or clear all expenses

## Need Help?

- Check the main [README.md](README.md) for full documentation
- Run tests: `pytest`
- View coverage: `pytest --cov=spendwise --cov-report=html`

---

**Quick Commands Reference:**

```bash
# Activate venv (do this first!)
.\venv\Scripts\activate          # Windows
source venv/bin/activate         # Linux/Mac

# Run app
python run.py                    # Always works

# Run tests
pytest                           # After activating venv

# Deactivate venv when done
deactivate
```
