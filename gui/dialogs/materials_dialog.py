import tkinter as tk
from tkinter import ttk, messagebox
from client.api_client import APIClient

class MaterialsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manage Materials")
        self.geometry("600x450")
        
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # Input Frame
        input_frame = tk.LabelFrame(self, text="Add/Edit Material", padx=10, pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(input_frame, text="Name:").grid(row=0, column=0, sticky="w")
        self.entry_name = tk.Entry(input_frame)
        self.entry_name.grid(row=0, column=1, padx=5)

        tk.Label(input_frame, text="Category:").grid(row=0, column=2, sticky="w")
        self.combo_category = ttk.Combobox(input_frame, values=["wax", "wick", "fragrance", "container", "other"])
        self.combo_category.grid(row=0, column=3, padx=5)

        tk.Label(input_frame, text="Cost:").grid(row=1, column=0, sticky="w")
        self.entry_cost = tk.Entry(input_frame)
        self.entry_cost.grid(row=1, column=1, padx=5)

        tk.Label(input_frame, text="Unit (g/ml/unit):").grid(row=1, column=2, sticky="w")
        self.entry_unit = tk.Entry(input_frame)
        self.entry_unit.grid(row=1, column=3, padx=5)

        btn_frame = tk.Frame(input_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        tk.Button(btn_frame, text="Save", command=self.save_material).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_inputs).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_material).pack(side="left", padx=5)

        # List Frame
        list_frame = tk.Frame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("ID", "Category", "Name", "Cost", "Unit")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        materials = APIClient.get_materials()
        for m in materials:
            self.tree.insert("", "end", values=(m['id'], m['category'], m['name'], m['unit_cost'], m['unit_type']))

    def save_material(self):
        name = self.entry_name.get()
        category = self.combo_category.get()
        cost = self.entry_cost.get()
        unit = self.entry_unit.get()

        if not name or not cost:
            messagebox.showerror("Error", "Name and Cost are required")
            return

        try:
            data = {
                "name": name,
                "category": category,
                "unit_cost": float(cost),
                "unit_type": unit
            }
            # Look for existing ID in selection to update, else add
            selected = self.tree.selection()
            if selected:
                 # Update mode could be inferred, but commonly 'Save' adds new unless explicit update. 
                 # For simplicity here: Clear selection acts as 'Add New', selected acts as 'Update'.
                 m_id = self.tree.item(selected[0])['values'][0]
                 APIClient.update_material(m_id, data)
            else:
                APIClient.add_material(data)
            
            self.refresh_list()
            self.clear_inputs()
            
        except ValueError:
             messagebox.showerror("Error", "Cost must be a number")
        except Exception as e:
             messagebox.showerror("Error", f"Failed: {e}")

    def delete_material(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        if messagebox.askyesno("Confirm", "Delete material?"):
            m_id = self.tree.item(selected[0])['values'][0]
            try:
                APIClient.delete_material(m_id)
                self.refresh_list()
                self.clear_inputs()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        # 0=id, 1=cat, 2=name, 3=cost, 4=unit
        self.clear_inputs()
        self.entry_name.insert(0, values[2])
        self.combo_category.set(values[1])
        self.entry_cost.insert(0, values[3])
        self.entry_unit.insert(0, values[4])

    def clear_inputs(self):
        self.tree.selection_remove(self.tree.selection())
        self.entry_name.delete(0, tk.END)
        self.combo_category.set("")
        self.entry_cost.delete(0, tk.END)
        self.entry_unit.delete(0, tk.END)
