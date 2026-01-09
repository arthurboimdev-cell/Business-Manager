from client.api_client import APIClient
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui.dialogs.materials_dialog import MaterialsDialog

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
        
        tk.Label(frame_general, text="Name:").grid(row=0, column=0, sticky="w")
        self.entry_name = tk.Entry(frame_general, width=25)
        self.entry_name.grid(row=0, column=1, padx=2)
        
        tk.Label(frame_general, text="Desc:").grid(row=0, column=2, sticky="w")
        self.entry_desc = tk.Entry(frame_general, width=25)
        self.entry_desc.grid(row=0, column=3, padx=2)

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

        tk.Button(frame_bom, text="Manage Materials", command=self.open_materials_dialog, font=("Arial", 8)).grid(row=4, column=0, columnspan=4, pady=5)

        # --- 4. Financials ---
        frame_fin = tk.LabelFrame(self.left_panel, text="4. Financials", padx=5, pady=5)
        frame_fin.pack(fill="x", pady=2)
        
        tk.Label(frame_fin, text="Box ($):").pack(side="left")
        self.entry_box = tk.Entry(frame_fin, width=6); self.entry_box.pack(side="left", padx=2)
        
        tk.Label(frame_fin, text="Wrap ($):").pack(side="left")
        self.entry_wrap = tk.Entry(frame_fin, width=6); self.entry_wrap.pack(side="left", padx=2)
        
        self.entry_box.bind("<KeyRelease>", self.calculate_cogs)
        self.entry_wrap.bind("<KeyRelease>", self.calculate_cogs)

        # Action Buttons
        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill="x", pady=10)
        tk.Button(btn_frame, text="Add Product", command=self.add_product, bg="#4CAF50", fg="white").pack(side="left", padx=2)
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
        cols = ("ID", "Name", "Wax", "Fragrance", "Total Cost")
        self.tree = ttk.Treeview(self.right_panel, columns=cols, show="headings")
        self.tree.pack(fill="both", expand=True)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
            
        tk.Button(self.right_panel, text="Delete Selected", command=self.delete_product_gui).pack(pady=5)
        tk.Button(self.right_panel, text="Refresh List", command=self.refresh_products).pack(pady=5)

    def open_materials_dialog(self):
        dlg = MaterialsDialog(self)
        self.wait_window(dlg)
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
        
        def get_mat_cost(name, cat):
            for m in self.materials:
                if m['name'] == name and m['category'] == cat:
                    return float(m['unit_cost'])
            return 0.0

        # 1. Wax
        try:
            wax_g = float(self.entry_wax_g.get() or 0)
            wax_name = self.combo_wax.get()
            unit_cost = get_mat_cost(wax_name, 'wax')
            cost = wax_g * unit_cost
            self.cogs_tree.insert("", "end", values=("Wax", f"{wax_g} g", f"${unit_cost}", f"${cost:.2f}"))
            total_cost += cost
        except ValueError: pass

        # 2. Fragrance
        try:
            frag_g = float(self.entry_fragrance_g.get() or 0)
            frag_name = self.combo_fragrance.get()
            unit_cost = get_mat_cost(frag_name, 'fragrance')
            cost = frag_g * unit_cost
            self.cogs_tree.insert("", "end", values=("Fragrance", f"{frag_g} g", f"${unit_cost}", f"${cost:.2f}"))
            total_cost += cost
        except ValueError: pass

        # 3. Wick
        try:
            wick_name = self.combo_wick.get()
            unit_cost = get_mat_cost(wick_name, 'wick')
            self.cogs_tree.insert("", "end", values=("Wick", "1 unit", f"${unit_cost}", f"${unit_cost:.2f}"))
            total_cost += unit_cost
        except ValueError: pass

        # 4. Container
        try:
            cont_name = self.combo_container.get()
            unit_cost = get_mat_cost(cont_name, 'container')
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
                p.get('id'), p.get('name'), p.get('wax_type'), p.get('fragrance'), f"${(p.get('total_cost') or 0):.2f}"
            ))

    def add_product(self):
        name = self.entry_name.get().strip()
        if not name:
            messagebox.showerror("Error", "Name required")
            return
            
        try:
            total_cost = self.calculate_cogs()
            data = {
                "name": name,
                "description": self.entry_desc.get(),
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
            APIClient.add_product(data)
            messagebox.showinfo("Success", "Product Added")
            self.clear_inputs()
            self.refresh_products()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_product_gui(self):
        selected = self.tree.selection()
        if selected:
            if messagebox.askyesno("Confirm", "Delete?"):
                pid = self.tree.item(selected[0])['values'][0]
                APIClient.delete_product(pid)
                self.refresh_products()

    def clear_inputs(self):
        self.entry_name.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
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
