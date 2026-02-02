import tkinter as tk
import tkinter.font
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from datetime import datetime
from config.config import TREE_COLUMNS, TRANSACTION_TYPES, BUTTON_ADD, BUTTON_CLEAR, UI_LABELS, UI_BUTTONS
from gui.charts import AnalyticsFrame
from gui.tabs.shipping_tab import ShippingTab
from gui.tabs.marketplace_tab import MarketplaceTab

class InputFrame(tb.Frame):
    def __init__(self, parent, transaction_types, on_add, on_clear, on_update):
        super().__init__(parent, padding=10)
        self.on_add = on_add
        self.on_clear = on_clear
        self.on_update = on_update
        self.current_edit_id = None

        self.columnconfigure(1, weight=1)

        self.create_field(UI_LABELS["date"], 0, "date")
        self.create_field(UI_LABELS["date"], 0, "date")
        
        # Set today's date as default
        today = datetime.now().strftime("%Y-%m-%d")
        self.entry_date.insert(0, today)
        
        # Description (now with Product Link)
        tb.Label(self, text=UI_LABELS["description"]).grid(row=1, column=0, sticky='w', pady=5)
        self.entry_desc = tb.Combobox(self)
        self.entry_desc.grid(row=1, column=1, sticky='ew', padx=10, pady=5)
        self.entry_desc.bind("<<ComboboxSelected>>", self._on_product_selected)
        
        self.products = [] # Store list of products for lookup
        self.create_field(UI_LABELS["quantity"], 2, "qty")
        
        # Total Cost (User Input)
        self.create_field("Total Cost ($):", 3, "total")
        
        # Unit Cost (Calculated)
        self.create_field("Unit Cost ($):", 4, "price")
        self.entry_price.configure(state="readonly") # Make read-only

        # Bindings for auto-calculation
        self.entry_qty.bind("<KeyRelease>", self._calculate_unit_cost)
        self.entry_total.bind("<KeyRelease>", self._calculate_unit_cost)

        self.create_field(UI_LABELS["supplier"], 5, "supplier")

        self.type_var = tk.StringVar(value=transaction_types[0])
        lbl = tb.Label(self, text=UI_LABELS["type"])
        lbl.grid(row=6, column=0, sticky='w', pady=5)
        
        radio_frame = tb.Frame(self)
        radio_frame.grid(row=6, column=1, sticky='w')
        for t_type in transaction_types:
            tb.Radiobutton(radio_frame, text=t_type.capitalize(), variable=self.type_var, value=t_type).pack(side='left', padx=5)

        btn_frame = tb.Frame(self)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15, sticky='w')

        self.btn_add = tb.Button(btn_frame, text=BUTTON_ADD, bootstyle="success", command=self._handle_add_or_update)
        self.btn_add.pack(side='left', padx=5)

        tb.Button(btn_frame, text=BUTTON_CLEAR, bootstyle="secondary", command=self.clear_fields).pack(side='left', padx=5)


    def update_products(self, products):
        self.products = products
        # Populate Combobox values with Product titles
        names = [p['title'] for p in products]
        self.entry_desc['values'] = names
        
    def _calculate_unit_cost(self, event=None):
        try:
            qty_val = self.entry_qty.get()
            total_val = self.entry_total.get()
            
            if not qty_val or not total_val:
                return

            qty = float(qty_val)
            total = float(total_val)
            
            if qty > 0:
                unit = total / qty
                self.entry_price.configure(state="normal")
                self.entry_price.delete(0, tk.END)
                self.entry_price.insert(0, f"{unit:.4f}")
                self.entry_price.configure(state="readonly")
        except ValueError:
            pass

    def _on_product_selected(self, event):
        # Auto-fill fields if a product is selected
        selected_name = self.entry_desc.get()
        if not selected_name:
            return
            
        found = next((p for p in self.products if p['title'] == selected_name), None)
        if found:
            pass

    def get_selected_product_id(self):
        name = self.entry_desc.get()
        found = next((p for p in self.products if p['title'] == name), None)
        return found['id'] if found else None

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
            "type": self.type_var.get(),
            "product_id": self.get_selected_product_id()
        }

    def _handle_add_or_update(self):
        data = self.get_data()
        if self.current_edit_id:
            self.on_update(self.current_edit_id, data)
        else:
            self.on_add(data)

    def clear_fields(self):
        self.entry_date.delete(0, tk.END)
        # Restore today's date as default
        today = datetime.now().strftime("%Y-%m-%d")
        self.entry_date.insert(0, today)
        
        self.entry_desc.delete(0, tk.END)
        self.entry_qty.delete(0, tk.END)
        self.entry_total.delete(0, tk.END)
        self.entry_price.configure(state="normal")
        self.entry_price.delete(0, tk.END)
        self.entry_price.configure(state="readonly")
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
        
        # Calculate and set Total and Unit Price
        unit_price = float(data['price'])
        qty = float(data['quantity'])
        if data.get('total') is not None:
            total = float(data['total'])
        else:
            total = unit_price * qty
        
        self.entry_total.insert(0, f"{total:.2f}")
        
        self.entry_price.configure(state="normal")
        self.entry_price.insert(0, str(data['price']))
        self.entry_price.configure(state="readonly")
        if data.get('supplier'):
            self.entry_supplier.insert(0, data['supplier'])
        self.type_var.set(data['transaction_type'])
        # Use dynamic update text
        self.btn_add.configure(text=UI_BUTTONS.get("update", "Update Transaction"), bootstyle="warning")


