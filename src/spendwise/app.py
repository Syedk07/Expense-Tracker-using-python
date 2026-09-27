"""
Application initialization and entry point.
"""
import tkinter as tk
from tkinter import messagebox

from spendwise.database.db import initialize_database
from spendwise.ui.main_window import MainWindow


def run_app():
    """
    Initialize and run the SpendWise application.
    
    Sets up the database, creates the main window, and starts the GUI loop.
    """
    try:
        # Initialize the database
        initialize_database()
        
        # Create the main window
        root = tk.Tk()
        app = MainWindow(root)
        app.run()
        
    except Exception as e:
        # Show error dialog if something goes wrong during startup
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror(
            "Startup Error",
            f"Failed to start SpendWise:\n\n{str(e)}\n\nPlease check your installation and try again."
        )
        root.destroy()
        raise
