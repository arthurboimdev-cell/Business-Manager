from tkinter import messagebox
from services.utils import TransactionUtils
from gui.models import TransactionModel
from gui.views import MainWindow, InputFrame, TreeFrame, SummaryFrame
from config.config import TREE_COLUMNS, TRANSACTION_TYPES, WINDOW_TITLE

class TransactionController:
    def __init__(self, table_name):
        self.model = TransactionModel(table_name)
        self.view = MainWindow(WINDOW_TITLE)
        
        # Init Sub-Frames
        # Pass callbacks to views
        self.input_frame = InputFrame(
            self.view, 
            TRANSACTION_TYPES, 
            on_add=self.add_transaction,
            on_clear=None, # handled internally by view usually, but can be explicit
            on_update=self.update_transaction
        )
        self.input_frame.pack(fill='x', padx=10, pady=5)

        self.tree_frame = TreeFrame(
            self.view, 
            TREE_COLUMNS, 
            on_delete=self.prompt_delete_transaction,
            on_edit=self.prep_edit_transaction
        )
        self.tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.summary_frame = SummaryFrame(self.view)
        self.summary_frame.pack(fill='x', padx=10, pady=5)

        # Initial Load
        self.refresh_ui()

    def run(self):
        self.view.mainloop()

    def refresh_ui(self):
        transactions = self.model.get_all_transactions()
        self.tree_frame.clear()
        
        # Populate Tree
        # Store full transaction objects mapping to tree items if needed
        # For now, we rely on the values match
        self.current_transactions_map = {} # Map ID or string rep to transaction object

        for t in transactions:
            # Treeview expects values in specific order of columns
            # Column order from config: ['date', 'description', 'quantity', 'price', 'type', 'total', 'supplier']
            # Keys in DB dict: transaction_date, description, quantity, price, transaction_type, total, supplier
            
            row_values = (
                t['transaction_date'],
                t['description'],
                t['quantity'],
                t['price'],
                t['transaction_type'],
                t['total'],
                t['supplier']
            )
            # Insert and get item ID (not DB ID)
            # We need to be able to find the DB ID from the row values later for editing/deleting
            # A robust way is to hide the ID in tags or a separate map
            # Making a makeshift key string for now, or finding by content (risky if duplicates)
            
            # Better approach: We will search the `transactions` list for the match since we have it fresh
            
            self.tree_frame.insert(row_values)

        # Update Summary
        summary = TransactionUtils.calculate_summary(transactions)
        summary_text = (
            f"Income: {summary['total_income']:.2f}  |  "
            f"Expenses: {summary['total_expense']:.2f}  |  "
            f"Balance: {summary['balance']:.2f}  |  "
            f"Units Sold: {summary['total_sold_units']}"
        )
        self.summary_frame.update_summary(summary_text)


    def add_transaction(self, data):
        try:
            qty = int(data['qty'])
            price = float(data['price'])
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer, Price must be number")
            return

        desc = TransactionUtils.normalize_text(data['desc'])
        supplier = TransactionUtils.normalize_text(data['supplier'])

        self.model.add_transaction(
            data['date'], desc, qty, price, data['type'], supplier
        )
        self.input_frame.clear_fields()
        self.refresh_ui()

    def update_transaction(self, t_id, data):
        try:
            qty = int(data['qty'])
            price = float(data['price'])
        except ValueError:
            messagebox.showerror("Error", "Quantity must be integer, Price must be number")
            return

        desc = TransactionUtils.normalize_text(data['desc'])
        supplier = TransactionUtils.normalize_text(data['supplier'])

        self.model.update_transaction(
            t_id, data['date'], desc, qty, price, data['type'], supplier
        )
        self.input_frame.clear_fields()
        self.refresh_ui()
        messagebox.showinfo("Success", "Transaction Updated")

    def prep_edit_transaction(self, tree_item):
        values = tree_item['values']
        # values list corresponds to columns
        # config columns: date, description, quantity, price, type, total, supplier
        
        # We need the real DB ID. 
        # Strategy: Search in current full list from DB. 
        # CAUTION: If there are exact duplicate rows, this picks the first one. 
        # Ideally, detailed treeview implementation would store ID in `tags` or `iid`.
        # For this refactor, let's implement the search.
        
        transactions = self.model.get_all_transactions()
        found = None
        for t in transactions:
            # Match strict on all visible fields
            if (str(t['transaction_date']) == str(values[0]) and 
                t['description'] == values[1] and 
                str(t['quantity']) == str(values[2]) and
                str(t['price']) == str(values[3]) and # floats might differ in string rep
                t['transaction_type'] == values[4]):
                found = t
                break
        
        if found:
            self.input_frame.load_for_editing(found['id'], found)
        else:
            messagebox.showerror("Error", "Could not locate original record (try refreshing).")

    def prompt_delete_transaction(self, tree_item):
        values = tree_item['values']
        transactions = self.model.get_all_transactions()
        found = None
        for t in transactions:
             if (str(t['transaction_date']) == str(values[0]) and 
                t['description'] == values[1] and 
                str(t['quantity']) == str(values[2]) and
                t['transaction_type'] == values[4]):
                found = t
                break
        
        if found:
            if messagebox.askyesno("Delete", "Are you sure?"):
                self.model.delete_transaction(found['id'])
                self.refresh_ui()
        else:
            messagebox.showerror("Error", "Could not locate record.")
