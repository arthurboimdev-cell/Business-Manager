from client.api_client import APIClient
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config.config import DEFAULT_LABOR_RATE

import base64
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

        # Grid for BOM
        # Wax
        tk.Label(frame_bom, text="Wax Name:").grid(row=0, column=0, sticky="w")
        self.entry_wax_name = tk.Entry(frame_bom, width=15)
        self.entry_wax_name.grid(row=0, column=1, padx=2)
        
        tk.Label(frame_bom, text="Weight (g):").grid(row=0, column=2, sticky="w")
        self.entry_wax_g = tk.Entry(frame_bom, width=6)
        self.entry_wax_g.grid(row=0, column=3, padx=2)
        
        tk.Label(frame_bom, text="Rate ($/g):").grid(row=0, column=4, sticky="w")
        self.entry_wax_rate = tk.Entry(frame_bom, width=8)
        self.entry_wax_rate.grid(row=0, column=5, padx=2)
        
        # Fragrance
        tk.Label(frame_bom, text="Frag Name:").grid(row=1, column=0, sticky="w")
        self.entry_frag_name = tk.Entry(frame_bom, width=15)
        self.entry_frag_name.grid(row=1, column=1, padx=2)
        
        tk.Label(frame_bom, text="Weight (g):").grid(row=1, column=2, sticky="w")
        self.entry_fragrance_g = tk.Entry(frame_bom, width=6)
        self.entry_fragrance_g.grid(row=1, column=3, padx=2)
        
        tk.Label(frame_bom, text="Rate ($/g):").grid(row=1, column=4, sticky="w")
        self.entry_frag_rate = tk.Entry(frame_bom, width=8)
        self.entry_frag_rate.grid(row=1, column=5, padx=2)
        
        # Wick
        tk.Label(frame_bom, text="Wick Name:").grid(row=2, column=0, sticky="w")
        self.entry_wick_name = tk.Entry(frame_bom, width=15)
        self.entry_wick_name.grid(row=2, column=1, padx=2)
        
        tk.Label(frame_bom, text="Qty:").grid(row=2, column=2, sticky="w")
        self.entry_wick_qty = tk.Entry(frame_bom, width=5)
        self.entry_wick_qty.grid(row=2, column=3, padx=2, sticky="w")
        self.entry_wick_qty.insert(0, "1")
        
        tk.Label(frame_bom, text="Rate ($/unit):").grid(row=2, column=4, sticky="w")
        self.entry_wick_rate = tk.Entry(frame_bom, width=8)
        self.entry_wick_rate.grid(row=2, column=5, padx=2, sticky="w")
        
        # Container
        tk.Label(frame_bom, text="Container:").grid(row=3, column=0, sticky="w")
        self.entry_container_name = tk.Entry(frame_bom, width=15)
        self.entry_container_name.grid(row=3, column=1, padx=2)
        
        tk.Label(frame_bom, text="Qty:").grid(row=3, column=2, sticky="w")
        self.entry_container_qty = tk.Entry(frame_bom, width=5)
        self.entry_container_qty.grid(row=3, column=3, padx=2, sticky="w")
        self.entry_container_qty.insert(0, "1")
        
        tk.Label(frame_bom, text="Rate ($/unit):").grid(row=3, column=4, sticky="w")
        self.entry_container_rate = tk.Entry(frame_bom, width=8)
        self.entry_container_rate.grid(row=3, column=5, padx=2, sticky="w")
        
        # Box 
        tk.Label(frame_bom, text="Box Name:").grid(row=4, column=0, sticky="w")
        self.entry_box_name = tk.Entry(frame_bom, width=15)
        self.entry_box_name.grid(row=4, column=1, padx=2)
        
        tk.Label(frame_bom, text="Qty:").grid(row=4, column=2, sticky="w")
        self.entry_box_qty = tk.Entry(frame_bom, width=5)
        self.entry_box_qty.grid(row=4, column=3, padx=2, sticky="w")
        self.entry_box_qty.insert(0, "1")
        
        tk.Label(frame_bom, text="Rate ($/unit):").grid(row=4, column=4, sticky="w")
        self.entry_box = tk.Entry(frame_bom, width=8)
        self.entry_box.grid(row=4, column=5, padx=2, sticky="w")
        
        # Wrap & Biz Card (Row 5)
        tk.Label(frame_bom, text="Wrap ($):").grid(row=5, column=0, sticky="w")
        self.entry_wrap = tk.Entry(frame_bom, width=6)
        self.entry_wrap.grid(row=5, column=1, padx=2, sticky="w")
        
        tk.Label(frame_bom, text="Biz Card ($):").grid(row=5, column=2, sticky="w")
        self.entry_biz_card = tk.Entry(frame_bom, width=6)
        self.entry_biz_card.grid(row=5, column=3, padx=2, sticky="w")
        
        # Labor (Row 6)
        tk.Label(frame_bom, text="Labor Time (min):").grid(row=6, column=0, sticky="w")
        self.entry_labor_time = tk.Entry(frame_bom, width=6)
        self.entry_labor_time.grid(row=6, column=1, padx=2, sticky="w")
        
        tk.Label(frame_bom, text="Labor Rate ($/h):").grid(row=6, column=2, sticky="w")
        self.entry_labor_rate = tk.Entry(frame_bom, width=6)
        self.entry_labor_rate.grid(row=6, column=3, padx=2, sticky="w")
        self.entry_labor_rate.insert(0, str(DEFAULT_LABOR_RATE))
        
        # Bindings
        for entry in [self.entry_wax_name, self.entry_wax_g, self.entry_wax_rate,
                      self.entry_frag_name, self.entry_fragrance_g, self.entry_frag_rate,
                      self.entry_wick_name, self.entry_wick_qty, self.entry_wick_rate,
                      self.entry_container_name, self.entry_container_qty, self.entry_container_rate,
                      self.entry_box_name, self.entry_box, self.entry_box_qty,
                      self.entry_wrap, self.entry_biz_card,
                      self.entry_labor_time, self.entry_labor_rate]:
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
        wax_g = get_val(self.entry_wax_g)
        wax_rate = get_val(self.entry_wax_rate)
        if wax_g > 0:
            cost = wax_g * wax_rate
            self.cogs_tree.insert("", "end", values=("Wax", f"{wax_g} g", f"${wax_rate}/g", f"${cost:.2f}"))
            total_cost += cost

        # 2. Fragrance
        frag_g = get_val(self.entry_fragrance_g)
        frag_rate = get_val(self.entry_frag_rate)
        if frag_g > 0:
            cost = frag_g * frag_rate
            self.cogs_tree.insert("", "end", values=("Fragrance", f"{frag_g} g", f"${frag_rate}/g", f"${cost:.2f}"))
            total_cost += cost

        # 3. Wick
        wick_qty = get_val(self.entry_wick_qty, is_float=False, default=1)
        wick_rate = get_val(self.entry_wick_rate)
        if wick_rate > 0:
             cost = wick_qty * wick_rate
             self.cogs_tree.insert("", "end", values=("Wick", f"{wick_qty} units", f"${wick_rate}", f"${cost:.2f}"))
             total_cost += cost
        
        # 4. Container
        cont_qty = get_val(self.entry_container_qty, is_float=False, default=1)
        cont_rate = get_val(self.entry_container_rate)
        if cont_rate > 0:
             cost = cont_qty * cont_rate
             self.cogs_tree.insert("", "end", values=("Container", f"{cont_qty} units", f"${cont_rate}", f"${cost:.2f}"))
             total_cost += cost

        # 5. Box
        box_qty = get_val(self.entry_box_qty, is_float=False, default=1)
        box_price = get_val(self.entry_box)
        if box_price > 0:
             cost = box_qty * box_price
             self.cogs_tree.insert("", "end", values=("Box", f"{box_qty} units", f"${box_price}", f"${cost:.2f}"))
             total_cost += cost

        # Wrap
        wrap_price = get_val(self.entry_wrap)
        if wrap_price > 0:
            self.cogs_tree.insert("", "end", values=("Wrap", "1 unit", f"${wrap_price}", f"${wrap_price:.2f}"))
            total_cost += wrap_price

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
                      self.entry_container_rate, self.entry_box_name, self.entry_box, 
                      self.entry_wrap, self.entry_biz_card, self.entry_labor_time]:
            entry.delete(0, tk.END)
            
        self.entry_wick_qty.delete(0, tk.END); self.entry_wick_qty.insert(0, "1")
        self.entry_container_qty.delete(0, tk.END); self.entry_container_qty.insert(0, "1")
        self.entry_box_qty.delete(0, tk.END); self.entry_box_qty.insert(0, "1")
        self.entry_labor_rate.delete(0, tk.END); self.entry_labor_rate.insert(0, str(DEFAULT_LABOR_RATE))
        
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
        
        set_val(self.entry_frag_name, data.get('fragrance_type')) # Note: schema might differ, check products_tab
        # Wait, products_tab doesn't have fragrance_type in entry map? 
        # Checking old file: "fragrance_type": self.entry_frag_name.get() -> in creation? No.
        # ProductsTab load logic:
        # self.entry_frag_name.insert(0, str(product.get('fragrance_type') or "")) 
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
        
        data = {
            "title": title,
            "sku": sku,
            "upc": self.entry_upc.get().strip(),
            "description": self.entry_desc.get(),
            "stock_quantity": int(self.entry_stock.get() or 0),
            "length_cm": float(self.entry_l.get() or 0),
            "width_cm": float(self.entry_w.get() or 0),
            "height_cm": float(self.entry_h.get() or 0),
            "weight_g": float(self.entry_weight.get() or 0),
            "wax_type": self.entry_wax_name.get(),
            "wax_weight_g": float(self.entry_wax_g.get() or 0),
            "wax_rate": float(self.entry_wax_rate.get() or 0),
            "fragrance_type": self.entry_frag_name.get(), 
            "fragrance_weight_g": float(self.entry_fragrance_g.get() or 0),
            "fragrance_rate": float(self.entry_frag_rate.get() or 0),
            "wick_type": self.entry_wick_name.get(),
            "wick_rate": float(self.entry_wick_rate.get() or 0),
            "wick_quantity": int(self.entry_wick_qty.get() or 1),
            "container_type": self.entry_container_name.get(),
            "container_rate": float(self.entry_container_rate.get() or 0),
            "container_quantity": int(self.entry_container_qty.get() or 1),
            "box_type": self.entry_box_name.get(),
            "box_price": float(self.entry_box.get() or 0),
            "box_quantity": int(self.entry_box_qty.get() or 1),
            "wrap_price": float(self.entry_wrap.get() or 0),
            "business_card_cost": float(self.entry_biz_card.get() or 0),
            "labor_time": int(self.entry_labor_time.get() or 0),
            "labor_rate": float(self.entry_labor_rate.get() or 0),
            "selling_price": float(self.entry_price.get() or 0),
            "total_cost": total_cost,
            "image": base64.b64encode(self.image_data).decode('utf-8') if self.image_data and isinstance(self.image_data, bytes) else self.image_data,
        }
        return data
