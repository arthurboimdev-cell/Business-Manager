from client.api_client import APIClient
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# Try to import PIL for image handling
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class ProductsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.products = []
        self.materials = []
        self.image_data = None # Holds bytes
        
        # Configure grid expansion
        self.columnconfigure(1, weight=1) # List area expands
        self.rowconfigure(0, weight=1)

        # Main Layout: Left (Inputs/Calc), Right (List)
        self.left_panel = tk.Frame(self)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.right_panel = tk.Frame(self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.create_input_sections()
        self.create_cogs_table() # Bottom of left panel
        self.create_list_frame()
        
        self.refresh_prods_and_mats()

    def create_input_sections(self):
        # --- 1. General Info ---
        frame_general = tk.LabelFrame(self.left_panel, text="1. General Info", padx=5, pady=5)
        frame_general.pack(fill="x", pady=2)
        
        # Product ID (Searchable)
        tk.Label(frame_general, text="ID:").grid(row=0, column=0, sticky="w")
        self.entry_id = tk.Entry(frame_general, width=10)
        self.entry_id.grid(row=0, column=1, padx=2, sticky="w")
        self.entry_id.bind("<Return>", self.search_by_id)
        tk.Button(frame_general, text="Find", command=self.search_by_id, font=("Arial", 8)).grid(row=0, column=2, padx=2)

        tk.Label(frame_general, text="Name:").grid(row=1, column=0, sticky="w")
        self.entry_name = tk.Entry(frame_general, width=25)
        self.entry_name.grid(row=1, column=1, columnspan=2, padx=2, sticky="w")
        
        tk.Label(frame_general, text="Desc:").grid(row=2, column=0, sticky="w")
        self.entry_desc = tk.Entry(frame_general, width=25)
        self.entry_desc.grid(row=2, column=1, columnspan=2, padx=2, sticky="w")
        
        # SKU / UPC
        tk.Label(frame_general, text="SKU:").grid(row=3, column=0, sticky="w")
        self.entry_sku = tk.Entry(frame_general, width=12)
        self.entry_sku.grid(row=3, column=1, sticky="w", padx=2)
        
        tk.Label(frame_general, text="UPC:").grid(row=3, column=2, sticky="w")
        self.entry_upc = tk.Entry(frame_general, width=12)
        self.entry_upc.grid(row=3, column=3, sticky="w", padx=2)
        
        tk.Label(frame_general, text="Units in stock:").grid(row=4, column=0, sticky="w", pady=2)
        self.entry_stock = tk.Entry(frame_general, width=10)
        self.entry_stock.grid(row=4, column=1, sticky="w", padx=2, pady=2)

        # --- 2. Physical Specs ---
        frame_specs = tk.LabelFrame(self.left_panel, text="2. Physical Specs", padx=5, pady=5)
        frame_specs.pack(fill="x", pady=2)
        
        tk.Label(frame_specs, text="Size (L/W/H cm):").pack(side="left")
        self.entry_l = tk.Entry(frame_specs, width=5); self.entry_l.pack(side="left", padx=2)
        self.entry_w = tk.Entry(frame_specs, width=5); self.entry_w.pack(side="left", padx=2)
        self.entry_h = tk.Entry(frame_specs, width=5); self.entry_h.pack(side="left", padx=2)
        
        tk.Label(frame_specs, text="Total Weight (g):").pack(side="left", padx=5)
        self.entry_weight = tk.Entry(frame_specs, width=8)
        self.entry_weight.pack(side="left")

        # --- 3. Bill of Materials (BOM) ---
        frame_bom = tk.LabelFrame(self.left_panel, text="3. Bill of Materials", padx=5, pady=5)
        frame_bom.pack(fill="x", pady=2)
        
        # Grid for BOM
        # Wax
        tk.Label(frame_bom, text="Wax:").grid(row=0, column=0, sticky="w")
        self.combo_wax = ttk.Combobox(frame_bom, width=15)
        self.combo_wax.grid(row=0, column=1, padx=2)
        tk.Label(frame_bom, text="g:").grid(row=0, column=2, sticky="w")
        self.entry_wax_g = tk.Entry(frame_bom, width=6)
        self.entry_wax_g.grid(row=0, column=3, padx=2)
        self.entry_wax_g.bind("<KeyRelease>", self.calculate_cogs)
        self.combo_wax.bind("<<ComboboxSelected>>", self.calculate_cogs)

        # Fragrance
        tk.Label(frame_bom, text="Fragrance:").grid(row=1, column=0, sticky="w")
        self.combo_fragrance = ttk.Combobox(frame_bom, width=15)
        self.combo_fragrance.grid(row=1, column=1, padx=2)
        tk.Label(frame_bom, text="g:").grid(row=1, column=2, sticky="w")
        self.entry_fragrance_g = tk.Entry(frame_bom, width=6)
        self.entry_fragrance_g.grid(row=1, column=3, padx=2)
        self.entry_fragrance_g.bind("<KeyRelease>", self.calculate_cogs)
        self.combo_fragrance.bind("<<ComboboxSelected>>", self.calculate_cogs)

        # Wick
        tk.Label(frame_bom, text="Wick:").grid(row=2, column=0, sticky="w")
        self.combo_wick = ttk.Combobox(frame_bom, width=15)
        self.combo_wick.grid(row=2, column=1, padx=2)
        self.combo_wick.bind("<<ComboboxSelected>>", self.calculate_cogs)

        # Container
        tk.Label(frame_bom, text="Container:").grid(row=3, column=0, sticky="w")
        self.combo_container = ttk.Combobox(frame_bom, width=15)
        self.combo_container.grid(row=3, column=1, padx=2)
        self.combo_container.bind("<<ComboboxSelected>>", self.calculate_cogs)
        
        # Box & Wrap (Moved to BOM)
        tk.Label(frame_bom, text="Box ($):").grid(row=4, column=0, sticky="w")
        self.entry_box = tk.Entry(frame_bom, width=6)
        self.entry_box.grid(row=4, column=1, padx=2, sticky="w")
        
        tk.Label(frame_bom, text="Wrap ($):").grid(row=4, column=2, sticky="w")
        self.entry_wrap = tk.Entry(frame_bom, width=6)
        self.entry_wrap.grid(row=4, column=3, padx=2, sticky="w")
        
        self.entry_box.bind("<KeyRelease>", self.calculate_cogs)
        self.entry_wrap.bind("<KeyRelease>", self.calculate_cogs)

        # Action Buttons
        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="Add Product", command=self.add_product, bg="#4CAF50", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="Update Product", command=self.update_product, bg="#FF9800", fg="white").pack(side="left", padx=2)
        tk.Button(btn_frame, text="Clear", command=self.clear_inputs).pack(side="left", padx=2)
        tk.Button(btn_frame, text="Select Image", command=self.select_image).pack(side="left", padx=2)
        self.lbl_image_status = tk.Label(btn_frame, text="")
        self.lbl_image_status.pack(side="left", padx=2)

    def create_cogs_table(self):
        lbl_frame = tk.LabelFrame(self.left_panel, text="COGS Calculator", padx=5, pady=5)
        lbl_frame.pack(fill="both", expand=True)

        cols = ("Component", "Amount", "Unit Cost", "Total")
        self.cogs_tree = ttk.Treeview(lbl_frame, columns=cols, show="headings", height=8)
        self.cogs_tree.pack(fill="both", expand=True)

        for col in cols:
            self.cogs_tree.heading(col, text=col)
            self.cogs_tree.column(col, width=60)
            
        # Total Label
        self.lbl_total_cogs = tk.Label(lbl_frame, text="TOTAL COGS: $0.00", font=("Arial", 12, "bold"), fg="blue")
        self.lbl_total_cogs.pack(anchor="e", pady=5)

    def create_list_frame(self):
        cols = ("ID", "Name", "Stock", "Wax", "Fragrance", "Total Cost")
        self.tree = ttk.Treeview(self.right_panel, columns=cols, show="headings")
        self.tree.pack(fill="both", expand=True)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
            
        self.tree.bind("<<TreeviewSelect>>", self.on_product_select)
            
        tk.Button(self.right_panel, text="Delete Selected", command=self.delete_product_gui).pack(pady=5)
        tk.Button(self.right_panel, text="Refresh List", command=self.refresh_products).pack(pady=5)

    def open_materials_dialog(self):
        # Deprecated logic removed, using MaterialsTab instead
        MaterialsDialog(self)
        self.refresh_prods_and_mats()

    def refresh_prods_and_mats(self):
        self.refresh_products()
        self.refresh_materials_dropdowns()

    def refresh_materials_dropdowns(self):
        self.materials = APIClient.get_materials()
        
        waxes = [m['name'] for m in self.materials if m['category'] == 'wax']
        wicks = [m['name'] for m in self.materials if m['category'] == 'wick']
        frags = [m['name'] for m in self.materials if m['category'] == 'fragrance']
        conts = [m['name'] for m in self.materials if m['category'] == 'container']
        
        self.combo_wax['values'] = waxes
        self.combo_wick['values'] = wicks
        self.combo_fragrance['values'] = frags
        self.combo_container['values'] = conts

    def calculate_cogs(self, event=None):
        # Clear table
        for item in self.cogs_tree.get_children():
            self.cogs_tree.delete(item)
            
        total_cost = 0.0
        
        def get_mat_info(name, cat):
            for m in self.materials:
                if m['name'] == name and m['category'] == cat:
                    return float(m['unit_cost']), m.get('unit_type', '').lower()
            return 0.0, ""

        # 1. Wax
        try:
            wax_g = float(self.entry_wax_g.get() or 0)
            wax_name = self.combo_wax.get()
            unit_cost, unit_type = get_mat_info(wax_name, 'wax')
            
            # Handle KG conversion
            if unit_type in ['kg', 'kilogram', 'kgs']:
                cost = (wax_g / 1000) * unit_cost
                unit_label = f"${unit_cost}/kg"
            else:
                cost = wax_g * unit_cost
                unit_label = f"${unit_cost}"

            self.cogs_tree.insert("", "end", values=("Wax", f"{wax_g} g", unit_label, f"${cost:.2f}"))
            total_cost += cost
        except ValueError: pass

        # 2. Fragrance
        try:
            frag_g = float(self.entry_fragrance_g.get() or 0)
            frag_name = self.combo_fragrance.get()
            unit_cost, unit_type = get_mat_info(frag_name, 'fragrance')
            
            # Handle KG conversion
            if unit_type in ['kg', 'kilogram', 'kgs']:
                cost = (frag_g / 1000) * unit_cost
                unit_label = f"${unit_cost}/kg"
            else:
                cost = frag_g * unit_cost
                unit_label = f"${unit_cost}"

            self.cogs_tree.insert("", "end", values=("Fragrance", f"{frag_g} g", unit_label, f"${cost:.2f}"))
            total_cost += cost
        except ValueError: pass

        # 3. Wick
        try:
            wick_name = self.combo_wick.get()
            unit_cost, _ = get_mat_info(wick_name, 'wick')
            self.cogs_tree.insert("", "end", values=("Wick", "1 unit", f"${unit_cost}", f"${unit_cost:.2f}"))
            total_cost += unit_cost
        except ValueError: pass

        # 4. Container
        try:
            cont_name = self.combo_container.get()
            unit_cost, _ = get_mat_info(cont_name, 'container')
            self.cogs_tree.insert("", "end", values=("Container", "1 unit", f"${unit_cost}", f"${unit_cost:.2f}"))
            total_cost += unit_cost
        except ValueError: pass
        
        # 5. Box & Wrap
        try:
            box = float(self.entry_box.get() or 0)
            if box > 0:
                self.cogs_tree.insert("", "end", values=("Box/Pkg", "1 unit", f"${box}", f"${box:.2f}"))
                total_cost += box
                
            wrap = float(self.entry_wrap.get() or 0)
            if wrap > 0:
                self.cogs_tree.insert("", "end", values=("Label/Wrap", "1 unit", f"${wrap}", f"${wrap:.2f}"))
                total_cost += wrap
        except ValueError: pass

        self.lbl_total_cogs.config(text=f"TOTAL COGS: ${total_cost:.2f}")
        return total_cost

    def refresh_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.products = APIClient.get_products()
        for p in self.products:
            self.tree.insert("", "end", values=(
                p.get('id'), p.get('name'), p.get('stock_quantity', 0), p.get('wax_type'), p.get('fragrance'), f"${(p.get('total_cost') or 0):.2f}"
            ))

    def add_product(self):
        self._save_product(is_update=False)

    def update_product(self):
        self._save_product(is_update=True)

    def _save_product(self, is_update):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Name required")
            return
            
        try:
            total_cost = self.calculate_cogs()
            data = {
                "name": name,
                "sku": self.entry_sku.get().strip(),
                "upc": self.entry_upc.get().strip(),
                "description": self.entry_desc.get(),
                "stock_quantity": int(self.entry_stock.get() or 0),
                "length_cm": float(self.entry_l.get() or 0),
                "width_cm": float(self.entry_w.get() or 0),
                "height_cm": float(self.entry_h.get() or 0),
                "weight_g": float(self.entry_weight.get() or 0),
                "wax_type": self.combo_wax.get(),
                "wax_weight_g": float(self.entry_wax_g.get() or 0),
                "fragrance_weight_g": float(self.entry_fragrance_g.get() or 0),
                "wick_type": self.combo_wick.get(),
                "container_type": self.combo_container.get(),
                "box_price": float(self.entry_box.get() or 0),
                "wrap_price": float(self.entry_wrap.get() or 0),
                "total_cost": total_cost,
                "image": self.image_data
            }
            
            if is_update:
                selected = self.tree.selection()
                if not selected:
                    messagebox.showwarning("Warning", "No product selected to update")
                    return
                p_id = self.tree.item(selected[0])['values'][0]
                APIClient.update_product(p_id, data)
                messagebox.showinfo("Success", "Product Updated")
            else:
                APIClient.add_product(data)
                messagebox.showinfo("Success", "Product Added")
                
            self.clear_inputs()
            self.refresh_products()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_by_id(self, event=None):
        search_id = self.entry_id.get().strip()
        if not search_id: return
        
        # Determine if numeric
        if not search_id.isdigit():
            messagebox.showerror("Error", "ID must be a number")
            return
            
        search_id = int(search_id)
        
        # Find in tree items
        found_item = None
        for item in self.tree.get_children():
            vals = self.tree.item(item)['values']
            if vals[0] == search_id:
                found_item = item
                break
        
        if found_item:
            self.tree.selection_set(found_item)
            self.tree.see(found_item)
            # The selection event will trigger population, but we can force it or let event handle it
            # The event binding might not trigger if set programmatically depending on Tk version/OS
            # Let's call select handler manually to be safe or rely on event. 
            # Usually selection_set triggers <<TreeviewSelect>> in some frameworks but Tcl/Tk often doesn't.
            # We'll call on_product_select manualy via a fake event or direct logic? 
            # actually better to just call logic directly.
            self.on_product_select(None)
        else:
            messagebox.showinfo("Not Found", f"Product ID {search_id} not found.")

    def on_product_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        p_id = self.tree.item(selected[0])['values'][0]
        # Find product in self.products
        product = next((p for p in self.products if p['id'] == p_id), None)
        
        if product:
            self.clear_inputs()
            self.entry_id.insert(0, str(p_id))
            self.entry_name.insert(0, product.get('name', ''))
            self.entry_sku.insert(0, product.get('sku') or '')
            self.entry_upc.insert(0, product.get('upc') or '')
            self.entry_desc.insert(0, product.get('description') or '')
            self.entry_stock.insert(0, str(product.get('stock_quantity', 0)))
            self.entry_l.insert(0, str(product.get('length_cm', 0)))
            self.entry_w.insert(0, str(product.get('width_cm', 0)))
            self.entry_h.insert(0, str(product.get('height_cm', 0)))
            self.entry_weight.insert(0, str(product.get('weight_g', 0)))
            
            self.combo_wax.set(product.get('wax_type') or '')
            self.entry_wax_g.insert(0, str(product.get('wax_weight_g', 0)))
            
            self.combo_fragrance.set('') # Logic to get frag name if stored? Currently stored in product?
            # Note: Previously we didn't seem to store frag_type explicitly in schema? 
            # Check schema: no 'fragrance_type' column! Just 'fragrance_weight_g'.
            # Wait, list view shows "Fragrance"? 
            # Let's check refresh_products list values: p.get('fragrance') ??
            # Schema has NO fragrance column. It has 'fragrance_weight_g'.
            # The list view in refresh_products uses p.get('fragrance'), which likely returns None/Null if not in DB.
            # I should verify if I wanted to store the fragrance NAME.
            # The input stores Fragrance Weight.
            
            self.entry_fragrance_g.insert(0, str(product.get('fragrance_weight_g', 0)))
            self.combo_wick.set(product.get('wick_type') or '')
            self.combo_container.set(product.get('container_type') or '')
            self.entry_box.insert(0, str(product.get('box_price', 0)))
            self.entry_wrap.insert(0, str(product.get('wrap_price', 0)))
            
            # Recalculate COGS based on loaded values
            self.calculate_cogs()

    def delete_product_gui(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Confirm", "Delete?"):
                pid = self.tree.item(selected[0])['values'][0]
                APIClient.delete_product(pid)
                self.refresh_products()

    def clear_inputs(self):
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.entry_sku.delete(0, tk.END)
        self.entry_upc.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.entry_stock.delete(0, tk.END)
        self.entry_l.delete(0, tk.END)
        self.entry_w.delete(0, tk.END)
        self.entry_h.delete(0, tk.END)
        self.entry_weight.delete(0, tk.END)
        self.combo_wax.set('')
        self.entry_wax_g.delete(0, tk.END)
        self.combo_fragrance.set('')
        self.entry_fragrance_g.delete(0, tk.END)
        self.combo_wick.set('')
        self.combo_container.set('')
        self.entry_box.delete(0, tk.END)
        self.entry_wrap.delete(0, tk.END)
        self.calculate_cogs()

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png")])
        if file_path:
            with open(file_path, "rb") as f:
                self.image_data = f.read()
            self.lbl_image_status.config(text="Image Loaded")
