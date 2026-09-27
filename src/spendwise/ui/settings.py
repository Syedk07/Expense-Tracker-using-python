"""
Settings view for application preferences and data management.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
from pathlib import Path

from spendwise import __version__, __app_name__
from spendwise.ui.styles import COLORS, FONTS, SPACING
from spendwise.services.export_service import ExportService
from spendwise.services.expense_service import ExpenseService
from spendwise.models.expense import DEFAULT_CATEGORIES
from spendwise.utils.paths import get_database_path, get_app_data_dir


class SettingsView:
    """Settings and data management view."""
    
    def __init__(self, parent, main_window):
        """
        Initialize the settings view.
        
        Args:
            parent: Parent frame
            main_window: Reference to main window
        """
        self.parent = parent
        self.main_window = main_window
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create settings view widgets."""
        # Create scrollable container
        self.create_scrollable_container()
        
        # Header
        header_frame = tk.Frame(self.container, bg=COLORS['background'])
        header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['lg'], SPACING['sm']))
        
        title = tk.Label(
            header_frame,
            text="Settings",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        )
        title.pack(side='left')
        
        # Data Export Section
        self.create_export_section()
        
        # Data Management Section
        self.create_data_management_section()
        
        # Application Info Section
        self.create_info_section()
        
        # Data Location Section
        self.create_data_section()
    
    def create_scrollable_container(self):
        """Create a scrollable container for settings content."""
        canvas = tk.Canvas(self.parent, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.parent, orient='vertical', command=canvas.yview)
        
        self.container = tk.Frame(canvas, bg=COLORS['background'])
        
        self.container.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.container, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel and trackpad scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _on_linux_scroll(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel (Windows/Mac)
        canvas.bind('<MouseWheel>', _on_mousewheel)
        self.container.bind('<MouseWheel>', _on_mousewheel)
        
        # Bind for Linux/Unix
        canvas.bind('<Button-4>', _on_linux_scroll)
        canvas.bind('<Button-5>', _on_linux_scroll)
        self.container.bind('<Button-4>', _on_linux_scroll)
        self.container.bind('<Button-5>', _on_linux_scroll)
        
        # Bind to all child widgets recursively
        def bind_to_mousewheel(widget):
            widget.bind('<MouseWheel>', _on_mousewheel)
            widget.bind('<Button-4>', _on_linux_scroll)
            widget.bind('<Button-5>', _on_linux_scroll)
            for child in widget.winfo_children():
                bind_to_mousewheel(child)
        
        self.container.bind('<Map>', lambda e: bind_to_mousewheel(self.container))
    
    def create_export_section(self):
        """Create data export section."""
        section = tk.Frame(self.container, bg=COLORS['surface'])
        section.pack(fill='x', padx=SPACING['xl'], pady=SPACING['md'])
        
        # Section header
        header = tk.Frame(section, bg=COLORS['surface'])
        header.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])
        
        tk.Label(
            header,
            text="Export Data",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left')
        
        # Export options
        options_frame = tk.Frame(section, bg=COLORS['surface'])
        options_frame.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        
        tk.Label(
            options_frame,
            text="Export your expenses to a CSV file for use in spreadsheet applications.",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium']
        ).pack(anchor='w', pady=(0, SPACING['md']))
        
        # Filter options
        filter_frame = tk.Frame(options_frame, bg=COLORS['surface'])
        filter_frame.pack(fill='x', pady=SPACING['sm'])
        
        # Category filter
        tk.Label(
            filter_frame,
            text="Category:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(0, SPACING['sm']))
        
        self.export_category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.export_category_var,
            values=["All"] + DEFAULT_CATEGORIES,
            state='readonly',
            width=20
        )
        category_combo.pack(side='left', padx=SPACING['sm'])
        
        # Date range
        tk.Label(
            filter_frame,
            text="From:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['lg'], SPACING['sm']))
        
        self.export_start_var = tk.StringVar()
        start_entry = tk.Entry(filter_frame, textvariable=self.export_start_var, width=12)
        start_entry.pack(side='left', padx=SPACING['sm'])
        
        tk.Label(
            filter_frame,
            text="To:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['md'], SPACING['sm']))
        
        self.export_end_var = tk.StringVar()
        end_entry = tk.Entry(filter_frame, textvariable=self.export_end_var, width=12)
        end_entry.pack(side='left', padx=SPACING['sm'])
        
        tk.Label(
            options_frame,
            text="Leave dates empty to export all expenses. Format: YYYY-MM-DD",
            font=FONTS['small'],
            bg=COLORS['surface'],
            fg=COLORS['text_light']
        ).pack(anchor='w', pady=(SPACING['xs'], SPACING['md']))
        
        # Export button
        export_btn = tk.Button(
            options_frame,
            text="Export to CSV",
            command=self.export_to_csv,
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['success'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['lg'],
            pady=SPACING['sm']
        )
        export_btn.pack(anchor='w', pady=SPACING['sm'])
    
    def create_data_management_section(self):
        """Create data management section."""
        section = tk.Frame(self.container, bg=COLORS['surface'])
        section.pack(fill='x', padx=SPACING['xl'], pady=SPACING['md'])
        
        # Section header
        header = tk.Frame(section, bg=COLORS['surface'])
        header.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])
        
        tk.Label(
            header,
            text="Data Management",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left')
        
        # Management options
        options_frame = tk.Frame(section, bg=COLORS['surface'])
        options_frame.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        
        tk.Label(
            options_frame,
            text="⚠️ Warning: This action cannot be undone!",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['danger']
        ).pack(anchor='w', pady=(0, SPACING['sm']))
        
        tk.Label(
            options_frame,
            text="Delete all your expense data from the database.",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium']
        ).pack(anchor='w', pady=(0, SPACING['md']))
        
        # Clear data button
        clear_btn = tk.Button(
            options_frame,
            text="🗑️ Clear All Data",
            command=self.clear_all_data,
            font=FONTS['body'],
            bg=COLORS['danger'],
            fg=COLORS['text_white'],
            activebackground='#c0392b',
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['lg'],
            pady=SPACING['sm']
        )
        clear_btn.pack(anchor='w', pady=SPACING['sm'])
    
    def create_info_section(self):
        """Create application info section."""
        section = tk.Frame(self.container, bg=COLORS['surface'])
        section.pack(fill='x', padx=SPACING['xl'], pady=SPACING['md'])
        
        # Section header
        header = tk.Frame(section, bg=COLORS['surface'])
        header.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])
        
        tk.Label(
            header,
            text="Application Information",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left')
        
        # Info content
        info_frame = tk.Frame(section, bg=COLORS['surface'])
        info_frame.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        
        info_items = [
            ("Application:", __app_name__),
            ("Version:", __version__),
            ("Description:", "Personal Expense Tracker"),
            ("Database:", "SQLite (Local)"),
        ]
        
        for label, value in info_items:
            item_frame = tk.Frame(info_frame, bg=COLORS['surface'])
            item_frame.pack(fill='x', pady=SPACING['xs'])
            
            tk.Label(
                item_frame,
                text=label,
                font=FONTS['body'],
                bg=COLORS['surface'],
                fg=COLORS['text_medium'],
                width=15,
                anchor='w'
            ).pack(side='left')
            
            tk.Label(
                item_frame,
                text=value,
                font=FONTS['body'],
                bg=COLORS['surface'],
                fg=COLORS['text_dark'],
                anchor='w'
            ).pack(side='left', padx=SPACING['sm'])
        
        # Statistics
        stats_frame = tk.Frame(info_frame, bg=COLORS['surface'])
        stats_frame.pack(fill='x', pady=(SPACING['md'], 0))
        
        total_expenses = ExpenseService.get_expense_count()
        
        tk.Label(
            stats_frame,
            text="Total Expenses:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium'],
            width=15,
            anchor='w'
        ).pack(side='left')
        
        tk.Label(
            stats_frame,
            text=str(total_expenses),
            font=FONTS['subheading'],
            bg=COLORS['surface'],
            fg=COLORS['secondary'],
            anchor='w'
        ).pack(side='left', padx=SPACING['sm'])
    
    def create_data_section(self):
        """Create data location section."""
        section = tk.Frame(self.container, bg=COLORS['surface'])
        section.pack(fill='x', padx=SPACING['xl'], pady=SPACING['md'])
        
        # Section header
        header = tk.Frame(section, bg=COLORS['surface'])
        header.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])
        
        tk.Label(
            header,
            text="Data Location",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left')
        
        # Location info
        info_frame = tk.Frame(section, bg=COLORS['surface'])
        info_frame.pack(fill='x', padx=SPACING['md'], pady=(0, SPACING['md']))
        
        tk.Label(
            info_frame,
            text="Your expense data is stored locally on your computer:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium']
        ).pack(anchor='w', pady=(0, SPACING['sm']))
        
        # Database path
        db_path = get_database_path()
        path_frame = tk.Frame(info_frame, bg=COLORS['background'])
        path_frame.pack(fill='x', pady=SPACING['sm'])
        
        path_text = tk.Text(
            path_frame,
            height=2,
            wrap='word',
            font=('Courier New', 9),
            bg=COLORS['background'],
            fg=COLORS['text_dark'],
            relief='flat',
            padx=SPACING['sm'],
            pady=SPACING['sm']
        )
        path_text.pack(fill='x')
        path_text.insert('1.0', str(db_path))
        path_text.config(state='disabled')
        
        # Open folder button
        open_btn = tk.Button(
            info_frame,
            text="Open Data Folder",
            command=self.open_data_folder,
            font=FONTS['body'],
            bg=COLORS['accent'],
            fg=COLORS['text_white'],
            activebackground=COLORS['info'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['md'],
            pady=SPACING['sm']
        )
        open_btn.pack(anchor='w', pady=(SPACING['sm'], 0))
    
    def export_to_csv(self):
        """Handle CSV export."""
        try:
            # Parse filters
            category = self.export_category_var.get()
            category = None if category == "All" else category
            
            start_date = None
            end_date = None
            
            start_str = self.export_start_var.get().strip()
            if start_str:
                from datetime import datetime
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            
            end_str = self.export_end_var.get().strip()
            if end_str:
                from datetime import datetime
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            
            # Get export summary
            summary = ExportService.get_export_summary(
                start_date=start_date,
                end_date=end_date,
                category=category
            )
            
            if summary['count'] == 0:
                messagebox.showwarning(
                    "No Data",
                    "No expenses found matching the specified filters."
                )
                return
            
            # Ask user for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Expenses to CSV",
                initialfile=f"spendwise_export_{date.today().strftime('%Y%m%d')}.csv"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Perform export
            count = ExportService.export_to_csv(
                file_path=file_path,
                start_date=start_date,
                end_date=end_date,
                category=category
            )
            
            messagebox.showinfo(
                "Export Successful",
                f"Successfully exported {count} expenses to:\n\n{file_path}"
            )
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n\n{str(e)}")
    
    def open_data_folder(self):
        """Open the data folder in file explorer."""
        import subprocess
        import sys
        
        data_dir = get_app_data_dir()
        
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', str(data_dir)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', str(data_dir)])
            else:  # Linux
                subprocess.run(['xdg-open', str(data_dir)])
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not open folder:\n\n{str(e)}\n\nFolder location:\n{data_dir}"
            )
    
    def clear_all_data(self):
        """Clear all expense data after confirmation."""
        # Get current count
        count = ExpenseService.get_expense_count()
        
        if count == 0:
            messagebox.showinfo(
                "No Data",
                "There is no expense data to delete.\n\nThe database is already empty."
            )
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "⚠️ Confirm Delete All Data",
            f"Are you sure you want to delete ALL {count} expense(s)?\n\n"
            "This action cannot be undone!\n\n"
            "All your expense records will be permanently deleted.",
            icon='warning'
        )
        
        if not confirm:
            return
        
        # Double confirmation for safety
        double_confirm = messagebox.askyesno(
            "⚠️ Final Confirmation",
            "This is your last chance!\n\n"
            f"Delete all {count} expense records permanently?",
            icon='warning'
        )
        
        if not double_confirm:
            return
        
        try:
            # Delete all expenses
            from spendwise.database.db import get_connection
            
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM expenses")
                conn.commit()
            
            messagebox.showinfo(
                "✓ Data Cleared",
                f"Successfully deleted all {count} expense records.\n\n"
                "Your database is now empty and ready for new expenses."
            )
            
            # Refresh the current view
            self.main_window.show_dashboard()
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to clear data:\n\n{str(e)}"
            )
