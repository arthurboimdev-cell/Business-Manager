import tkinter as tk
from tkinter import ttk, messagebox
from db.transactions import write_transaction, read_transactions
from config.config import TABLE_NAME, TREE_COLUMNS, WINDOW_TITLE, BUTTON_ADD, BUTTON_REFRESH, BUTTON_CLEAR, TRANSACTION_TYPES
# Delete from DB
from db.transactions import delete_transaction
from services.utils import TransactionUtils

class TransactionGUI:
    def __init__(self, master, table=TABLE_NAME):
        self.transactions = None
        self.master = master
        self.master.title(WINDOW_TITLE)
        self.table = table
        self.transaction_type = tk.StringVar(value=TRANSACTION_TYPES[0])

        # Make window resizable
        self.master.rowconfigure(2, weight=1)  # Treeview row expands
        self.master.columnconfigure(0, weight=1)  # Treeview column expands

        self.create_input_frame()
        self.create_buttons_frame()
        self.create_treeview()
        self.create_summary_label()
        self.create_filter_frame()
        self.refresh_transactions()

    # ------------------- Input Frame -------------------
    def create_input_frame(self):
        frame = tk.Frame(self.master)
        frame.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        self.entry_date = self.add_labeled_entry(frame, "Date (YYYY-MM-DD)", 0)
        self.entry_description = self.add_labeled_entry(frame, "Description", 1)
        self.entry_quantity = self.add_labeled_entry(frame, "Quantity", 2)
        self.entry_price = self.add_labeled_entry(frame, "Price", 3)
        self.entry_supplier = self.add_labeled_entry(frame, "Supplier", 4)  # or next available row

        # Transaction type radio buttons aligned left
        for i, t_type in enumerate(TRANSACTION_TYPES):
            tk.Radiobutton(frame, text=t_type.capitalize(), variable=self.transaction_type, value=t_type).grid(row=5, column=i, sticky='w')

    def add_labeled_entry(self, parent, label_text, row):
        tk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky='w')
        entry = tk.Entry(parent)
        entry.grid(row=row, column=1, padx=5, pady=5, sticky='w')
        return entry

    # ------------------- Buttons Frame -------------------
    def create_buttons_frame(self):
        frame = tk.Frame(self.master)
        frame.grid(row=1, column=0, pady=5, sticky='w')

        tk.Button(frame, text=BUTTON_ADD, command=self.add_transaction_gui).grid(row=0, column=0, padx=5, sticky='w')
        tk.Button(frame, text=BUTTON_REFRESH, command=self.refresh_transactions).grid(row=0, column=1, padx=5, sticky='w')
        tk.Button(frame, text=BUTTON_CLEAR, command=self.clear_entries).grid(row=0, column=2, padx=5, sticky='w')
        tk.Button(frame, text="Delete", command=self.delete_selected_transaction).grid(row=0, column=3, padx=5, sticky='w')

    # ------------------- Treeview -------------------
    def create_treeview(self):
        tree_frame = tk.Frame(self.master)
        tree_frame.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_frame, columns=TREE_COLUMNS, show="headings")
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.tree.configure(yscroll=scrollbar.set)
        style = ttk.Style()
        style.configure(
            "Treeview",
            rowheight=30  # try 35–50
        )

        # Set headings and left-align columns
        for col in TREE_COLUMNS:
            self.tree.heading(col, text=col.capitalize(), anchor='w')
            self.tree.column(col, anchor='w', width=100)

    # ------------------- Summary Label -------------------
    def create_summary_label(self):
        self.lbl_summary = tk.Label(self.master, text="", anchor='w', justify='left')
        self.lbl_summary.grid(row=3, column=0, pady=5, padx=10, sticky='w')

    # ------------------- Actions -------------------
    def clear_entries(self):
        for entry in [self.entry_date, self.entry_description, self.entry_quantity, self.entry_price]:
            entry.delete(0, tk.END)

    def add_transaction_gui(self):
        date = self.entry_date.get()
        description = TransactionUtils.normalize_text(
            self.entry_description.get()
        )

        try:
            quantity = int(self.entry_quantity.get())
            price = float(self.entry_price.get())
            supplier = TransactionUtils.normalize_text(self.entry_supplier.get())
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer, Price must be number")
            return
        t_type = self.transaction_type.get()

        write_transaction(date, description, quantity, price, t_type, supplier=supplier, table=self.table)
        #messagebox.showinfo("Success", "Transaction added!")
        self.clear_entries()
        self.refresh_transactions()

    def delete_selected_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No transaction selected!")
            return

        # Get the first selected item
        item_id = selected_item[0]
        values = self.tree.item(item_id, 'values')

        # Assuming the first column is transaction_date, find the transaction id from self.transactions
        # We'll match by date, description, quantity, price, type, total
        for t in self.transactions:
            if (str(t['transaction_date']) == str(values[0]) and
                    t['description'] == values[1] and
                    t['quantity'] == int(values[2]) and
                    float(t['price']) == float(values[3]) and
                    t['transaction_type'] == values[4] and
                    float(t['total']) == float(values[5])):
                transaction_id = t['id']
                break
        else:
            messagebox.showerror("Error", "Transaction not found!")
            return

        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
            return

        delete_transaction(transaction_id, table=self.table)

        messagebox.showinfo("Deleted", "Transaction deleted successfully!")
        self.refresh_transactions()

    def refresh_transactions(self):
        """Load transactions and update treeview and summary"""
        self.clear_treeview()
        self.transactions = read_transactions(table=self.table)
        print("Transactions read from DB:", self.transactions)

        # Insert each transaction into the Treeview
        for t in self.transactions:
            self.tree.insert('', 'end', values=(
                t['transaction_date'],  # use 'transaction_date'
                t['description'],
                t['quantity'],
                float(t['price']),  # convert Decimal to float
                t['transaction_type'],
                float(t['total']),
                t['supplier']
            ))

        summary = TransactionUtils.calculate_summary(self.transactions)
        self.update_summary(
            summary['total_income'],
            summary['total_expense'],
            summary['balance'],
            summary['total_sold_units'],
            summary['avg_price_per_unit']
        )

    def clear_treeview(self):
        for row_item in self.tree.get_children():
            self.tree.delete(row_item)

    def update_summary(self, income, expense, balance, sold_units, avg_price):
        self.lbl_summary.config(
            text=f"Income: {income:.2f}  |  Expenses: {expense:.2f}  |  "
                 f"Balance: {balance:.2f}  |  Units Sold: {sold_units}  |  Avg Price: {avg_price:.2f}"
        )

    def create_filter_frame(self):
        # Create a new frame for filters
        frame = tk.Frame(self.master)
        frame.grid(row=4, column=0, padx=10, pady=5, sticky='w')

        # Year input
        tk.Label(frame, text="Year:").grid(row=0, column=0, sticky='w')
        self.year_var = tk.StringVar()
        self.year_entry = tk.Entry(frame, textvariable=self.year_var, width=6)
        self.year_entry.grid(row=0, column=1, sticky='w')

        # Month input
        tk.Label(frame, text="Month:").grid(row=0, column=2, sticky='w')
        self.month_var = tk.StringVar()
        self.month_entry = tk.Entry(frame, textvariable=self.month_var, width=4)
        self.month_entry.grid(row=0, column=3, sticky='w')

        # Quarter input
        tk.Label(frame, text="Quarter:").grid(row=0, column=4, sticky='w')
        self.quarter_var = tk.StringVar()
        self.quarter_entry = tk.Entry(frame, textvariable=self.quarter_var, width=4)
        self.quarter_entry.grid(row=0, column=5, sticky='w')

        # Filter button
        tk.Button(frame, text="Filter", command=self.filter_transactions).grid(row=0, column=6, padx=5, sticky='w')

    def filter_transactions(self):
        self.transactions = read_transactions(table=self.table)

        year = self.year_var.get()
        month = self.month_var.get()
        quarter = self.quarter_var.get()

        if year:
            transactions = TransactionUtils.filter_by_year(self.transactions, int(year))
        if month:
            transactions = TransactionUtils.filter_by_month(self.transactions, int(year), int(month))
        if quarter:
            transactions = TransactionUtils.filter_by_quarter(self.transactions, int(year), int(quarter))

        self.transactions = transactions
        self.refresh_tree_and_summary()

    def refresh_tree_and_summary(self):
        """Update the Treeview and summary using the current transactions"""
        self.clear_treeview()

        for t in self.transactions:
            self.tree.insert('', 'end', values=(
                t['date'], t['description'], t['quantity'], t['price'], t['transaction_type'], float(t['total'], t['supplier'])
            ))

        from services.utils import TransactionUtils
        summary = TransactionUtils.calculate_summary(self.transactions)

        self.update_summary(
            summary['total_income'],
            summary['total_expense'],
            summary['balance'],
            summary['total_sold_units'],
            summary['avg_price_per_unit']
        )


# ------------------- Root Launcher -------------------
def start_gui(table=TABLE_NAME):
    root = tk.Tk()
    # Make window resizable
    root.rowconfigure(2, weight=1)
    root.columnconfigure(0, weight=1)
    app = TransactionGUI(root, table=table)
    root.mainloop()
