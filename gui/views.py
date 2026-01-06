import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config.config import TREE_COLUMNS, TRANSACTION_TYPES, BUTTON_ADD, BUTTON_REFRESH, BUTTON_CLEAR

class InputFrame(tb.Frame):
    def __init__(self, parent, transaction_types, on_add, on_clear, on_update):
        super().__init__(parent, padding=10)
        self.on_add = on_add
        self.on_clear = on_clear
        self.on_update = on_update
        self.current_edit_id = None  # If not None, we are in Edit mode

        # Grid Layout
        self.columnconfigure(1, weight=1)

        # Fields
        self.create_field("Date (YYYY-MM-DD):", 0, "date")
        self.create_field("Description:", 1, "desc")
        self.create_field("Quantity:", 2, "qty")
        self.create_field("Price:", 3, "price")
        self.create_field("Supplier:", 4, "supplier")

        # Type (Radio)
        self.type_var = tk.StringVar(value=transaction_types[0])
        lbl = tb.Label(self, text="Type:")
        lbl.grid(row=5, column=0, sticky='w', pady=5)
        
        radio_frame = tb.Frame(self)
        radio_frame.grid(row=5, column=1, sticky='w')
        for t_type in transaction_types:
            tb.Radiobutton(radio_frame, text=t_type.capitalize(), variable=self.type_var, value=t_type).pack(side='left', padx=5)

        # Buttons
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
        
        # Exit edit mode
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

        self.btn_add.configure(text="Update Transaction", bootstyle="warning")


class TreeFrame(tb.Frame):
    def __init__(self, parent, columns, on_delete, on_edit):
        super().__init__(parent, padding=10)
        self.on_delete = on_delete
        self.on_edit = on_edit

        # Treeview
        self.tree = tb.Treeview(self, columns=columns, show='headings', bootstyle="primary")
        
        # Scrollbar
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
        self.geometry("1000x700")
