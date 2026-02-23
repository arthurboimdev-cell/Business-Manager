from client.api_client import APIClient
import copy
import base64
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config.config import DEFAULT_LABOR_RATE, UI_LABELS, BUTTON_ADD, BUTTON_UPDATE, BUTTON_CLEAR
from services.shipping_service import format_shipping_summary, get_cheapest_by_destination

import io
import uuid

# Try to import PIL for image handling
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

class ProductForm(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.image_data = None # Holds specific image being uploaded (bytes)
        self.pending_gallery_images = [] # List of pending images for new product
        self.current_product_id = None # Track ID if editing existing product

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Tabbed Interface
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)
        
        self.tab_core = tk.Frame(self.notebook)
        self.tab_bom = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_core, text="Core Info")
        self.notebook.add(self.tab_bom, text="Manufacturing (BOM)")

        self.create_core_tab()
        self.create_bom_tab()

    def create_core_tab(self):
        # Top Container for General Info (Left) and Image Preview (Right)
        parent = self.tab_core
        frame_top = tk.Frame(parent)
        frame_top.pack(fill="x", pady=2)
        
        # --- Left Side: 1. General Info ---
        frame_left = tk.Frame(frame_top)
        frame_left.pack(side="left", fill="both", expand=True)
        
        frame_general = tk.LabelFrame(frame_left, text="1. General Info", padx=5, pady=5)
        frame_general.pack(fill="x", pady=2)
        
        tk.Label(frame_general, text="Title*:").grid(row=1, column=0, sticky="w")
        self.entry_title = tk.Entry(frame_general, width=25)
        self.entry_title.grid(row=1, column=1, columnspan=2, padx=2, sticky="w")
        
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
        
        tk.Label(frame_general, text="Stock:").grid(row=4, column=0, sticky="w", pady=2)
        self.entry_stock = tk.Entry(frame_general, width=10)
        self.entry_stock.grid(row=4, column=1, sticky="w", padx=2, pady=2)
        
        tk.Label(frame_general, text="Price ($)*:").grid(row=4, column=2, sticky="w")
        self.entry_price = tk.Entry(frame_general, width=12)
        self.entry_price.grid(row=4, column=3, sticky="w", padx=2)
        self.entry_price.bind("<KeyRelease>", self.calculate_cogs)
        
        # COGS & Profit (Row 5)
        
        # Capture theme's default entry background dynamically
        default_bg = self.entry_price.cget("bg")
        
        tk.Label(frame_general, text="COGS:").grid(row=5, column=0, sticky="w", pady=2)
        self.entry_cogs = tk.Entry(frame_general, width=10, state="readonly", fg="red", readonlybackground=default_bg)
        self.entry_cogs.grid(row=5, column=1, sticky="w", padx=2, pady=2)
        
        tk.Label(frame_general, text="Profit:").grid(row=5, column=2, sticky="w")
        self.entry_profit = tk.Entry(frame_general, width=12, state="readonly", fg="green", readonlybackground=default_bg)
        self.entry_profit.grid(row=5, column=3, sticky="w", padx=2)

        # Recommended Price (Row 6)
        tk.Label(frame_general, text="Rec. Price:").grid(row=6, column=2, sticky="w")
        self.entry_rec_price = tk.Entry(frame_general, width=12, state="readonly", fg="blue", readonlybackground=default_bg)
        self.entry_rec_price.grid(row=6, column=3, sticky="w", padx=2)

        # Shipping & Break Even CA (Row 7)
        tk.Label(frame_general, text="Shipping (CA):").grid(row=7, column=0, sticky="w", pady=2)
        self.entry_shipping_ca = tk.Entry(frame_general, width=10, state="readonly", fg="purple", readonlybackground=default_bg)
        self.entry_shipping_ca.grid(row=7, column=1, sticky="w", padx=2, pady=2)
        
        tk.Label(frame_general, text="Break Even (CA):").grid(row=7, column=2, sticky="w")
        self.entry_break_even_ca = tk.Entry(frame_general, width=12, state="readonly", fg="black", readonlybackground=default_bg)
        self.entry_break_even_ca.grid(row=7, column=3, sticky="w", padx=2)

        # Shipping & Break Even US (Row 8)
        tk.Label(frame_general, text="Shipping (US):").grid(row=8, column=0, sticky="w", pady=2)
        self.entry_shipping_us = tk.Entry(frame_general, width=10, state="readonly", fg="purple", readonlybackground=default_bg)
        self.entry_shipping_us.grid(row=8, column=1, sticky="w", padx=2, pady=2)
        
        tk.Label(frame_general, text="Break Even (US):").grid(row=8, column=2, sticky="w")
        self.entry_break_even_us = tk.Entry(frame_general, width=12, state="readonly", fg="black", readonlybackground=default_bg)
        self.entry_break_even_us.grid(row=8, column=3, sticky="w", padx=2)

        # Etsy Fees CA (Row 9)
        tk.Label(frame_general, text="Etsy Fees (CA):").grid(row=9, column=0, sticky="w", pady=2)
        self.entry_etsy_fees_ca = tk.Entry(frame_general, width=10, state="readonly", fg="orange", readonlybackground=default_bg)
        self.entry_etsy_fees_ca.grid(row=9, column=1, sticky="w", padx=2, pady=2)
        
        tk.Label(frame_general, text="Etsy Fees (US):").grid(row=9, column=2, sticky="w")
        self.entry_etsy_fees_us = tk.Entry(frame_general, width=12, state="readonly", fg="orange", readonlybackground=default_bg)
        self.entry_etsy_fees_us.grid(row=9, column=3, sticky="w", padx=2)

        # --- Right Side: Main Image Preview ---
        frame_right = tk.LabelFrame(frame_top, text="Main Image", padx=5, pady=5)
        frame_right.pack(side="right", fill="y", padx=5)
        
        self.lbl_main_img_preview = tk.Label(frame_right, text="No Image", width=20, height=10, bg="#f0f0f0")
        self.lbl_main_img_preview.pack()
        
        # Debug Label
        self.lbl_img_debug = tk.Label(frame_right, text="Data: None", font=("Arial", 8), fg="gray")
        self.lbl_img_debug.pack()
        
        tk.Button(frame_right, text="Select Image", command=self.select_image).pack(pady=2)

        # --- 2. Physical Specs (Below Top Frame) ---
        frame_specs = tk.LabelFrame(parent, text="2. Physical Specs", padx=5, pady=5)
        frame_specs.pack(fill="x", pady=2)
        
        tk.Label(frame_specs, text="Size (L/W/H cm):").pack(side="left")
        self.entry_l = tk.Entry(frame_specs, width=5); self.entry_l.pack(side="left", padx=2)
        self.entry_w = tk.Entry(frame_specs, width=5); self.entry_w.pack(side="left", padx=2)
        self.entry_h = tk.Entry(frame_specs, width=5); self.entry_h.pack(side="left", padx=2)
        
        tk.Label(frame_specs, text="Weight (g):").pack(side="left", padx=5)
        self.entry_weight = tk.Entry(frame_specs, width=8)
        self.entry_weight.pack(side="left")

        for entry in [self.entry_l, self.entry_w, self.entry_h, self.entry_weight]:
            entry.bind("<KeyRelease>", self.update_shipping_estimate)
            entry.bind("<FocusOut>", self.update_shipping_estimate)
        
        # --- 3. Image Gallery (Placeholder for now) ---
        frame_imgs = tk.LabelFrame(parent, text="3. Images (Max 20)", padx=5, pady=5)
        frame_imgs.pack(fill="both", expand=True, pady=2)
        
        btn_img_actions = tk.Frame(frame_imgs)
        btn_img_actions.pack(fill="x")
        tk.Button(btn_img_actions, text="Add Gallery Image", command=self.add_image_dialog).pack(side="left")
        
        # Gallery Grid
        self.gallery_frame = tk.Frame(frame_imgs)
        self.gallery_frame.pack(fill="both", expand=True)

    def create_bom_tab(self):
        parent = self.tab_bom
        # --- Bill of Materials ---
        frame_bom = tk.LabelFrame(parent, text="Bill of Materials", padx=5, pady=5)
        frame_bom.pack(fill="x", pady=2)

        # Dynamic Generation based on Config
        current_row = 0
        bind_list = []

        # Iterate over BOM_LAYOUT from config
        # We need to import BOM_LAYOUT first, but since replacement is block based:
        from config.config import BOM_LAYOUT, DEFAULT_LABOR_RATE
        print(f"DEBUG: BOM_LAYOUT length: {len(BOM_LAYOUT)}")

        for item in BOM_LAYOUT:
             # Labels and Entries
             tk.Label(frame_bom, text=f"{item['label']}:").grid(row=current_row, column=0, sticky="w")
             
             ent_name = tk.Entry(frame_bom, width=15)
             ent_name.grid(row=current_row, column=1, padx=2)
             # Map: self.entry_{id}_name
             setattr(self, f"entry_{item['id']}_name", ent_name)
             bind_list.append(ent_name)

             # Qty/Weight Entry
             if item['type'] in ['weight', 'weight_unit']:
                 lbl = "Weight (g):"
                 # Special handling for legacy db_prefix if needed (e.g. frag -> fragrance)
                 mapped_attr = f"entry_{item.get('db_prefix', item['id'])}_g" 
             elif item['type'] in ['unit', 'basic']:
                 lbl = "Qty:"
                 mapped_attr = f"entry_{item['id']}_qty"
             
             if item['type'] != 'basic': 
                 tk.Label(frame_bom, text=lbl).grid(row=current_row, column=2, sticky="w")
                 ent_qty = tk.Entry(frame_bom, width=6)
                 ent_qty.grid(row=current_row, column=3, padx=2)
                 setattr(self, mapped_attr, ent_qty)
                 if item['type'] == 'unit': ent_qty.insert(0, "1")
                 bind_list.append(ent_qty)
             
             # Rate / Cost Entry
             tk.Label(frame_bom, text=item['rate_label']).grid(row=current_row, column=4, sticky="w")
             ent_rate = tk.Entry(frame_bom, width=8)
             ent_rate.grid(row=current_row, column=5, padx=2, sticky="w")
             
             # Naming: entry_{id}_rate usually.
             rate_attr = f"entry_{item['id']}_rate"
             if item['id'] == 'box': rate_attr = "entry_box" # Backward compat
             if item['id'] == 'wrap': rate_attr = "entry_wrap" # Backward compat
             
             setattr(self, rate_attr, ent_rate)
             bind_list.append(ent_rate)
             
             current_row += 1

        # Labor (Fixed for now as it's not strictly Material in config yet)
        tk.Label(frame_bom, text="Labor Time (min):").grid(row=current_row, column=0, sticky="w")
        self.entry_labor_time = tk.Entry(frame_bom, width=6)
        self.entry_labor_time.grid(row=current_row, column=1, padx=2, sticky="w")
        
        tk.Label(frame_bom, text="Labor Rate ($/h):").grid(row=current_row, column=2, sticky="w")
        self.entry_labor_rate = tk.Entry(frame_bom, width=6)
        self.entry_labor_rate.grid(row=current_row, column=3, padx=2, sticky="w")
        self.entry_labor_rate.insert(0, str(DEFAULT_LABOR_RATE))
        bind_list.append(self.entry_labor_time)
        bind_list.append(self.entry_labor_rate)
        
        current_row += 1
        tk.Label(frame_bom, text="Biz Card ($):").grid(row=current_row, column=0, sticky="w")
        self.entry_biz_card = tk.Entry(frame_bom, width=6)
        self.entry_biz_card.grid(row=current_row, column=1, padx=2, sticky="w")
        bind_list.append(self.entry_biz_card)

        # Bindings
        for entry in bind_list:
             entry.bind("<KeyRelease>", self.calculate_cogs)
        
        # Add COGS Table here within BOM tab
        self.create_cogs_table(parent) 

    def create_cogs_table(self, parent):
        lbl_frame = tk.LabelFrame(parent, text="COGS Calculator", padx=5, pady=5)
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

    def calculate_cogs(self, event=None):
        # Clear table
        for item in self.cogs_tree.get_children():
            self.cogs_tree.delete(item)
            
        total_cost = 0.0
        
        # Helper to simplify
        def get_val(entry, is_float=True, default=0):
            try:
                val = entry.get()
                if not val: return default
                return float(val) if is_float else int(val)
            except ValueError:
                return default

        # 1. Wax
        # Generic calculation based on BOM_LAYOUT
        from config.config import BOM_LAYOUT
        
        for item in BOM_LAYOUT:
            item_id = item['id']
            item_type = item['type']
            label = item['label']
            
            # Rate
            rate_attr = f"entry_{item_id}_rate"
            if item_id == 'box': rate_attr = "entry_box"
            if item_id == 'wrap': rate_attr = "entry_wrap"
            
            rate_entry = getattr(self, rate_attr, None)
            rate = get_val(rate_entry) if rate_entry else 0.0
            
            cost = 0.0
            display_qty = ""
            display_rate = f"${rate}"
            
            if item_type in ['weight', 'weight_unit']:
                # Weight based
                mapped_g_attr = f"entry_{item.get('db_prefix', item_id)}_g"
                g_entry = getattr(self, mapped_g_attr, None)
                weight_g = get_val(g_entry) if g_entry else 0.0
                
                if weight_g > 0:
                    # Rate is $/kg
                    cost = weight_g * (rate / 1000)
                    display_qty = f"{weight_g} g"
                    display_rate = f"${rate}/kg"
                    
            elif item_type in ['unit', 'basic']: # 'basic' treated like unit if it has quantity?
                # Unit based
                qty_attr = f"entry_{item_id}_qty"
                qty_entry = getattr(self, qty_attr, None)
                # Box default 1, others 1
                qty = get_val(qty_entry, is_float=False, default=1) if qty_entry else 1
                
                if item_type == 'basic' and not qty_entry:
                    # Pure cost item (Wrap)
                    qty = 1
                    
                if rate > 0:
                    cost = qty * rate
                    display_qty = f"{qty} units" if ((item_type == 'unit') or (item_type=='basic' and qty_entry)) else "1 unit"
                    display_rate = f"${rate}"
            
            if cost > 0:
                self.cogs_tree.insert("", "end", values=(label, display_qty, display_rate, f"${cost:.2f}"))
                total_cost += cost

        # Biz Card
        biz = get_val(self.entry_biz_card)
        if biz > 0:
            self.cogs_tree.insert("", "end", values=("Biz Card", "1 unit", f"${biz}", f"${biz:.2f}"))
            total_cost += biz
            
        # 6. Labor
        l_time = get_val(self.entry_labor_time, is_float=False, default=0)
        l_rate = get_val(self.entry_labor_rate)
        if l_time > 0 and l_rate > 0:
             l_cost = (l_time / 60) * l_rate
             self.cogs_tree.insert("", "end", values=("Labor", f"{l_time} min", f"${l_rate}/h", f"${l_cost:.2f}"))
             total_cost += l_cost

        self.lbl_total_cogs.config(text=f"TOTAL COGS: ${total_cost:.2f}")
        
        # Initial display for COGS
        self.entry_cogs.config(state="normal")
        self.entry_cogs.delete(0, "end")
        self.entry_cogs.insert(0, f"${total_cost:.2f}")
        self.entry_cogs.config(state="readonly")
        
        # Calculate Profit
        # Get Price
        try:
             price_val = float(self.entry_price.get())
        except ValueError:
             price_val = 0.0
             
        profit = price_val - total_cost
        
        self.entry_profit.config(state="normal", fg="green" if profit >= 0 else "red")
        self.entry_profit.delete(0, "end")
        self.entry_profit.insert(0, f"${profit:.2f}")
        self.entry_profit.config(state="readonly")

        self.entry_profit.config(state="readonly")

        # Calculate Recommended Price logic
        # Price = (Materials * M) + Labor
        # M = M_min + (M_max - M_min) / (1 + (Cost / Decay))
        
        # 1. Separate Materials from Labor
        # We calculated total_cost earlier which includes Labor.
        # We also calculated l_cost explicitly.
        # If l_cost was not calculated (not in 'if' block), it defaults to 0.
        
        # Re-calc labor cost to be sure (scope issue if not defined in if)
        labor_cost_val = 0.0
        l_time_val = get_val(self.entry_labor_time, is_float=False, default=0)
        l_rate_val = get_val(self.entry_labor_rate)
        if l_time_val > 0 and l_rate_val > 0:
             labor_cost_val = (l_time_val / 60) * l_rate_val
             
        material_cost = total_cost - labor_cost_val
        
        # Get Config Params
        from config.config import config_data
        pricing = config_data.get("pricing", {})
        if pricing.get("enabled", False):
            m_max = pricing.get("markup_max", 5.0)
            m_min = pricing.get("markup_min", 1.5)
            decay = pricing.get("decay_factor", 20.0)
            
            # Formlua
            # Avoid division by zero if decay is 0 (unlikely but safe)
            denominator = 1 + (material_cost / decay) if decay else 1
            markup = m_min + (m_max - m_min) / denominator
            
            rec_price = (material_cost * markup) + labor_cost_val
            
            # Build string with explanation tooltip? Just val for now.
            disp_str = f"${rec_price:.2f} (x{markup:.2f})"
            
            self.entry_rec_price.config(state="normal")
            self.entry_rec_price.delete(0, "end")
            self.entry_rec_price.insert(0, disp_str)
            self.entry_rec_price.config(state="readonly")

            self.entry_rec_price.config(state="readonly")
            
        # Calculate Total Weight = Sum of all 'weight' or 'weight_unit' items
        # Only if we have valid values
        calc_weight = 0.0
        
        # Iterate BOM again to sum weights? Or we could have done it in previous loop.
        # Let's iterate again for clarity or just grab filters.
        for item in BOM_LAYOUT:
            if item['type'] in ['weight', 'weight_unit']:
                # Retrieve the weight value
                mapped_g_attr = f"entry_{item.get('db_prefix', item['id'])}_g"
                g_entry = getattr(self, mapped_g_attr, None)
                w_val = get_val(g_entry) if g_entry else 0.0
                if w_val > 0:
                     calc_weight += w_val
        
        # Update Weight Entry if calculated weight > 0 and user hasn't manually set it
        if calc_weight > 0:
            current_weight = self.entry_weight.get().strip()
            # Only auto-fill if weight is empty (user hasn't manually entered)
            if not current_weight:
                self.entry_weight.delete(0, "end")
                self.entry_weight.insert(0, f"{calc_weight:.2f}")
                self.update_shipping_estimate()
            else:
                # User manually entered weight, so just update shipping with their value
                self.update_shipping_estimate()
            
        self.calculate_break_even()
        return total_cost

    def display_main_image(self, image_input):
        if not HAS_PIL:
            self.lbl_main_img_preview.config(text="PIL Missing")
            return

        if not image_input:
            self.lbl_main_img_preview.config(image="", text="No Image", width=20, height=10)
            self.current_preview_image = None # Keep reference
            self.lbl_img_debug.config(text="Data: None")
            return
            
        try:
            # Determine if bytes or base64 string
            img_bytes = None
            if isinstance(image_input, bytes):
                img_bytes = image_input
            elif isinstance(image_input, str):
                # Decode Base64
                if "," in image_input: # Remove header if present (data:image/png;base64,...)
                    image_input = image_input.split(",")[1]
                img_bytes = base64.b64decode(image_input)
            
            if img_bytes:
                pil_img = Image.open(io.BytesIO(img_bytes))
                # Resize for thumbnail
                pil_img.thumbnail((150, 150))
                tk_img = ImageTk.PhotoImage(pil_img)
                
                self.lbl_main_img_preview.config(image=tk_img, text="", width=150, height=150)
                self.current_preview_image = tk_img # Keep ref!
                self.lbl_img_debug.config(text=f"Data: {len(img_bytes)} bytes")
        except Exception as e:
            # print(f"Error displaying image: {e}") # Suppress noisy error for bad data
            self.lbl_main_img_preview.config(text="Invalid Image", image="", width=20, height=10)
            self.lbl_img_debug.config(text="Data: Error")

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if file_path:
            with open(file_path, "rb") as f:
                self.image_data = f.read()
            self.display_main_image(self.image_data)

    def add_image_dialog(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.png *.jpeg")])
        if not file_paths:
            return

        success_count = 0
        errors = []

        for file_path in file_paths:
            try:
                with open(file_path, "rb") as f:
                    img_bytes = f.read()

                if not self.current_product_id:
                    # Pending Mode
                    temp_id = f"temp_{uuid.uuid4()}"
                    self.pending_gallery_images.append({
                        'id': temp_id,
                        'image_data': base64.b64encode(img_bytes).decode('utf-8'),
                        'raw_bytes': img_bytes
                    })
                else:
                    # Live Mode
                    APIClient.add_product_image(self.current_product_id, img_bytes)
                
                success_count += 1
            except Exception as e:
                errors.append(f"{file_path}: {e}")

        # Refresh once after processing all
        self.refresh_gallery()
        
        if errors:
            messagebox.showwarning("Upload Issues", "Some images failed to upload:\n" + "\n".join(errors))
        elif success_count > 0:
            # Optional: Show success toast or just status? 
            # messagebox.showinfo("Success", f"Added {success_count} images.") # A bit annoying
            pass

    def refresh_gallery(self):
        # Clear existing
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
            
        if not HAS_PIL:
            tk.Label(self.gallery_frame, text="PIL Required").pack()
            return
            
        try:
            images = []
            if self.current_product_id:
                images = APIClient.get_product_images(self.current_product_id)
            else:
                images = self.pending_gallery_images

            row = 0
            col = 0
            max_cols = 5
            self.gallery_refs = [] # Keep refs to prevent GC
            
            for img in images:
                img_data = img.get('image_data')
                img_id = img.get('id')
                if img_data:
                    try:
                        b64_data = img_data
                        if "," in b64_data:
                            b64_data = b64_data.split(",")[1]
                        
                        img_bytes = base64.b64decode(b64_data)
                        pil_img = Image.open(io.BytesIO(img_bytes))
                        pil_img.thumbnail((100, 100)) # Smaller thumbnail
                        tk_img = ImageTk.PhotoImage(pil_img)
                        self.gallery_refs.append(tk_img)
                        
                        # Container Frame
                        f = tk.Frame(self.gallery_frame, bd=1, relief="solid")
                        f.grid(row=row, column=col, padx=5, pady=5)
                        
                        lbl = tk.Label(f, image=tk_img)
                        lbl.pack()
                        
                        # Context Menu
                        menu = tk.Menu(f, tearoff=0)
                        menu.add_command(label="Set as Main Image", command=lambda i=img_id, d=b64_data: self.set_main_image_from_gallery(d))
                        
                        def do_popup(event, m=menu):
                            try: m.tk_popup(event.x_root, event.y_root)
                            finally: m.grab_release()
                        lbl.bind("<Button-3>", do_popup) 
                        
                        btn_del = tk.Button(f, text="x", font=("Arial", 8), fg="red", 
                                            command=lambda i=img_id: self.delete_image_from_gallery(i))
                        btn_del.place(relx=1.0, rely=0.0, anchor="ne")
                        
                        col += 1
                        if col >= max_cols:
                            col = 0; row += 1
                    except Exception as e:
                        print(f"Error rendering gallery image {img_id}: {e}")
        except Exception as e:
            tk.Label(self.gallery_frame, text=f"Error loading gallery: {e}").pack()

    def set_main_image_from_gallery(self, b64_data):
        self.display_main_image(b64_data)
        
        # Internal State Update
        try:
             clean_b64 = b64_data.split(",")[1] if "," in b64_data else b64_data
             self.image_data = base64.b64decode(clean_b64)
        except Exception as e:
             print(f"Error updating local state for image: {e}")

        # If Live Mode, API Call
        if self.current_product_id:
            try:
                APIClient.update_product(self.current_product_id, {'image': b64_data})
                messagebox.showinfo("Success", "Main image updated.")
                # We should notify parent to refresh? Or assume parent handles list refresh elsewhere.
                # Actually parent list is stale if we don't refresh it.
                # Ideally, form should trigger an event. But for now, let's just save valid state.
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update main image: {e}")

    def delete_image_from_gallery(self, img_id):
        if not messagebox.askyesno("Confirm", "Delete this image?"):
            return
            
        try:
            if str(img_id).startswith("temp_"):
                self.pending_gallery_images = [img for img in self.pending_gallery_images if img['id'] != img_id]
                self.refresh_gallery()
            else:
                APIClient.delete_product_image(img_id)
                self.refresh_gallery()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear(self):
        # Helper to clear entries
        for entry in [self.entry_title, self.entry_desc, self.entry_sku, self.entry_upc, 
                      self.entry_stock, self.entry_price, self.entry_l, self.entry_w, self.entry_h, 
                      self.entry_weight, self.entry_wax_name, self.entry_wax_g, self.entry_wax_rate,
                      self.entry_frag_name, self.entry_fragrance_g, self.entry_frag_rate,
                      self.entry_wick_name, self.entry_wick_rate, self.entry_container_name, 
                      self.entry_container_rate, self.entry_second_container_name, 
                      self.entry_second_container_g, self.entry_second_container_rate,
                      self.entry_box_name, self.entry_box, 
                      self.entry_wrap, self.entry_biz_card, self.entry_labor_time]:
            entry.delete(0, tk.END)
            
        self.entry_wick_qty.delete(0, tk.END); self.entry_wick_qty.insert(0, "1")
        self.entry_container_qty.delete(0, tk.END); self.entry_container_qty.insert(0, "1")
        self.entry_box_qty.delete(0, tk.END); self.entry_box_qty.insert(0, "1")
        self.entry_labor_rate.delete(0, tk.END); self.entry_labor_rate.insert(0, str(DEFAULT_LABOR_RATE))
        
        # Clear readonly fields
        for entry in [self.entry_etsy_fees_ca, self.entry_etsy_fees_us]:
            entry.config(state="normal")
            entry.delete(0, tk.END)
            entry.config(state="readonly")
        
        self.image_data = None
        self.pending_gallery_images = []
        self.current_product_id = None
        self.display_main_image(None)
        self.refresh_gallery()
        self.calculate_cogs()

    def load_product(self, data):
        self.clear()
        self.current_product_id = data.get('id')
        
        def set_val(entry, val):
            entry.delete(0, tk.END)
            if val is not None:
                entry.insert(0, str(val))

        set_val(self.entry_title, data.get('title'))
        set_val(self.entry_desc, data.get('description'))
        set_val(self.entry_sku, data.get('sku'))
        set_val(self.entry_upc, data.get('upc'))
        set_val(self.entry_stock, data.get('stock_quantity', 0))
        set_val(self.entry_price, data.get('selling_price', 0))
        
        set_val(self.entry_l, data.get('length_cm'))
        set_val(self.entry_w, data.get('width_cm'))
        set_val(self.entry_h, data.get('height_cm'))
        set_val(self.entry_weight, data.get('weight_g'))
        
        set_val(self.entry_wax_name, data.get('wax_type'))
        set_val(self.entry_wax_g, data.get('wax_weight_g'))
        set_val(self.entry_wax_rate, data.get('wax_rate'))
        
        if hasattr(self, 'entry_frag_name'):
            set_val(self.entry_frag_name, data.get('fragrance_type'))
        set_val(self.entry_fragrance_g, data.get('fragrance_weight_g'))
        set_val(self.entry_frag_rate, data.get('fragrance_rate'))
        
        set_val(self.entry_wick_name, data.get('wick_type'))
        set_val(self.entry_wick_rate, data.get('wick_rate'))
        set_val(self.entry_wick_qty, data.get('wick_quantity', 1))

        set_val(self.entry_container_name, data.get('container_type'))
        set_val(self.entry_container_rate, data.get('container_rate'))
        set_val(self.entry_container_qty, data.get('container_quantity', 1))

        if hasattr(self, 'entry_second_container_name'):
            set_val(self.entry_second_container_name, data.get('second_container_type'))
            set_val(self.entry_second_container_g, data.get('second_container_weight_g'))
            set_val(self.entry_second_container_rate, data.get('second_container_rate'))
            
        set_val(self.entry_box_name, data.get('box_type'))
        set_val(self.entry_box, data.get('box_price'))
        set_val(self.entry_box_qty, data.get('box_quantity', 1))
        
        set_val(self.entry_wrap, data.get('wrap_price'))
        set_val(self.entry_biz_card, data.get('business_card_cost'))
        
        set_val(self.entry_labor_time, data.get('labor_time'))
        set_val(self.entry_labor_rate, data.get('labor_rate'))
        
        self.update_shipping_estimate()
        # Ah, DB has fragrance_type? 
        # Let's check DB schema or API response. 
        # Assuming API returns keys matching what we saved. 
        # In current products_tab, save_product does: "fragrance_weight_g", "fragrance_rate"... but where is type?
        # create_core_tab code: self.entry_frag_name...
        # save_product code: ... wait, I don't see 'fragrance_type' being saved in my previous read of save_product!
        # Let's check lines 526 in products_tab:
        # "fragrance_weight_g": ... "fragrance_rate": ... where is name? 
        # It seems I might have missed it in previous refactor or products_tab.
        # Let's check `db/products.py` `create_product`... columns list.
        # If it's missing, I should add it.
        # For now, I will use what I have.
        
        set_val(self.entry_fragrance_g, data.get('fragrance_weight_g'))
        set_val(self.entry_frag_rate, data.get('fragrance_rate'))
        
        set_val(self.entry_wick_name, data.get('wick_type'))
        set_val(self.entry_wick_rate, data.get('wick_rate'))
        set_val(self.entry_wick_qty, data.get('wick_quantity'))
        
        set_val(self.entry_container_name, data.get('container_type'))
        set_val(self.entry_container_rate, data.get('container_rate'))
        set_val(self.entry_container_qty, data.get('container_quantity'))
        
        set_val(self.entry_second_container_name, data.get('second_container_type'))
        set_val(self.entry_second_container_g, data.get('second_container_weight_g'))
        set_val(self.entry_second_container_rate, data.get('second_container_rate'))

        set_val(self.entry_box_name, data.get('box_type'))
        set_val(self.entry_box, data.get('box_price'))
        set_val(self.entry_box_qty, data.get('box_quantity'))
        
        set_val(self.entry_wrap, data.get('wrap_price'))
        set_val(self.entry_biz_card, data.get('business_card_cost'))
        
        set_val(self.entry_labor_time, data.get('labor_time'))
        set_val(self.entry_labor_rate, data.get('labor_rate'))

        # Image
        if data.get('image'):
            img_blob = data.get('image')
            # It might be bytes or base64 string depending on API
            # APIClient get_products usually returns what's in DB (BLOB -> bytes in python connector)
            # But wait, routes.py get_products returns data.
            # python connector returns bytes for blob.
            # FastAPI json encoder might fail on bytes, so routes.py usually handles encoding?
            # actually routes.py `get_products` does not iterate and encode images. 
            # If DB returns bytes, generic serializer might fail or return string repr?
            # Actually, my previous debugging showed "image" column exists.
            # If the API client is getting "data: len X bytes", it's bytes.
            self.image_data = img_blob
            self.display_main_image(img_blob)
            
        self.refresh_gallery()
        self.calculate_cogs()

    def get_data(self):
        title = self.entry_title.get().strip()
        sku = self.entry_sku.get().strip()
        
        if not title:
            raise ValueError("Title is required")

        total_cost = self.calculate_cogs()
        
        def safe_float(entry, default=0.0):
            try:
                val = entry.get().strip()
                if not val:
                    return float(default)
                # Replace commas with empty string to handle "1,000" gracefully
                val = val.replace(',', '')
                return float(val)
            except ValueError:
                return float(default)

        def safe_int(entry, default=1):
            try:
                val = entry.get().strip()
                if not val:
                    return int(default)
                val = val.replace(',', '')
                return int(val)
            except ValueError:
                return int(default)
        
        data = {
            "title": title,
            "sku": sku,
            "upc": self.entry_upc.get().strip(),
            "description": self.entry_desc.get().strip() if self.entry_desc.get() else None,
            "stock_quantity": safe_int(self.entry_stock, 0),
            "length_cm": safe_float(self.entry_l, 0),
            "width_cm": safe_float(self.entry_w, 0),
            "height_cm": safe_float(self.entry_h, 0),
            "weight_g": safe_float(self.entry_weight, 0),
            "wax_type": self.entry_wax_name.get().strip() if self.entry_wax_name.get() else None,
            "wax_weight_g": safe_float(self.entry_wax_g, 0),
            "wax_rate": safe_float(self.entry_wax_rate, 0),
            "fragrance_type": self.entry_frag_name.get().strip() if getattr(self, 'entry_frag_name', None) and self.entry_frag_name.get() else None, 
            "fragrance_weight_g": safe_float(self.entry_fragrance_g, 0),
            "fragrance_rate": safe_float(self.entry_frag_rate, 0),
            "wick_type": self.entry_wick_name.get().strip() if self.entry_wick_name.get() else None,
            "wick_rate": safe_float(self.entry_wick_rate, 0),
            "wick_quantity": safe_int(self.entry_wick_qty, 1),
            "container_type": self.entry_container_name.get().strip() if self.entry_container_name.get() else None,
            "container_rate": safe_float(self.entry_container_rate, 0),
            "container_quantity": safe_int(self.entry_container_qty, 1), 
            "second_container_type": self.entry_second_container_name.get().strip() if getattr(self, 'entry_second_container_name', None) and self.entry_second_container_name.get() else None,
            "second_container_weight_g": safe_float(self.entry_second_container_g, 0) if getattr(self, 'entry_second_container_g', None) else 0.0,
            "second_container_rate": safe_float(self.entry_second_container_rate, 0) if getattr(self, 'entry_second_container_rate', None) else 0.0,
            "box_type": self.entry_box_name.get().strip() if self.entry_box_name.get() else None,
            "box_price": safe_float(self.entry_box, 0),
            "box_quantity": safe_int(self.entry_box_qty, 1),
            "wrap_price": safe_float(self.entry_wrap, 0),
            "business_card_cost": safe_float(self.entry_biz_card, 0),
            "labor_time": safe_int(self.entry_labor_time, 0),
            "labor_rate": safe_float(self.entry_labor_rate, 0),
            "selling_price": safe_float(self.entry_price, 0),
            "total_cost": total_cost,
            "image": base64.b64encode(self.image_data).decode('utf-8') if self.image_data and isinstance(self.image_data, bytes) else self.image_data,
        }
        return data

    def update_shipping_estimate(self, event=None):
        """Calculates and updates both CA and US shipping estimate fields and triggers break-even."""
        weight_str = self.entry_weight.get().strip()
        
        def set_ship_val(entry, val_str):
            entry.config(state="normal")
            entry.delete(0, 'end')
            if val_str:
                entry.insert(0, val_str)
            entry.config(state="readonly")
            
        if not weight_str:
            set_ship_val(self.entry_shipping_ca, "N/A")
            set_ship_val(self.entry_shipping_us, "N/A")
            self.calculate_break_even()
            return

        try:
            # Safely parse commas or spaces
            weight_str = weight_str.replace(',', '')
            weight_g = float(weight_str)
            if weight_g > 0:
                best = get_cheapest_by_destination(weight_g)
                if best and best["ca"]:
                    set_ship_val(self.entry_shipping_ca, f"${best['ca']['cost']:.2f}")
                else:
                    set_ship_val(self.entry_shipping_ca, "N/A")
                
                if best and best["us"]:
                    set_ship_val(self.entry_shipping_us, f"${best['us']['cost']:.2f}")
                else:
                    set_ship_val(self.entry_shipping_us, "N/A")
            else:
                set_ship_val(self.entry_shipping_ca, "N/A")
                set_ship_val(self.entry_shipping_us, "N/A")
        except ValueError:
            set_ship_val(self.entry_shipping_ca, "Error")
            set_ship_val(self.entry_shipping_us, "Error")
            
        self.calculate_break_even()

    def calculate_break_even(self):
        """Calculates Break Even price including COGS, Shipping (FREE SHIPPING - included in price), and Etsy Fees for both CA and US
        
        Etsy Fees (standard):
        - Listing: $0.20 fixed
        - Transaction: 6.5% of Price
        - Payment Processing: 3% + $0.25 of Price
        
        Since shipping is FREE (included in price):
        Formula: Price = (COGS + Shipping + 0.45) / 0.905
        """
        try:
            cogs_str = self.entry_cogs.get().replace('$', '').strip()
            cogs_val = float(cogs_str) if cogs_str and cogs_str != "N/A" and cogs_str != "Error" else 0.0
            
            # Etsy fee rates
            LISTING_FEE = 0.20
            TRANSACTION_RATE = 0.065  # 6.5%
            PAYMENT_RATE = 0.03       # 3%
            PAYMENT_FIXED = 0.25
            COMBINED_RATE = TRANSACTION_RATE + PAYMENT_RATE  # 9.5%
            
            # CA
            ship_ca_str = self.entry_shipping_ca.get().replace('$', '').strip()
            ship_ca_val = float(ship_ca_str) if ship_ca_str and ship_ca_str != "N/A" and ship_ca_str != "Error" else 0.0
            
            # Calculate break-even with FREE shipping (included in price)
            # break_even = (cogs + shipping + LISTING_FEE + PAYMENT_FIXED) / (1 - COMBINED_RATE)
            break_even_ca = (cogs_val + ship_ca_val + LISTING_FEE + PAYMENT_FIXED) / (1 - COMBINED_RATE)
            
            # Calculate Etsy fees at break-even price (CA)
            etsy_listing_fee_ca = LISTING_FEE
            etsy_transaction_fee_ca = break_even_ca * TRANSACTION_RATE
            etsy_payment_fee_ca = (break_even_ca * PAYMENT_RATE) + PAYMENT_FIXED
            total_etsy_fees_ca = etsy_listing_fee_ca + etsy_transaction_fee_ca + etsy_payment_fee_ca
            
            self.entry_break_even_ca.config(state="normal")
            self.entry_break_even_ca.delete(0, 'end')
            if break_even_ca > 0:
                self.entry_break_even_ca.insert(0, f"${break_even_ca:.2f}")
            self.entry_break_even_ca.config(state="readonly")
            
            self.entry_etsy_fees_ca.config(state="normal")
            self.entry_etsy_fees_ca.delete(0, 'end')
            if total_etsy_fees_ca > 0:
                self.entry_etsy_fees_ca.insert(0, f"${total_etsy_fees_ca:.2f}")
            self.entry_etsy_fees_ca.config(state="readonly")
            
            # US
            ship_us_str = self.entry_shipping_us.get().replace('$', '').strip()
            ship_us_val = float(ship_us_str) if ship_us_str and ship_us_str != "N/A" and ship_us_str != "Error" else 0.0
            
            # Calculate break-even with FREE shipping (included in price)
            break_even_us = (cogs_val + ship_us_val + LISTING_FEE + PAYMENT_FIXED) / (1 - COMBINED_RATE)
            
            # Calculate Etsy fees at break-even price (US)
            etsy_listing_fee_us = LISTING_FEE
            etsy_transaction_fee_us = break_even_us * TRANSACTION_RATE
            etsy_payment_fee_us = (break_even_us * PAYMENT_RATE) + PAYMENT_FIXED
            total_etsy_fees_us = etsy_listing_fee_us + etsy_transaction_fee_us + etsy_payment_fee_us
            
            self.entry_break_even_us.config(state="normal")
            self.entry_break_even_us.delete(0, 'end')
            if break_even_us > 0:
                self.entry_break_even_us.insert(0, f"${break_even_us:.2f}")
            self.entry_break_even_us.config(state="readonly")
            
            self.entry_etsy_fees_us.config(state="normal")
            self.entry_etsy_fees_us.delete(0, 'end')
            if total_etsy_fees_us > 0:
                self.entry_etsy_fees_us.insert(0, f"${total_etsy_fees_us:.2f}")
            self.entry_etsy_fees_us.config(state="readonly")
            
        except Exception as e:
            self.entry_break_even_ca.config(state="normal")
            self.entry_break_even_ca.delete(0, 'end')
            self.entry_break_even_ca.insert(0, "Error")
            self.entry_break_even_ca.config(state="readonly")
            
            self.entry_break_even_us.config(state="normal")
            self.entry_break_even_us.delete(0, 'end')
            self.entry_break_even_us.insert(0, "Error")
            self.entry_break_even_us.config(state="readonly")
            
            self.entry_etsy_fees_ca.config(state="normal")
            self.entry_etsy_fees_ca.delete(0, 'end')
            self.entry_etsy_fees_ca.insert(0, "Error")
            self.entry_etsy_fees_ca.config(state="readonly")
            
            self.entry_etsy_fees_us.config(state="normal")
            self.entry_etsy_fees_us.delete(0, 'end')
            self.entry_etsy_fees_us.insert(0, "Error")
            self.entry_etsy_fees_us.config(state="readonly")

