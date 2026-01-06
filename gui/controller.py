from tkinter import messagebox, filedialog
from services.utils import TransactionUtils
from services.data_service import DataService
from gui.models import TransactionModel
from gui.views import MainWindow, InputFrame, TreeFrame, SummaryFrame
from gui.charts import AnalyticsFrame
from config.config import TREE_COLUMNS, TRANSACTION_TYPES, WINDOW_TITLE

class TransactionController:
    def __init__(self, table_name):
        self.model = TransactionModel(table_name)
        self.view = MainWindow(WINDOW_TITLE)
        
        # --- Tab 1: Transactions ---
        self.input_frame = InputFrame(
            self.view.tab_transactions, 
            TRANSACTION_TYPES, 
            on_add=self.add_transaction,
            on_clear=None, 
            on_update=self.update_transaction
        )
        self.input_frame.pack(fill='x', padx=10, pady=5)

        self.tree_frame = TreeFrame(
            self.view.tab_transactions, 
            TREE_COLUMNS, 
            on_delete=self.prompt_delete_transaction,
            on_edit=self.prep_edit_transaction,
            on_search=self.filter_transactions,
            on_export=self.export_csv,
            on_sort=self.sort_transactions
        )
        self.tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.summary_frame = SummaryFrame(self.view.tab_transactions)
        self.summary_frame.pack(fill='x', padx=10, pady=5)

        # --- Tab 2: Analytics ---
        self.analytics_frame = AnalyticsFrame(self.view.tab_analytics)
        self.analytics_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # UI State
        self.current_search_query = ""
        # Default sort: Date Descending
        self.sort_col = "date"
        self.sort_reverse = True

        # Map UI columns to DB/Model keys
        self.COLUMN_MAP = {
            "date": "transaction_date",
            "description": "description",
            "quantity": "quantity",
            "price": "price",
            "type": "transaction_type",
            "supplier": "supplier",
            "total": "total"
        }

        # Initial Load
        self.refresh_ui()

    def run(self):
        self.view.mainloop()

    def filter_transactions(self, query):
        self.current_search_query = query.lower().strip()
        self.refresh_ui()

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            DataService.export_to_csv(filename, self.model.get_all_transactions())
            messagebox.showinfo("Success", f"Exported to {filename}")

    def refresh_ui(self):
        all_transactions = self.model.get_all_transactions()
        
        # Filter if search is active
        if self.current_search_query:
            display_transactions = [
                t for t in all_transactions
                if self.current_search_query in t['description'].lower() or 
                   (t['supplier'] and self.current_search_query in t['supplier'].lower())
            ]
        else:
            display_transactions = all_transactions

        # Sort
        if self.sort_col:
            sort_key = self.COLUMN_MAP.get(self.sort_col, self.sort_col)
            display_transactions.sort(
                key=lambda x: x[sort_key] if x[sort_key] is not None else "",
                reverse=self.sort_reverse
            )

        self.tree_frame.clear()
        
        for t in display_transactions:
            row_values = (
                t['transaction_date'],
                t['description'],
                t['quantity'],
                t['price'],
                t['transaction_type'],
                t['total'],
                t['supplier']
            )
            self.tree_frame.insert(row_values)
        
        self.tree_frame.autosize_columns()

        # Update Summary
        summary = TransactionUtils.calculate_summary(display_transactions)
        summary_text = (
            f"Income: {summary['total_income']:.2f}  |  "
            f"Expenses: {summary['total_expense']:.2f}  |  "
            f"Balance: {summary['balance']:.2f}  |  "
            f"Units Sold: {summary['total_sold_units']}"
        )
        self.summary_frame.update_summary(summary_text)

        # Update Charts (Always use All Transactions or Filtered? Ideally Filtered matches view)
        self.analytics_frame.refresh_charts(display_transactions)


    def sort_transactions(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        
        self.refresh_ui()


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
        # We search in ALL transactions to find the ID, even if filtered view
        transactions = self.model.get_all_transactions()
        found = None
        for t in transactions:
            if (str(t['transaction_date']) == str(values[0]) and 
                t['description'] == values[1] and 
                str(t['quantity']) == str(values[2]) and
                str(t['price']) == str(values[3]) and 
                t['transaction_type'] == values[4]):
                found = t
                break
        
        if found:
            # Switch to Tab 1 if needed (though Edit is on Tab 1)
            self.input_frame.load_for_editing(found['id'], found)
        else:
            messagebox.showerror("Error", "Could not locate original record.")

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
                # Clear search if deleting to avoid confusion? No, keep context.
                self.refresh_ui()
        else:
            messagebox.showerror("Error", "Could not locate record.")
