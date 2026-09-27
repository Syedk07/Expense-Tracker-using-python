"""
Main application window with navigation sidebar.
"""
import tkinter as tk
from tkinter import ttk

from spendwise import __app_name__, __version__
from spendwise.ui.styles import COLORS, FONTS
from spendwise.ui.dashboard import DashboardView
from spendwise.ui.transactions import TransactionsView
from spendwise.ui.reports import ReportsView
from spendwise.ui.settings import SettingsView


class MainWindow:
    """Main application window for SpendWise."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title(f"{__app_name__} v{__version__}")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 600)
        
        # Configure window background
        self.root.configure(bg=COLORS['background'])
        
        # Center the window on screen
        self.center_window()
        
        # Current view reference
        self.current_view = None
        self.current_nav_button = None
        
        # Create main layout
        self.create_layout()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_layout(self):
        """Create the main layout with sidebar and content area."""
        # Create main container
        main_container = tk.Frame(self.root, bg=COLORS['background'])
        main_container.pack(fill='both', expand=True)
        
        # Create sidebar
        self.create_sidebar(main_container)
        
        # Create content area
        self.content_frame = tk.Frame(
            main_container,
            bg=COLORS['background']
        )
        self.content_frame.pack(side='left', fill='both', expand=True)
    
    def create_sidebar(self, parent):
        """Create the navigation sidebar."""
        sidebar = tk.Frame(
            parent,
            bg=COLORS['primary'],
            width=220
        )
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # App title
        title_frame = tk.Frame(sidebar, bg=COLORS['primary'])
        title_frame.pack(fill='x', pady=20)
        
        app_title = tk.Label(
            title_frame,
            text=__app_name__,
            font=('Segoe UI', 18, 'bold'),
            bg=COLORS['primary'],
            fg=COLORS['text_white']
        )
        app_title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="Expense Tracker",
            font=('Segoe UI', 9),
            bg=COLORS['primary'],
            fg=COLORS['text_light']
        )
        subtitle.pack()
        
        # Separator
        separator = tk.Frame(sidebar, bg=COLORS['border'], height=1)
        separator.pack(fill='x', pady=15, padx=15)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        self.nav_buttons['dashboard'] = self.create_nav_button(
            sidebar, "📊 Dashboard", self.show_dashboard
        )
        
        self.nav_buttons['transactions'] = self.create_nav_button(
            sidebar, "💳 Transactions", self.show_transactions
        )
        
        self.nav_buttons['reports'] = self.create_nav_button(
            sidebar, "📈 Reports", self.show_reports
        )
        
        self.nav_buttons['settings'] = self.create_nav_button(
            sidebar, "⚙️ Settings", self.show_settings
        )
        
        # Version label at bottom
        version_label = tk.Label(
            sidebar,
            text=f"v{__version__}",
            font=('Segoe UI', 8),
            bg=COLORS['primary'],
            fg=COLORS['text_light']
        )
        version_label.pack(side='bottom', pady=10)
    
    def create_nav_button(self, parent, text, command):
        """Create a navigation button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONTS['nav'],
            bg=COLORS['primary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['accent'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            anchor='w',
            padx=20,
            pady=12,
            cursor='hand2'
        )
        btn.pack(fill='x', padx=10, pady=2)
        
        # Bind hover effects
        btn.bind('<Enter>', lambda e: btn.configure(bg=COLORS['accent']))
        btn.bind('<Leave>', lambda e: btn.configure(
            bg=COLORS['accent'] if btn == self.current_nav_button else COLORS['primary']
        ))
        
        return btn
    
    def set_active_nav_button(self, button):
        """Mark a navigation button as active."""
        # Reset previous button
        if self.current_nav_button:
            self.current_nav_button.configure(bg=COLORS['primary'])
        
        # Set new active button
        self.current_nav_button = button
        button.configure(bg=COLORS['accent'])
    
    def clear_content(self):
        """Clear the content area."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.current_view = None
    
    def show_dashboard(self):
        """Show the dashboard view."""
        self.clear_content()
        self.set_active_nav_button(self.nav_buttons['dashboard'])
        self.current_view = DashboardView(self.content_frame, self)
    
    def show_transactions(self):
        """Show the transactions view."""
        self.clear_content()
        self.set_active_nav_button(self.nav_buttons['transactions'])
        self.current_view = TransactionsView(self.content_frame, self)
    
    def show_reports(self):
        """Show the reports view."""
        self.clear_content()
        self.set_active_nav_button(self.nav_buttons['reports'])
        self.current_view = ReportsView(self.content_frame, self)
    
    def show_settings(self):
        """Show the settings view."""
        self.clear_content()
        self.set_active_nav_button(self.nav_buttons['settings'])
        self.current_view = SettingsView(self.content_frame, self)
    
    def refresh_dashboard(self):
        """Refresh the dashboard if it's the current view."""
        if self.current_view and isinstance(self.current_view, DashboardView):
            self.show_dashboard()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
