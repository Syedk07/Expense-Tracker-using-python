"""
Dashboard view showing expense summaries and statistics.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date
from decimal import Decimal

from spendwise.ui.styles import COLORS, FONTS, SPACING
from spendwise.services.expense_service import ExpenseService


class DashboardView:
    """Dashboard view with expense summaries."""
    
    def __init__(self, parent, main_window):
        """
        Initialize the dashboard view.
        
        Args:
            parent: Parent frame
            main_window: Reference to main window
        """
        self.parent = parent
        self.main_window = main_window
        
        # Create scrollable container
        self.create_scrollable_container()
        
        # Load and display data
        self.load_data()
        self.create_widgets()
    
    def create_scrollable_container(self):
        """Create a scrollable container for dashboard content."""
        # Canvas for scrolling
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
    
    def load_data(self):
        """Load dashboard data from database."""
        today = date.today()
        
        # Get all expenses
        all_expenses = ExpenseService.get_all_expenses()
        
        # Calculate totals
        self.today_total = sum(
            e.amount for e in all_expenses
            if e.expense_date.date() == today
        )
        
        self.month_total = sum(
            e.amount for e in all_expenses
            if e.expense_date.year == today.year and e.expense_date.month == today.month
        )
        
        self.year_total = sum(
            e.amount for e in all_expenses
            if e.expense_date.year == today.year
        )
        
        self.transaction_count = len(all_expenses)
        
        # Category breakdown for current month
        self.category_totals = {}
        month_expenses = [
            e for e in all_expenses
            if e.expense_date.year == today.year and e.expense_date.month == today.month
        ]
        
        for expense in month_expenses:
            category = expense.category
            self.category_totals[category] = self.category_totals.get(category, Decimal('0')) + expense.amount
        
        # Sort categories by amount
        self.category_totals = dict(sorted(
            self.category_totals.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        # Recent expenses (last 10)
        self.recent_expenses = all_expenses[:10] if all_expenses else []
    
    def create_widgets(self):
        """Create dashboard widgets."""
        # Header
        header_frame = tk.Frame(self.container, bg=COLORS['background'])
        header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['lg'], SPACING['sm']))
        
        title = tk.Label(
            header_frame,
            text="Dashboard",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        )
        title.pack(side='left')
        
        subtitle = tk.Label(
            header_frame,
            text=datetime.now().strftime("%B %d, %Y"),
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_medium']
        )
        subtitle.pack(side='left', padx=SPACING['md'])
        
        # Summary cards
        self.create_summary_cards()
        
        # Category breakdown and recent transactions
        content_frame = tk.Frame(self.container, bg=COLORS['background'])
        content_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['md'])
        
        # Categories on the left
        categories_frame = tk.Frame(content_frame, bg=COLORS['background'])
        categories_frame.pack(side='left', fill='both', expand=True, padx=(0, SPACING['sm']))
        self.create_category_section(categories_frame)
        
        # Recent transactions on the right
        recent_frame = tk.Frame(content_frame, bg=COLORS['background'])
        recent_frame.pack(side='right', fill='both', expand=True, padx=(SPACING['sm'], 0))
        self.create_recent_section(recent_frame)
    
    def create_summary_cards(self):
        """Create summary statistic cards."""
        cards_frame = tk.Frame(self.container, bg=COLORS['background'])
        cards_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['md'])
        
        # Configure grid
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Today card
        self.create_stat_card(
            cards_frame, 0,
            "Today",
            f"${self.today_total:,.2f}",
            COLORS['info']
        )
        
        # Month card
        self.create_stat_card(
            cards_frame, 1,
            "This Month",
            f"${self.month_total:,.2f}",
            COLORS['secondary']
        )
        
        # Year card
        self.create_stat_card(
            cards_frame, 2,
            "This Year",
            f"${self.year_total:,.2f}",
            COLORS['accent']
        )
        
        # Transactions card
        self.create_stat_card(
            cards_frame, 3,
            "Transactions",
            str(self.transaction_count),
            COLORS['warning']
        )
    
    def create_stat_card(self, parent, column, label, value, color):
        """Create a statistic card."""
        card = tk.Frame(
            parent,
            bg=COLORS['surface'],
            relief='flat',
            bd=0
        )
        card.grid(row=0, column=column, padx=SPACING['sm'], pady=SPACING['sm'], sticky='ew')
        
        # Add subtle border effect
        border_frame = tk.Frame(card, bg=color, height=4)
        border_frame.pack(fill='x')
        
        content = tk.Frame(card, bg=COLORS['surface'])
        content.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['md'])
        
        label_widget = tk.Label(
            content,
            text=label,
            font=FONTS['small'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium']
        )
        label_widget.pack(anchor='w')
        
        value_widget = tk.Label(
            content,
            text=value,
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        value_widget.pack(anchor='w', pady=(SPACING['xs'], 0))
    
    def create_category_section(self, parent):
        """Create category breakdown section."""
        card = tk.Frame(parent, bg=COLORS['surface'])
        card.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(card, bg=COLORS['surface'])
        header.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])
        
        title = tk.Label(
            header,
            text="Spending by Category",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        title.pack(side='left')
        
        month_label = tk.Label(
            header,
            text=f"({datetime.now().strftime('%B %Y')})",
            font=FONTS['small'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium']
        )
        month_label.pack(side='left', padx=SPACING['sm'])
        
        # Categories list
        if self.category_totals:
            for category, amount in list(self.category_totals.items())[:5]:
                self.create_category_item(card, category, amount)
        else:
            empty_label = tk.Label(
                card,
                text="No expenses this month",
                font=FONTS['body'],
                bg=COLORS['surface'],
                fg=COLORS['text_medium']
            )
            empty_label.pack(pady=SPACING['xl'])
    
    def create_category_item(self, parent, category, amount):
        """Create a category breakdown item."""
        item = tk.Frame(parent, bg=COLORS['surface'])
        item.pack(fill='x', padx=SPACING['md'], pady=SPACING['xs'])
        
        # Category name
        name = tk.Label(
            item,
            text=category,
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        name.pack(side='left')
        
        # Amount
        amount_label = tk.Label(
            item,
            text=f"${amount:,.2f}",
            font=FONTS['subheading'],
            bg=COLORS['surface'],
            fg=COLORS['secondary']
        )
        amount_label.pack(side='right')
    
    def create_recent_section(self, parent):
        """Create recent transactions section."""
        card = tk.Frame(parent, bg=COLORS['surface'])
        card.pack(fill='both', expand=True)
        
        # Header
        header = tk.Frame(card, bg=COLORS['surface'])
        header.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])
        
        title = tk.Label(
            header,
            text="Recent Transactions",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        title.pack(side='left')
        
        # Transactions list
        if self.recent_expenses:
            for expense in self.recent_expenses[:5]:
                self.create_transaction_item(card, expense)
        else:
            empty_label = tk.Label(
                card,
                text="No transactions yet",
                font=FONTS['body'],
                bg=COLORS['surface'],
                fg=COLORS['text_medium']
            )
            empty_label.pack(pady=SPACING['xl'])
    
    def create_transaction_item(self, parent, expense):
        """Create a transaction list item."""
        item = tk.Frame(parent, bg=COLORS['surface'])
        item.pack(fill='x', padx=SPACING['md'], pady=SPACING['xs'])
        
        # Left side - description and date
        left = tk.Frame(item, bg=COLORS['surface'])
        left.pack(side='left', fill='x', expand=True)
        
        desc = tk.Label(
            left,
            text=expense.description,
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark'],
            anchor='w'
        )
        desc.pack(anchor='w')
        
        date_cat = tk.Label(
            left,
            text=f"{expense.expense_date.strftime('%b %d')} • {expense.category}",
            font=FONTS['small'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium'],
            anchor='w'
        )
        date_cat.pack(anchor='w')
        
        # Right side - amount
        amount = tk.Label(
            item,
            text=f"${expense.amount:,.2f}",
            font=FONTS['subheading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        amount.pack(side='right')
