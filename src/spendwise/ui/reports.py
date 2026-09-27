"""
Reports view showing expense analysis and insights.
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime, date, timedelta
from calendar import monthrange

from spendwise.ui.styles import COLORS, FONTS, SPACING
from spendwise.services.report_service import ReportService


class ReportsView:
    """Reports and insights view."""
    
    def __init__(self, parent, main_window):
        """
        Initialize the reports view.
        
        Args:
            parent: Parent frame
            main_window: Reference to main window
        """
        self.parent = parent
        self.main_window = main_window
        
        # Current report type
        self.report_type = "monthly"
        self.selected_date = date.today()
        
        self.create_widgets()
        self.load_report()
    
    def create_widgets(self):
        """Create report view widgets."""
        # Create scrollable container
        self.create_scrollable_container()
        
        # Header
        header_frame = tk.Frame(self.container, bg=COLORS['background'])
        header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['lg'], SPACING['sm']))
        
        title = tk.Label(
            header_frame,
            text="Reports & Insights",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        )
        title.pack(side='left')
        
        # Report type selector
        selector_frame = tk.Frame(self.container, bg=COLORS['surface'])
        selector_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['md'])
        
        tk.Label(
            selector_frame,
            text="Report Period:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['md'], SPACING['sm']))
        
        self.report_var = tk.StringVar(value="monthly")
        
        periods = [
            ("Monthly", "monthly"),
            ("Yearly", "yearly"),
            ("Custom Range", "custom")
        ]
        
        for text, value in periods:
            rb = tk.Radiobutton(
                selector_frame,
                text=text,
                variable=self.report_var,
                value=value,
                command=self.on_report_type_changed,
                font=FONTS['body'],
                bg=COLORS['surface'],
                fg=COLORS['text_dark'],
                selectcolor=COLORS['background'],
                activebackground=COLORS['surface'],
                activeforeground=COLORS['text_dark']
            )
            rb.pack(side='left', padx=SPACING['sm'])
        
        # Date selector frame (will be populated based on report type)
        self.date_selector_frame = tk.Frame(self.container, bg=COLORS['surface'])
        self.date_selector_frame.pack(fill='x', padx=SPACING['xl'], pady=(0, SPACING['md']))
        
        # Report content frame
        self.report_frame = tk.Frame(self.container, bg=COLORS['background'])
        self.report_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['md'])
        
        # Initialize date selector
        self.update_date_selector()
    
    def create_scrollable_container(self):
        """Create a scrollable container for report content."""
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
    
    def on_report_type_changed(self):
        """Handle report type change."""
        self.report_type = self.report_var.get()
        self.update_date_selector()
        self.load_report()
    
    def update_date_selector(self):
        """Update date selector based on report type."""
        # Clear existing widgets
        for widget in self.date_selector_frame.winfo_children():
            widget.destroy()
        
        if self.report_type == "monthly":
            self.create_monthly_selector()
        elif self.report_type == "yearly":
            self.create_yearly_selector()
        elif self.report_type == "custom":
            self.create_custom_selector()
    
    def create_monthly_selector(self):
        """Create month/year selector."""
        tk.Label(
            self.date_selector_frame,
            text="Select Month:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['md'], SPACING['sm']))
        
        # Month selector
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        self.month_var = tk.StringVar(value=months[self.selected_date.month - 1])
        month_combo = ttk.Combobox(
            self.date_selector_frame,
            textvariable=self.month_var,
            values=months,
            state='readonly',
            width=12
        )
        month_combo.pack(side='left', padx=SPACING['sm'])
        month_combo.bind('<<ComboboxSelected>>', lambda e: self.load_report())
        
        # Year selector
        current_year = date.today().year
        years = [str(y) for y in range(current_year - 5, current_year + 1)]
        
        self.year_var = tk.StringVar(value=str(self.selected_date.year))
        year_combo = ttk.Combobox(
            self.date_selector_frame,
            textvariable=self.year_var,
            values=years,
            state='readonly',
            width=8
        )
        year_combo.pack(side='left', padx=SPACING['sm'])
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_report())
    
    def create_yearly_selector(self):
        """Create year selector."""
        tk.Label(
            self.date_selector_frame,
            text="Select Year:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['md'], SPACING['sm']))
        
        current_year = date.today().year
        years = [str(y) for y in range(current_year - 5, current_year + 1)]
        
        self.year_var = tk.StringVar(value=str(self.selected_date.year))
        year_combo = ttk.Combobox(
            self.date_selector_frame,
            textvariable=self.year_var,
            values=years,
            state='readonly',
            width=8
        )
        year_combo.pack(side='left', padx=SPACING['sm'])
        year_combo.bind('<<ComboboxSelected>>', lambda e: self.load_report())
    
    def create_custom_selector(self):
        """Create custom date range selector."""
        tk.Label(
            self.date_selector_frame,
            text="From:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['md'], SPACING['sm']))
        
        self.start_date_var = tk.StringVar(
            value=(date.today() - timedelta(days=30)).strftime('%Y-%m-%d')
        )
        start_entry = tk.Entry(
            self.date_selector_frame,
            textvariable=self.start_date_var,
            width=12
        )
        start_entry.pack(side='left', padx=SPACING['sm'])
        
        tk.Label(
            self.date_selector_frame,
            text="To:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left', padx=(SPACING['md'], SPACING['sm']))
        
        self.end_date_var = tk.StringVar(value=date.today().strftime('%Y-%m-%d'))
        end_entry = tk.Entry(
            self.date_selector_frame,
            textvariable=self.end_date_var,
            width=12
        )
        end_entry.pack(side='left', padx=SPACING['sm'])
        
        # Load button
        load_btn = tk.Button(
            self.date_selector_frame,
            text="Load Report",
            command=self.load_report,
            font=FONTS['body'],
            bg=COLORS['accent'],
            fg=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['md'],
            pady=SPACING['xs']
        )
        load_btn.pack(side='left', padx=SPACING['md'])
    
    def load_report(self):
        """Load and display the report."""
        # Clear existing report
        for widget in self.report_frame.winfo_children():
            widget.destroy()
        
        try:
            if self.report_type == "monthly":
                self.load_monthly_report()
            elif self.report_type == "yearly":
                self.load_yearly_report()
            elif self.report_type == "custom":
                self.load_custom_report()
        except Exception as e:
            error_label = tk.Label(
                self.report_frame,
                text=f"Error loading report: {str(e)}",
                font=FONTS['body'],
                bg=COLORS['background'],
                fg=COLORS['danger']
            )
            error_label.pack(pady=SPACING['xl'])
    
    def load_monthly_report(self):
        """Load monthly report."""
        # Get selected month and year
        months = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month = months.index(self.month_var.get()) + 1
        year = int(self.year_var.get())
        
        # Get report data
        summary = ReportService.get_monthly_summary(year, month)
        
        # Display report
        self.display_summary_report(
            summary,
            f"{self.month_var.get()} {year}"
        )
    
    def load_yearly_report(self):
        """Load yearly report."""
        year = int(self.year_var.get())
        
        # Get report data
        summary = ReportService.get_yearly_summary(year)
        
        # Display report
        self.display_summary_report(summary, str(year))
        
        # Add monthly breakdown
        if summary.get('monthly_breakdown'):
            self.display_monthly_breakdown(summary['monthly_breakdown'])
    
    def load_custom_report(self):
        """Load custom date range report."""
        try:
            start_date = datetime.strptime(self.start_date_var.get(), '%Y-%m-%d').date()
            end_date = datetime.strptime(self.end_date_var.get(), '%Y-%m-%d').date()
            
            if start_date > end_date:
                raise ValueError("Start date must be before end date")
            
            # Get report data
            summary = ReportService.get_date_range_summary(start_date, end_date)
            
            # Display report
            self.display_summary_report(
                summary,
                f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"
            )
            
        except ValueError as e:
            error_label = tk.Label(
                self.report_frame,
                text=f"Invalid date format: {str(e)}\nPlease use YYYY-MM-DD format",
                font=FONTS['body'],
                bg=COLORS['background'],
                fg=COLORS['danger']
            )
            error_label.pack(pady=SPACING['xl'])
    
    def display_summary_report(self, summary, period_label):
        """Display summary report."""
        # Period header
        period_frame = tk.Frame(self.report_frame, bg=COLORS['background'])
        period_frame.pack(fill='x', pady=(0, SPACING['md']))
        
        tk.Label(
            period_frame,
            text=f"Report for {period_label}",
            font=FONTS['heading'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        ).pack(anchor='w')
        
        # Summary cards
        cards_frame = tk.Frame(self.report_frame, bg=COLORS['background'])
        cards_frame.pack(fill='x', pady=SPACING['md'])
        
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)
        
        # Total spending
        self.create_report_card(
            cards_frame, 0,
            "Total Spending",
            f"${summary['total']:,.2f}",
            COLORS['danger']
        )
        
        # Transactions
        self.create_report_card(
            cards_frame, 1,
            "Transactions",
            str(summary['count']),
            COLORS['info']
        )
        
        # Average daily
        self.create_report_card(
            cards_frame, 2,
            "Avg. Daily",
            f"${summary['avg_daily']:,.2f}",
            COLORS['warning']
        )
        
        # Top category
        top_cat = summary['top_category'] or "N/A"
        self.create_report_card(
            cards_frame, 3,
            "Top Category",
            top_cat,
            COLORS['secondary']
        )
        
        # Category breakdown
        if summary['categories']:
            cat_frame = tk.Frame(self.report_frame, bg=COLORS['surface'])
            cat_frame.pack(fill='both', expand=True, pady=SPACING['lg'])
            
            tk.Label(
                cat_frame,
                text="Spending by Category",
                font=FONTS['heading'],
                bg=COLORS['surface'],
                fg=COLORS['text_dark']
            ).pack(anchor='w', padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
            
            for category, amount in summary['categories'].items():
                percentage = (float(amount) / float(summary['total']) * 100) if summary['total'] > 0 else 0
                self.create_category_bar(cat_frame, category, amount, percentage)
        else:
            empty_label = tk.Label(
                self.report_frame,
                text="No expenses recorded for this period",
                font=FONTS['body'],
                bg=COLORS['background'],
                fg=COLORS['text_medium']
            )
            empty_label.pack(pady=SPACING['xl'])
    
    def create_report_card(self, parent, column, label, value, color):
        """Create a report statistic card."""
        card = tk.Frame(parent, bg=COLORS['surface'], relief='flat')
        card.grid(row=0, column=column, padx=SPACING['sm'], pady=SPACING['sm'], sticky='ew')
        
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
    
    def create_category_bar(self, parent, category, amount, percentage):
        """Create a category spending bar."""
        item_frame = tk.Frame(parent, bg=COLORS['surface'])
        item_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['sm'])
        
        # Category name and amount
        info_frame = tk.Frame(item_frame, bg=COLORS['surface'])
        info_frame.pack(fill='x')
        
        tk.Label(
            info_frame,
            text=category,
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(side='left')
        
        tk.Label(
            info_frame,
            text=f"${amount:,.2f} ({percentage:.1f}%)",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_medium']
        ).pack(side='right')
        
        # Progress bar
        bar_bg = tk.Frame(item_frame, bg=COLORS['border'], height=8)
        bar_bg.pack(fill='x', pady=(SPACING['xs'], 0))
        
        bar_width = int(percentage * 10)  # Scale to fit
        bar_fill = tk.Frame(bar_bg, bg=COLORS['secondary'], width=bar_width, height=8)
        bar_fill.place(x=0, y=0, relheight=1)
    
    def display_monthly_breakdown(self, monthly_data):
        """Display monthly breakdown for yearly report."""
        breakdown_frame = tk.Frame(self.report_frame, bg=COLORS['surface'])
        breakdown_frame.pack(fill='both', expand=True, pady=SPACING['lg'])
        
        tk.Label(
            breakdown_frame,
            text="Monthly Breakdown",
            font=FONTS['heading'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        ).pack(anchor='w', padx=SPACING['md'], pady=(SPACING['md'], SPACING['sm']))
        
        # Create table
        for month_data in monthly_data:
            if month_data['total'] > 0:  # Only show months with expenses
                month_name = date(2024, month_data['month'], 1).strftime('%B')
                item_frame = tk.Frame(breakdown_frame, bg=COLORS['surface'])
                item_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['xs'])
                
                tk.Label(
                    item_frame,
                    text=month_name,
                    font=FONTS['body'],
                    bg=COLORS['surface'],
                    fg=COLORS['text_dark']
                ).pack(side='left')
                
                tk.Label(
                    item_frame,
                    text=f"${month_data['total']:,.2f} ({month_data['count']} transactions)",
                    font=FONTS['body'],
                    bg=COLORS['surface'],
                    fg=COLORS['text_medium']
                ).pack(side='right')
