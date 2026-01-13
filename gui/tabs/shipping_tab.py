import tkinter as tk
from tkinter import ttk, messagebox
import threading
from services.shipping_service import ChitChatsProvider

class ShippingTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.provider = ChitChatsProvider()
        
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        # -- Left Panel: Inputs --
        self.left_panel = tk.Frame(self)
        self.left_panel.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        
        self.create_recipient_section()
        self.create_package_section()
        
        # -- Right Panel: Results --
        self.right_panel = tk.LabelFrame(self, text="Shipping Rates", padx=5, pady=5)
        self.right_panel.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        
        self.create_results_table()
        
        # Action Buttons
        btn_frame = tk.Frame(self.left_panel)
        btn_frame.pack(fill="x", pady=20)
        
        tk.Button(btn_frame, text="Get Rates", command=self.get_rates_thread, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_inputs).pack(side="left", fill="x", expand=True, padx=5)

    def create_recipient_section(self):
        frame = tk.LabelFrame(self.left_panel, text="1. Recipient Address", padx=5, pady=5)
        frame.pack(fill="x", pady=5)
        
        entries = [
            ("Name*", "entry_name"),
            ("Address*", "entry_address"),
            ("City*", "entry_city"),
            ("Province (Code)", "entry_prov"),
            ("Postal Code*", "entry_postal"),
            ("Country Code* (e.g. US, CA, IL)", "entry_country")
        ]
        
        for i, (label, var_name) in enumerate(entries):
            tk.Label(frame, text=f"{label}:").grid(row=i, column=0, sticky="w", pady=2)
            entry = tk.Entry(frame)
            entry.grid(row=i, column=1, sticky="ew", padx=5, pady=2)
            setattr(self, var_name, entry)
            
        frame.columnconfigure(1, weight=1)

    def create_package_section(self):
        frame = tk.LabelFrame(self.left_panel, text="2. Package Details", padx=5, pady=5)
        frame.pack(fill="x", pady=5)
        
        # Dimensions
        tk.Label(frame, text="Size* (L x W x H cm):").grid(row=0, column=0, sticky="w")
        dim_frame = tk.Frame(frame)
        dim_frame.grid(row=0, column=1, sticky="w")
        self.entry_len = tk.Entry(dim_frame, width=5)
        self.entry_len.pack(side="left", padx=2)
        tk.Label(dim_frame, text="x").pack(side="left")
        self.entry_width = tk.Entry(dim_frame, width=5)
        self.entry_width.pack(side="left", padx=2)
        tk.Label(dim_frame, text="x").pack(side="left")
        self.entry_height = tk.Entry(dim_frame, width=5)
        self.entry_height.pack(side="left", padx=2)
        
        # Weight
        tk.Label(frame, text="Weight* (g):").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_weight = tk.Entry(frame, width=10)
        self.entry_weight.grid(row=1, column=1, sticky="w", padx=5)
        
        # Value & Desc
        tk.Label(frame, text="Value* (USD):").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_value = tk.Entry(frame, width=10)
        self.entry_value.grid(row=2, column=1, sticky="w", padx=5)
        
        tk.Label(frame, text="Description*:").grid(row=3, column=0, sticky="w", pady=5)
        self.entry_desc = tk.Entry(frame)
        self.entry_desc.grid(row=3, column=1, sticky="ew", padx=5)
        frame.columnconfigure(1, weight=1)

    def create_results_table(self):
        cols = ("Carrier", "Service", "Cost (USD)", "Est. Delivery")
        self.tree = ttk.Treeview(self.right_panel, columns=cols, show="headings")
        self.tree.pack(fill="both", expand=True)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)

    def get_rates_thread(self):
        threading.Thread(target=self.get_rates, daemon=True).start()

    def get_rates(self):
        # Gather data
        try:
            recipient = {
                "name": self.entry_name.get(),
                "address_1": self.entry_address.get(),
                "city": self.entry_city.get(),
                "province_code": self.entry_prov.get(),
                "postal_code": self.entry_postal.get(),
                "country_code": self.entry_country.get()
            }
            
            package = {
                "size_x": float(self.entry_len.get() or 0),
                "size_y": float(self.entry_width.get() or 0),
                "size_z": float(self.entry_height.get() or 0),
                "weight": float(self.entry_weight.get() or 0),
                "value": float(self.entry_value.get() or 0),
                "description": self.entry_desc.get()
            }
            
            # Call Service
            rates = self.provider.get_rates(recipient, package)
            
            # Update UI (Main Thread)
            self.after(0, self.display_rates, rates)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for dimensions and weight.")

    def display_rates(self, rates):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        if not rates:
             messagebox.showinfo("Result", "No rates found.")
             return
             
        # Check for error
        if len(rates) == 1 and "error" in rates[0]:
            messagebox.showerror("Shipping Error", rates[0]["error"])
            return
             


        for rate in rates:
            # Chit Chats response mapping
            carrier = rate.get("postage_carrier_type", rate.get("postage_carrier", "Unknown")).replace("_", " ").title()
            service = rate.get("postage_description", rate.get("postage_type_description", "Standard"))
            
            # Use payment_amount for total cost, fallback to postage_fee or postage_label_price
            cost_val = rate.get("payment_amount", rate.get("postage_fee", rate.get("postage_label_price", "0.00")))
            cost = f"${cost_val}"
            
            est = rate.get("delivery_time_description", rate.get("estimated_delivery_date", "N/A"))
            
            self.tree.insert("", "end", values=(carrier, service, cost, est))

    def clear_inputs(self):
        entries = [
            self.entry_name, self.entry_address, self.entry_city, self.entry_prov, 
            self.entry_postal, self.entry_country, self.entry_len, self.entry_width, 
            self.entry_height, self.entry_weight, self.entry_value, self.entry_desc
        ]
        for e in entries:
            e.delete(0, tk.END)
        
        for item in self.tree.get_children():
            self.tree.delete(item)
