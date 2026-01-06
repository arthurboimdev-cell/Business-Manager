import tkinter as tk
import tkinter.font
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config.config import TREE_COLUMNS, TRANSACTION_TYPES, BUTTON_ADD, BUTTON_CLEAR, UI_LABELS, UI_BUTTONS
from gui.charts import AnalyticsFrame

class InputFrame(tb.Frame):
    def __init__(self, parent, transaction_types, on_add, on_clear, on_update):
        super().__init__(parent, padding=10)
        self.on_add = on_add
        self.on_clear = on_clear
        self.on_update = on_update
        self.current_edit_id = None

        self.columnconfigure(1, weight=1)

        self.create_field(UI_LABELS["date"], 0, "date")
        self.create_field(UI_LABELS["description"], 1, "desc")
        self.create_field(UI_LABELS["quantity"], 2, "qty")
        self.create_field(UI_LABELS["price"], 3, "price")
        self.create_field(UI_LABELS["supplier"], 4, "supplier")

        self.type_var = tk.StringVar(value=transaction_types[0])
        lbl = tb.Label(self, text=UI_LABELS["type"])
        lbl.grid(row=5, column=0, sticky='w', pady=5)
        
        radio_frame = tb.Frame(self)
        radio_frame.grid(row=5, column=1, sticky='w')
        for t_type in transaction_types:
            tb.Radiobutton(radio_frame, text=t_type.capitalize(), variable=self.type_var, value=t_type).pack(side='left', padx=5)

        btn_frame = tb.Frame(self)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15, sticky='w')

        self.btn_add = tb.Button(btn_frame, text=BUTTON_ADD, bootstyle="success", command=self._handle_add_or_update)
        self.btn_add.pack(side='left', padx=5)

        tb.Button(btn_frame, text=BUTTON_CLEAR, bootstyle="secondary", command=self.clear_fields).pack(side='left', padx=5)

    def create_field(self, label, row, var_name):
        tb.Label(self, text=label).grid(row=row, column=0, sticky='w', pady=5)
        entry = tb.Entry(self)
        entry.grid(row=row, column=1, sticky='ew', padx=10, pady=5)
        setattr(self, f"entry_{var_name}", entry)

    def get_data(self):
        return {
            "date": self.entry_date.get(),
            "desc": self.entry_desc.get(),
            "qty": self.entry_qty.get(),
            "price": self.entry_price.get(),
            "supplier": self.entry_supplier.get(),
            "type": self.type_var.get()
        }

    def _handle_add_or_update(self):
        data = self.get_data()
        if self.current_edit_id:
            self.on_update(self.current_edit_id, data)
        else:
            self.on_add(data)

    def clear_fields(self):
        self.entry_date.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_supplier.delete(0, tk.END)
        self.type_var.set(TRANSACTION_TYPES[0])
        self.current_edit_id = None
        self.btn_add.configure(text=BUTTON_ADD, bootstyle="success")

    def load_for_editing(self, t_id, data):
        self.clear_fields()
        self.current_edit_id = t_id
        self.entry_date.insert(0, data['transaction_date'])
        self.entry_desc.insert(0, data['description'])
        self.entry_qty.insert(0, str(data['quantity']))
        self.entry_price.insert(0, str(data['price']))
        if data.get('supplier'):
            self.entry_supplier.insert(0, data['supplier'])
        self.type_var.set(data['transaction_type'])
        # Use dynamic update text
        self.btn_add.configure(text=UI_BUTTONS.get("update", "Update Transaction"), bootstyle="warning")


class TreeFrame(tb.Frame):
    def __init__(self, parent, columns, on_delete, on_edit, on_search, on_export):
        super().__init__(parent, padding=10)
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.on_search = on_search
        self.on_export = on_export

        # -- Toolbar --
        toolbar = tb.Frame(self)
        toolbar.pack(fill='x', pady=(0, 10))

        # Search
        self.search_var = tk.StringVar()
        tb.Label(toolbar, text="Search:").pack(side='left', padx=5)
        tb.Entry(toolbar, textvariable=self.search_var).pack(side='left', padx=5)
        tb.Button(toolbar, text=UI_BUTTONS["filter"], bootstyle="info-outline", command=self._handle_search).pack(side='left', padx=5)
        tb.Button(toolbar, text=UI_BUTTONS["reset"], bootstyle="secondary-outline", command=self._handle_reset).pack(side='left', padx=5)

        # Export
        tb.Button(toolbar, text=UI_BUTTONS["export"], bootstyle="success-outline", command=self.on_export).pack(side='right', padx=5)

        # -- Treeview --
        self.tree = tb.Treeview(self, columns=columns, show='headings', bootstyle="primary")
        scrollbar = tb.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100)

        # Context Menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Edit", command=self._handle_edit)
        self.menu.add_command(label="Delete", command=self._handle_delete)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def _handle_search(self):
        query = self.search_var.get()
        self.on_search(query)

    def _handle_reset(self):
        self.search_var.set("")
        self.on_search("")

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def _handle_edit(self):
        selected = self.tree.selection()
        if selected:
            self.on_edit(self.tree.item(selected[0]))

    def _handle_delete(self):
        selected = self.tree.selection()
        if selected:
            self.on_delete(self.tree.item(selected[0]))

    def clear(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def insert(self, values):
        self.tree.insert('', 'end', values=values)

    def autosize_columns(self):
        """Automatically adjust column widths based on content"""
        # Dictionary to store max width for each column (start with header width)
        col_widths = {}
        for col in self.tree['columns']:
            col_widths[col] = tk.font.Font().measure(col.title()) + 20

        # Iterate through all items to find max width
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            for i, col in enumerate(self.tree['columns']):
                # Measure text width
                val_width = tk.font.Font().measure(str(values[i])) + 20
                if val_width > col_widths[col]:
                    col_widths[col] = val_width

        # Apply new widths
        for col, width in col_widths.items():
            # Cap width at 400 to prevent overly wide columns
            self.tree.column(col, width=min(width, 400))

class SummaryFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10, bootstyle="info")
        self.lbl_text = tb.Label(self, text="Summary", font=("Helvetica", 10, "bold"), bootstyle="inverse-info")
        self.lbl_text.pack(fill='both', padx=5, pady=5)

    def update_summary(self, text):
        self.lbl_text.config(text=text)


class MainWindow(tb.Window):
    def __init__(self, title, theme="superhero"):
        super().__init__(themename=theme)
        self.title(title)
        self.geometry("1100x800")
        
        # Tabs
        self.notebook = tb.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Transactions
        self.tab_transactions = tb.Frame(self.notebook)
        self.notebook.add(self.tab_transactions, text="Transactions")

        # Tab 2: Analytics
        self.tab_analytics = tb.Frame(self.notebook)
        self.notebook.add(self.tab_analytics, text="Analytics")

