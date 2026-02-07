from client.api_client import APIClient
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config.config import DEFAULT_LABOR_RATE
import threading

from gui.forms.product_form import ProductForm
from gui.dialogs.create_product_dialog import CreateProductDialog
from services.etsy_import import import_etsy_products


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
        tk.Button(btn_frame, text="Import from Etsy CSV", command=self.import_from_etsy, bg="#2196F3", fg="white").pack(side="left", padx=2)


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
            print("Fetching products from API...")
            self.products = APIClient.get_products()
            print(f"Received {len(self.products)} products from API")
            
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
            print(f"Displayed {len(self.products)} products in tree")
        except Exception as e:
            print(f"Error refreshing list: {e}")
            import traceback
            traceback.print_exc()

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
        if not selected:
            messagebox.showwarning("Warning", "No products selected to delete")
            return
        
        # Get count of selected items
        count = len(selected)
        item_text = "product" if count == 1 else "products"
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", f"Delete {count} {item_text}?"):
            return
        
        try:
            # Delete all selected products
            for item in selected:
                p_id = self.tree.item(item)['values'][0]
                APIClient.delete_product(p_id)
            
            # Show success message
            messagebox.showinfo("Success", f"Deleted {count} {item_text}")
            
            # Refresh list in background
            self.after(100, self.refresh_product_list)
            
            # Clear form
            self.form.clear()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete products: {e}")


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

    def import_from_etsy(self):
        """Import products from Etsy CSV file with progress dialog."""
        # Open file dialog
        csv_path = filedialog.askopenfilename(
            title="Select Etsy CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
        if not csv_path:
            return  # User cancelled
        
        # Create progress dialog
        progress_window = tk.Toplevel(self)
        progress_window.title("Importing Products")
        progress_window.geometry("400x150")
        progress_window.transient(self)
        progress_window.grab_set()
        
        # Center the window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (progress_window.winfo_width() // 2)
        y = (progress_window.winfo_screenheight() // 2) - (progress_window.winfo_height() // 2)
        progress_window.geometry(f"+{x}+{y}")
        
        # Progress label
        status_label = tk.Label(progress_window, text="Starting import...", wraplength=380)
        status_label.pack(pady=20)
        
        # Progress bar
        progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=350)
        progress_bar.pack(pady=10)
        
        # Result container
        result = {'stats': None, 'error': None}
        
        def progress_callback(current, total, message):
            """Update progress bar and status label."""
            progress_bar['value'] = (current / total) * 100
            status_label.config(text=message)
            progress_window.update()
        
        def do_import():
            """Run import in background thread."""
            try:
                stats = import_etsy_products(csv_path, progress_callback)
                result['stats'] = stats
            except Exception as e:
                result['error'] = str(e)
        
        # Run import in thread
        import_thread = threading.Thread(target=do_import, daemon=True)
        import_thread.start()
        
        # Wait for thread to complete
        while import_thread.is_alive():
            progress_window.update()
            self.after(100)
        
        # Close progress window
        progress_window.destroy()
        
        # Show results
        if result['error']:
            messagebox.showerror("Import Error", f"Failed to import products:\n{result['error']}")
        elif result['stats']:
            stats = result['stats']
            message = (
                f"Import Complete!\n\n"
                f"✓ Imported: {stats['imported']} products\n"
                f"⊘ Skipped (duplicates): {stats['skipped_duplicates']}\n"
                f"✗ Skipped (errors): {stats['skipped_errors']}"
            )
            messagebox.showinfo("Import Results", message)
        
        # Force immediate refresh of product list
        try:
            self.refresh_product_list()
            print(f"Products refreshed: {len(self.products)} products in list")
        except Exception as refresh_error:
            print(f"Error refreshing after import: {refresh_error}")
            messagebox.showwarning("Refresh Issue", f"Products imported successfully but list refresh failed. Please click 'Refresh List' manually.\n\nError: {refresh_error}")


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