class TreeFrame(tb.Frame):
    def __init__(self, parent, columns, on_delete, on_edit, on_search, on_export, on_import, on_refresh, on_sort, features=None):
        super().__init__(parent, padding=10)
        self.features = features or {}
        self.on_delete = on_delete
        self.on_edit = on_edit
        self.on_search = on_search
        self.on_export = on_export
        self.on_import = on_import
        self.on_refresh = on_refresh
        self.on_sort = on_sort

        # -- Toolbar --
        toolbar = tb.Frame(self)
        toolbar.pack(fill='x', pady=(0, 10))

        # Search
        if self.features.get("search", True):
            self.search_var = tk.StringVar()
            tb.Label(toolbar, text="Search:").pack(side='left', padx=5)
            self.entry_search = tb.Entry(toolbar, textvariable=self.search_var)
            self.entry_search.pack(side='left', padx=5)
            self.entry_search.bind("<KeyRelease>", lambda e: self._handle_search())
            
        # Refresh
        tb.Button(toolbar, text="Refresh", bootstyle="info-outline", command=self.on_refresh).pack(side='left', padx=10)

        # Import/Export
        # Import
        tb.Button(toolbar, text="Import CSV", bootstyle="warning-outline", command=self.on_import).pack(side='right', padx=5)
        # Export
        if self.features.get("export_csv", True):
            tb.Button(toolbar, text=UI_BUTTONS["export"], bootstyle="success-outline", command=self.on_export).pack(side='right', padx=5)

        # -- Treeview --
        self.tree = tb.Treeview(self, columns=columns, show='headings', bootstyle="primary")
        scrollbar = tb.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        for col in columns:
            self.tree.heading(col, text=col.capitalize(), command=lambda c=col: self.on_sort(c))
            self.tree.column(col, width=100)

        # Context Menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Edit", command=self._handle_edit)
        self.menu.add_command(label="Delete", command=self._handle_delete)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def _handle_search(self):
        query = self.search_var.get()
        self.on_search(query)

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
    def __init__(self, title, theme="superhero", features=None):
        super().__init__(themename=theme)
        self.title(title)
        self.geometry("1100x800")
        self.features = features or {}
        
        # Tabs
        self.notebook = tb.Notebook(self)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Tab 1: Transactions
        self.tab_transactions = tb.Frame(self.notebook)
        self.notebook.add(self.tab_transactions, text="Transactions")

        # Tab 2: Products
        if self.features.get("product_inventory", True):
            self.tab_products = tb.Frame(self.notebook)
            self.notebook.add(self.tab_products, text="Products")

        # Tab 3: Materials (NEW)
        if self.features.get("materials_inventory", True):
            self.tab_materials = tb.Frame(self.notebook)
            self.notebook.add(self.tab_materials, text="Materials")

        # Tab 4: Analytics
        self.tab_analytics = tb.Frame(self.notebook)
        self.notebook.add(self.tab_analytics, text="Analytics")

        # Tab 5: Shipping (NEW)
        if self.features.get("shipping", True):
            self.tab_shipping = ShippingTab(self.notebook)
            self.notebook.add(self.tab_shipping, text="Shipping")

        # Tab 6: Marketplace (NEW)
        if self.features.get("marketplace", True):
            self.tab_marketplace = MarketplaceTab(self.notebook)
            self.notebook.add(self.tab_marketplace, text="Marketplace")

    def hide_analytics_tab(self):
        self.notebook.forget(self.tab_analytics)

