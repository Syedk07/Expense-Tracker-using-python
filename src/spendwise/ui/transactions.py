"""
Transactions view for managing expenses.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

from spendwise.ui.styles import COLORS, FONTS, SPACING
from spendwise.services.expense_service import ExpenseService
from spendwise.models.expense import DEFAULT_CATEGORIES


class TransactionsView:
    """Transactions management view."""
    
    def __init__(self, parent, main_window):
        """
        Initialize the transactions view.
        
        Args:
            parent: Parent frame
            main_window: Reference to main window
        """
        self.parent = parent
        self.main_window = main_window
        
        # Initialize tree as None first
        self.tree = None
        
        self.create_widgets()
        # Now load transactions after tree is created
        if self.tree:
            self.load_transactions()
    
    def create_widgets(self):
        """Create transaction view widgets."""
        # Header
        header_frame = tk.Frame(self.parent, bg=COLORS['background'])
        header_frame.pack(fill='x', padx=SPACING['xl'], pady=(SPACING['lg'], SPACING['sm']))
        
        title = tk.Label(
            header_frame,
            text="Transactions",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        )
        title.pack(side='left')
        
        # Add button
        add_btn = tk.Button(
            header_frame,
            text="+ Add Expense",
            command=self.show_add_dialog,
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['success'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['md'],
            pady=SPACING['sm']
        )
        add_btn.pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(self.parent, bg=COLORS['surface'])
        filter_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        
        # Search
        search_label = tk.Label(
            filter_frame,
            text="Search:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        search_label.pack(side='left', padx=(SPACING['md'], SPACING['xs']))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.load_transactions())
        
        search_entry = tk.Entry(
            filter_frame,
            textvariable=self.search_var,
            font=FONTS['body'],
            width=30
        )
        search_entry.pack(side='left', padx=SPACING['sm'])
        
        # Category filter
        category_label = tk.Label(
            filter_frame,
            text="Category:",
            font=FONTS['body'],
            bg=COLORS['surface'],
            fg=COLORS['text_dark']
        )
        category_label.pack(side='left', padx=(SPACING['lg'], SPACING['xs']))
        
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.category_var,
            values=["All"] + DEFAULT_CATEGORIES,
            state='readonly',
            font=FONTS['body'],
            width=20
        )
        category_combo.pack(side='left', padx=SPACING['sm'])
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.load_transactions())
        
        # Transaction table
        self.create_table()
    
    def create_table(self):
        """Create the transactions table."""
        table_frame = tk.Frame(self.parent, bg=COLORS['surface'])
        table_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['md'])
        
        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(table_frame, orient='vertical')
        tree_scroll_y.pack(side='right', fill='y')
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient='horizontal')
        tree_scroll_x.pack(side='bottom', fill='x')
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=('Date', 'Description', 'Category', 'Amount'),
            show='headings',
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=20
        )
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading('Date', text='Date')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Amount', text='Amount')
        
        self.tree.column('Date', width=100, anchor='center')
        self.tree.column('Description', width=300, anchor='w')
        self.tree.column('Category', width=150, anchor='center')
        self.tree.column('Amount', width=100, anchor='e')
        
        self.tree.pack(fill='both', expand=True)
        
        # Double-click to edit
        self.tree.bind('<Double-Button-1>', lambda e: self.edit_selected())
        
        # Action buttons
        btn_frame = tk.Frame(self.parent, bg=COLORS['background'])
        btn_frame.pack(fill='x', padx=SPACING['xl'], pady=SPACING['sm'])
        
        edit_btn = tk.Button(
            btn_frame,
            text="Edit",
            command=self.edit_selected,
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
        edit_btn.pack(side='left', padx=(0, SPACING['sm']))
        
        delete_btn = tk.Button(
            btn_frame,
            text="Delete",
            command=self.delete_selected,
            font=FONTS['body'],
            bg=COLORS['danger'],
            fg=COLORS['text_white'],
            activebackground='#c0392b',
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['md'],
            pady=SPACING['sm']
        )
        delete_btn.pack(side='left')
    
    def load_transactions(self):
        """Load and display transactions."""
        # Don't load if tree not created yet
        if not self.tree:
            return
            
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filters
        search_term = self.search_var.get().strip() or None
        category = self.category_var.get() if self.category_var.get() != "All" else None
        
        # Load expenses
        expenses = ExpenseService.get_all_expenses(
            category=category,
            search_term=search_term
        )
        
        # Populate table
        for expense in expenses:
            self.tree.insert('', 'end', iid=str(expense.id), values=(
                expense.expense_date.strftime('%Y-%m-%d'),
                expense.description,
                expense.category,
                f"${expense.amount:,.2f}"
            ))
    
    def show_add_dialog(self):
        """Show dialog to add a new expense."""
        dialog = ExpenseDialog(self.parent, "Add Expense")
        self.parent.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                ExpenseService.create_expense(
                    description=dialog.result['description'],
                    amount=dialog.result['amount'],
                    category=dialog.result['category'],
                    expense_date=dialog.result['date'],
                    notes=dialog.result['notes']
                )
                messagebox.showinfo("Success", "Expense added successfully!")
                self.load_transactions()
                self.main_window.refresh_dashboard()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add expense: {str(e)}")
    
    def edit_selected(self):
        """Edit the selected expense."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an expense to edit.")
            return
        
        expense_id = int(selection[0])
        expense = ExpenseService.get_expense(expense_id)
        
        if not expense:
            messagebox.showerror("Error", "Expense not found.")
            return
        
        dialog = ExpenseDialog(self.parent, "Edit Expense", expense)
        self.parent.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                ExpenseService.update_expense(
                    expense_id=expense_id,
                    description=dialog.result['description'],
                    amount=dialog.result['amount'],
                    category=dialog.result['category'],
                    expense_date=dialog.result['date'],
                    notes=dialog.result['notes']
                )
                messagebox.showinfo("Success", "Expense updated successfully!")
                self.load_transactions()
                self.main_window.refresh_dashboard()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update expense: {str(e)}")
    
    def delete_selected(self):
        """Delete the selected expense."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an expense to delete.")
            return
        
        expense_id = int(selection[0])
        expense = ExpenseService.get_expense(expense_id)
        
        if not expense:
            messagebox.showerror("Error", "Expense not found.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this expense?\n\n"
            f"Description: {expense.description}\n"
            f"Amount: ${expense.amount:,.2f}\n"
            f"Date: {expense.expense_date.strftime('%Y-%m-%d')}"
        )
        
        if confirm:
            try:
                ExpenseService.delete_expense(expense_id)
                messagebox.showinfo("Success", "Expense deleted successfully!")
                self.load_transactions()
                self.main_window.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")


class ExpenseDialog:
    """Dialog for adding/editing expenses."""
    
    def __init__(self, parent, title, expense=None):
        """
        Initialize the dialog.
        
        Args:
            parent: Parent widget
            title: Dialog title
            expense: Expense to edit (None for new expense)
        """
        self.result = None
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x550")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=COLORS['background'])
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create form
        self.create_form(expense)
    
    def create_form(self, expense):
        """Create the expense form."""
        form_frame = tk.Frame(self.dialog, bg=COLORS['background'])
        form_frame.pack(fill='both', expand=True, padx=SPACING['xl'], pady=SPACING['lg'])
        
        # Description
        tk.Label(
            form_frame,
            text="Description *",
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        ).pack(anchor='w', pady=(0, SPACING['xs']))
        
        self.desc_var = tk.StringVar(value=expense.description if expense else "")
        desc_entry = tk.Entry(form_frame, textvariable=self.desc_var, font=FONTS['body'])
        desc_entry.pack(fill='x', pady=(0, SPACING['md']))
        
        # Amount
        tk.Label(
            form_frame,
            text="Amount *",
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        ).pack(anchor='w', pady=(0, SPACING['xs']))
        
        self.amount_var = tk.StringVar(value=str(expense.amount) if expense else "")
        amount_entry = tk.Entry(form_frame, textvariable=self.amount_var, font=FONTS['body'])
        amount_entry.pack(fill='x', pady=(0, SPACING['md']))
        
        # Category
        tk.Label(
            form_frame,
            text="Category *",
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        ).pack(anchor='w', pady=(0, SPACING['xs']))
        
        self.category_var = tk.StringVar(value=expense.category if expense else DEFAULT_CATEGORIES[0])
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            values=DEFAULT_CATEGORIES,
            state='readonly',
            font=FONTS['body']
        )
        category_combo.pack(fill='x', pady=(0, SPACING['md']))
        
        # Date
        tk.Label(
            form_frame,
            text="Date *",
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        ).pack(anchor='w', pady=(0, SPACING['xs']))
        
        self.date_var = tk.StringVar(
            value=expense.expense_date.strftime('%Y-%m-%d') if expense 
            else date.today().strftime('%Y-%m-%d')
        )
        date_entry = tk.Entry(form_frame, textvariable=self.date_var, font=FONTS['body'])
        date_entry.pack(fill='x', pady=(0, SPACING['md']))
        
        # Notes
        tk.Label(
            form_frame,
            text="Notes (Optional)",
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_dark']
        ).pack(anchor='w', pady=(0, SPACING['xs']))
        
        self.notes_text = tk.Text(form_frame, font=FONTS['body'], height=4)
        self.notes_text.pack(fill='x', pady=(0, SPACING['md']))
        
        if expense and expense.notes:
            self.notes_text.insert('1.0', expense.notes)
        
        # Buttons - Large and prominent
        btn_frame = tk.Frame(form_frame, bg=COLORS['background'])
        btn_frame.pack(fill='x', pady=(SPACING['lg'], 0))
        
        save_btn = tk.Button(
            btn_frame,
            text="💾 Save Expense",
            command=self.save,
            font=('Segoe UI', 12, 'bold'),
            bg=COLORS['secondary'],
            fg=COLORS['text_white'],
            activebackground=COLORS['success'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['xl'],
            pady=SPACING['md'],
            width=20
        )
        save_btn.pack(side='left', padx=(0, SPACING['sm']))
        
        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            font=FONTS['body'],
            bg=COLORS['text_medium'],
            fg=COLORS['text_white'],
            activebackground=COLORS['text_dark'],
            activeforeground=COLORS['text_white'],
            relief='flat',
            cursor='hand2',
            padx=SPACING['lg'],
            pady=SPACING['md']
        )
        cancel_btn.pack(side='left')
    
    def save(self):
        """Save the expense data."""
        try:
            # Parse amount
            amount_str = self.amount_var.get().strip()
            if not amount_str:
                raise ValueError("Amount is required")
            
            # Remove currency symbols and commas
            amount_str = amount_str.replace('$', '').replace(',', '')
            amount = Decimal(amount_str)
            
            # Parse date
            date_str = self.date_var.get().strip()
            expense_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Get notes
            notes = self.notes_text.get('1.0', 'end-1c').strip() or None
            
            # Validate description
            description = self.desc_var.get().strip()
            if not description:
                raise ValueError("Description is required")
            
            # Set result
            self.result = {
                'description': description,
                'amount': amount,
                'category': self.category_var.get(),
                'date': expense_date,
                'notes': notes
            }
            
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e), parent=self.dialog)
        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}", parent=self.dialog)
