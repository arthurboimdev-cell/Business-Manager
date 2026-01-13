from client.api_client import APIClient
import tkinter as tk
from tkinter import ttk, messagebox
from config.config import DEFAULT_LABOR_RATE

from gui.forms.product_form import ProductForm
from gui.dialogs.create_product_dialog import CreateProductDialog

class ProductsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.products = []
        
        # Configure grid expansion
        self.columnconfigure(1, weight=1) # List area expands
        self.rowconfigure(0, weight=1)

        # Main Layout: Left (Form), Right (List)
        self.left_panel = tk.Frame(self)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.right_panel = tk.Frame(self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Embed Product Form in Left Panel
        self.form = ProductForm(self.left_panel)
        self.form.pack(fill="both", expand=True)

        # Action Buttons (Below Form)
        self.create_action_buttons()
        
        # List View (Right Panel)
        self.create_list_frame()
        self.refresh_product_list()

    def create_action_buttons(self):
        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill="x", pady=10)
        
        tk.Button(btn_frame, text="Create Product", command=self.open_create_dialog, bg="#4CAF50", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="Update Product", command=self.update_product, bg="#FF9800", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="Clear", command=self.form.clear).pack(side="left", padx=2)

    def open_create_dialog(self):
        # Open the popup dialog
        dlg = CreateProductDialog(self, on_success_callback=self.refresh_product_list)
        # dlg.grab_set() # Modal? Optional.

    def update_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No product selected to update")
            return
            
        p_id = self.tree.item(selected[0])['values'][0]
        
        try:
            data = self.form.get_data() # Gets validated data
            
            # API Update
            APIClient.update_product(p_id, data)
            messagebox.showinfo("Success", "Product Updated")
            self.refresh_product_list()
            
            # Verify if image was updated, we might need to refresh local state?
            # get_data encodes the image.
            # If successful, we can reload? Or just assume form state is fine.
            # actually we should probably reload to be safe, but form state is what we just sent.
            
        except ValueError as ve:
             messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
             messagebox.showerror("Error", f"Failed to update product: {e}")

    def create_list_frame(self):
        # Treeview for products
        self.search_frame = tk.Frame(self.right_panel)
        self.search_frame.pack(fill="x", pady=5)
        
        tk.Label(self.search_frame, text="Search ID/SKU:").pack(side="left")
        self.entry_search = tk.Entry(self.search_frame)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<Return>", self.search_by_id)
        tk.Button(self.search_frame, text="Find", command=self.search_by_id).pack(side="left")

        # Treeview
        self.tree = ttk.Treeview(self.right_panel, columns=("ID", "Title", "SKU", "Stock", "Cost", "Price"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Cost", text="Cost")
        self.tree.heading("Price", text="Price")
        
        self.tree.column("ID", width=30)
        self.tree.column("Title", width=150)
        self.tree.column("SKU", width=80)
        self.tree.column("Stock", width=50)
        self.tree.column("Cost", width=60)
        self.tree.column("Price", width=60)
        
        self.tree.pack(fill="both", expand=True, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)
            
        tk.Button(self.right_panel, text="Delete Selected", command=self.delete_product_gui).pack(pady=5)
        tk.Button(self.right_panel, text="Refresh List", command=self.refresh_product_list).pack(pady=5)

    def refresh_product_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.products = APIClient.get_products()
            for product in self.products:
                total_cost = self.calculate_product_cost_static(product)
                
                self.tree.insert("", "end", values=(
                    product.get('id'), 
                    product.get('title'),
                    product.get('sku'),
                    product.get('stock_quantity', 0),
                    f"${total_cost:.2f}",
                    f"${(product.get('selling_price') or 0):.2f}"
                ))
        except Exception as e:
            print(f"Error refreshing list: {e}")

    def on_product_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        p_id = str(self.tree.item(selected[0])['values'][0])
        # Find product in self.products
        product = next((p for p in self.products if str(p['id']) == p_id), None)
        
        if product:
             self.form.load_product(product)

    def delete_product_gui(self):
        selected = self.tree.selection()
        if not selected: return
        
        if messagebox.askyesno("Confirm", "Delete selected product?"):
            try:
                p_id = self.tree.item(selected[0])['values'][0]
                APIClient.delete_product(p_id)
                self.refresh_product_list()
                self.form.clear()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def search_by_id(self, event=None):
        search_term = self.entry_search.get().strip().lower()
        if not search_term: return
        
        # Determine if search term is numeric (for ID)
        is_numeric = search_term.isdigit()
        search_id = int(search_term) if is_numeric else None
        
        # Find in tree items
        found_item = None
        for item in self.tree.get_children():
            vals = self.tree.item(item)['values']
            
            # Check ID match
            if is_numeric and str(vals[0]) == str(search_id):
                found_item = item
                break
            
            # Check SKU Match
            sku = str(vals[2]).lower() if vals[2] else ""
            if search_term == sku:
                found_item = item
                break
                
        if found_item:
            self.tree.selection_set(found_item)
            self.tree.see(found_item)
            self.on_product_select(None)
        else:
            messagebox.showinfo("Not Found", f"Product '{search_term}' not found.")

    @staticmethod
    def calculate_product_cost_static(data):
        """Calculate total COGS from a product dictionary"""
        total = 0.0
        try:
            def get_float(k, d=0.0): return float(data.get(k) or d)
            def get_int(k, d=1): return int(data.get(k) or d)
            
            # 1. Materials
            # Rates for Wax/Fragrance are $/kg, so divide by 1000 for per-gram cost
            total += get_float('wax_weight_g', 0) * (get_float('wax_rate', 0) / 1000.0)
            total += get_float('fragrance_weight_g', 0) * (get_float('fragrance_rate', 0) / 1000.0)
            total += get_int('wick_quantity', 1) * get_float('wick_rate', 0)
            total += get_int('container_quantity', 1) * get_float('container_rate', 0)
            total += get_int('box_quantity', 1) * get_float('box_price', 0)
            total += get_float('wrap_price', 0)
            total += get_float('business_card_cost', 0)
            
            # 2. Labor
            labor_min = get_int('labor_time', 0)
            labor_rate = get_float('labor_rate', 0)
            total += (labor_min / 60.0) * labor_rate
            
        except (ValueError, TypeError):
            pass
        return total
