import tkinter as tk
from tkinter import ttk, messagebox
from client.api_client import APIClient

class MaterialsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.materials = []
        
        # Configure layout
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # Left Panel (Inputs)
        self.left_panel = tk.Frame(self)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Right Panel (List)
        self.right_panel = tk.Frame(self)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.create_input_widgets()
        self.create_list_widgets()
        self.refresh_list()

    def create_input_widgets(self):
        lbl_frame = tk.LabelFrame(self.left_panel, text="Material Details", padx=10, pady=10)
        lbl_frame.pack(fill="x", pady=5)

        # ID / Search
        tk.Label(lbl_frame, text="ID:").grid(row=0, column=0, sticky="w")
        self.entry_id = tk.Entry(lbl_frame, width=10)
        self.entry_id.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.entry_id.bind("<Return>", self.search_by_id)
        tk.Button(lbl_frame, text="Find", command=self.search_by_id, font=("Arial", 8)).grid(row=0, column=2, sticky="w")

        tk.Label(lbl_frame, text="Name:").grid(row=1, column=0, sticky="w")
        self.entry_name = tk.Entry(lbl_frame, width=25)
        self.entry_name.grid(row=1, column=1, padx=5, pady=2, columnspan=2, sticky="w")

        tk.Label(lbl_frame, text="Category:").grid(row=2, column=0, sticky="w")
        self.combo_category = ttk.Combobox(lbl_frame, values=["wax", "wick", "fragrance", "container", "other"], width=22)
        self.combo_category.grid(row=2, column=1, padx=5, pady=2, columnspan=2, sticky="w")

        # Inventory
        tk.Label(lbl_frame, text="Stock Qty:").grid(row=3, column=0, sticky="w")
        self.entry_stock = tk.Entry(lbl_frame, width=25)
        self.entry_stock.grid(row=3, column=1, padx=5, pady=2, columnspan=2, sticky="w")

        # Calculator Helpers
        sep = tk.LabelFrame(self.left_panel, text="Price Calculator (Optional)", padx=10, pady=5)
        sep.pack(fill="x", pady=10)
        
        tk.Label(sep, text="Total Cost ($):").grid(row=0, column=0, sticky="w")
        self.entry_total_cost = tk.Entry(sep, width=15)
        self.entry_total_cost.grid(row=0, column=1, padx=5)
        self.entry_total_cost.bind("<KeyRelease>", self.calc_unit_price)
        
        tk.Label(sep, text="Total Qty:").grid(row=1, column=0, sticky="w")
        self.entry_total_qty = tk.Entry(sep, width=15)
        self.entry_total_qty.grid(row=1, column=1, padx=5)
        self.entry_total_qty.bind("<KeyRelease>", self.calc_unit_price)

        # Unit Cost Result
        tk.Label(lbl_frame, text="Unit Cost ($):").grid(row=4, column=0, sticky="w")
        self.entry_cost = tk.Entry(lbl_frame, width=25)
        self.entry_cost.grid(row=4, column=1, padx=5, pady=2, columnspan=2, sticky="w")

        tk.Label(lbl_frame, text="Unit Type:").grid(row=5, column=0, sticky="w")
        self.entry_unit = tk.Entry(lbl_frame, width=25)
        self.entry_unit.grid(row=5, column=1, padx=5, pady=2)
        tk.Label(lbl_frame, text="(g, kg, ml, unit)", font=("Arial", 8), fg="gray").grid(row=5, column=2, sticky="w")

        # Buttons
        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(btn_frame, text="Add Material", command=self.add_material, bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Material", command=self.update_material, bg="#FF9800", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_inputs).pack(side="left", padx=5)

    def calc_unit_price(self, event=None):
        try:
            total = float(self.entry_total_cost.get())
            qty = float(self.entry_total_qty.get())
            if qty > 0:
                unit_price = total / qty
                self.entry_cost.delete(0, tk.END)
                self.entry_cost.insert(0, f"{unit_price:.4f}")
        except ValueError:
            pass

    def create_list_widgets(self):
        cols = ("ID", "Name", "Stock", "Cost", "Unit")
        self.tree = ttk.Treeview(self.right_panel, columns=cols, show="headings")
        self.tree.pack(fill="both", expand=True)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)

        scrollbar = ttk.Scrollbar(self.right_panel, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y", in_=self.tree)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        tk.Button(self.right_panel, text="Delete Selected", command=self.delete_material, bg="#FF5252", fg="white").pack(pady=10)
        tk.Button(self.right_panel, text="Refresh List", command=self.refresh_list).pack(pady=5)

    def refresh(self):
        """Standard interface for controller calls"""
        self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.materials = APIClient.get_materials()
        for m in self.materials:
            self.tree.insert("", "end", values=(m['id'], m['name'], m.get('stock_quantity', 0), m['unit_cost'], m['unit_type']))

    def add_material(self):
        self._save_material(is_update=False)

    def update_material(self):
        self._save_material(is_update=True)

    def _save_material(self, is_update):
        data = self._get_form_data()
        if not data: return
        try:
            if is_update:
                selected = self.tree.selection()
                if not selected:
                    # Try using ID field if no selection
                    search_id = self.entry_id.get().strip()
                    if search_id.isdigit():
                         m_id = int(search_id)
                    else:
                        messagebox.showwarning("Warning", "No material selected or ID provided")
                        return
                else:
                    m_id = self.tree.item(selected[0])['values'][0]
                
                APIClient.update_material(m_id, data)
                messagebox.showinfo("Success", "Material Updated")
            else:
                APIClient.add_material(data)
                messagebox.showinfo("Success", "Material Added")
            
            self.refresh_list()
            self.clear_inputs()
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_material(self):
        selected = self.tree.selection()
        if not selected: return
        
        if messagebox.askyesno("Confirm", "Delete material?"):
            m_id = self.tree.item(selected[0])['values'][0]
            try:
                APIClient.delete_material(m_id)
                self.refresh_list()
                self.clear_inputs()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def _get_form_data(self):
        name = self.entry_name.get().strip()
        cost = self.entry_cost.get().strip()
        
        if not name or not cost:
            messagebox.showerror("Error", "Name and Cost are required")
            return None
        
        try:
            return {
                "name": name,
                "category": self.combo_category.get(),
                "stock_quantity": float(self.entry_stock.get() or 0),
                "unit_cost": float(cost),
                "unit_type": self.entry_unit.get().strip()
            }
        except ValueError:
            messagebox.showerror("Error", "Cost/Stock must be a number")
            return None

    def search_by_id(self, event=None):
        search_id = self.entry_id.get().strip()
        if not search_id.isdigit(): return
        
        search_id = int(search_id)
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == search_id:
                self.tree.selection_set(item)
                self.tree.see(item)
                self.on_select(None)
                return
        messagebox.showinfo("Info", "Material ID not found")

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected: return
        
        m_id = self.tree.item(selected[0])['values'][0]
        # Find material data
        mat = next((m for m in self.materials if m['id'] == m_id), None)
        if mat:
            self.clear_inputs()
            self.entry_id.insert(0, str(mat['id']))
            self.entry_name.insert(0, mat['name'])
            self.combo_category.set(mat['category'])
            self.entry_stock.insert(0, str(mat.get('stock_quantity', 0)))
            self.entry_cost.insert(0, str(mat['unit_cost']))
            self.entry_unit.insert(0, mat['unit_type'])

    def clear_inputs(self):
        self.entry_id.delete(0, tk.END)
        self.entry_name.delete(0, tk.END)
        self.combo_category.set("")
        self.entry_stock.delete(0, tk.END)
        self.entry_cost.delete(0, tk.END)
        self.entry_unit.delete(0, tk.END)
        self.entry_total_cost.delete(0, tk.END)
        self.entry_total_qty.delete(0, tk.END)
