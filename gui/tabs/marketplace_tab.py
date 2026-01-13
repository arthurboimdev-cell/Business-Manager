import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class MarketplaceTab(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # -- Calculator Panel --
        self.calc_panel = tb.LabelFrame(self, text="Etsy Fee Calculator")
        self.calc_panel.pack(fill="x", expand=False, padx=10, pady=10)
        
        # Inputs
        self.create_input_field("Sale Price ($)", "price", 0)
        self.create_input_field("Shipping Charged ($)", "shipping", 1)
        self.create_input_field("Item Cost ($)", "cost", 2)
        
        # Offsite Ads Checkbox
        self.var_offsite = tk.BooleanVar(value=False)
        tb.Checkbutton(self.calc_panel, text="Offsite Ads (15%)", variable=self.var_offsite, bootstyle="round-toggle").grid(row=3, column=0, columnspan=2, pady=5)
        
        # Calculate Button
        self.btn_calc = tb.Button(self.calc_panel, text="Calculate", bootstyle="primary", command=self.calculate)
        self.btn_calc.grid(row=4, column=0, columnspan=2, pady=15, sticky="ew")
        
        # Results
        self.create_result_field("Listing Fee", "fee_listing", 5)
        self.create_result_field("Transaction Fee (6.5%)", "fee_transaction", 6)
        self.create_result_field("Payment Fee (3% + 0.25)", "fee_payment", 7)
        self.create_result_field("Offsite Ads Fee (15%)", "fee_offsite", 8)
        
        tb.Separator(self.calc_panel).grid(row=9, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.create_result_field("Total Fees", "fee_total", 10, is_bold=True)
        self.create_result_field("Net Profit", "net_profit", 11, is_bold=True, color="success")
        self.create_result_field("Margin", "margin", 12)

        self.calc_panel.columnconfigure(1, weight=1)

    def create_input_field(self, label, var_name, row):
        tb.Label(self.calc_panel, text=label).grid(row=row, column=0, sticky="w", pady=5)
        entry = tb.Entry(self.calc_panel)
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=5)
        setattr(self, f"entry_{var_name}", entry)

    def create_result_field(self, label, var_name, row, is_bold=False, color=None):
        font = ("Helvetica", 10, "bold") if is_bold else None
        bootstyle = color if color else "default"
        
        tb.Label(self.calc_panel, text=label, font=font).grid(row=row, column=0, sticky="w", pady=2)
        lbl_val = tb.Label(self.calc_panel, text="$0.00", font=font, bootstyle=bootstyle)
        lbl_val.grid(row=row, column=1, sticky="e", padx=10, pady=2)
        setattr(self, f"lbl_{var_name}", lbl_val)

    def calculate(self):
        try:
            p_val = self.entry_price.get()
            print(f"DEBUG: Price raw='{p_val}'")
            price = float(p_val or 0)
            shipping = float(self.entry_shipping.get() or 0)
            cost = float(self.entry_cost.get() or 0)
            
            total_revenue = price + shipping
            
            # Etsy Fees (Approximate standard)
            # Listing: $0.20 USD fixed
            # Transaction: 6.5% of (Price + Shipping)
            # Payment Proc: 3% + $0.25
            
            fee_listing = 0.20
            fee_transaction = total_revenue * 0.065
            fee_payment = (total_revenue * 0.03) + 0.25
            
            # Offsite Ads
            fee_offsite = 0.0
            if self.var_offsite.get():
                fee_offsite = total_revenue * 0.15
            
            total_fees = fee_listing + fee_transaction + fee_payment + fee_offsite
            net_profit = total_revenue - total_fees - cost
            
            margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Update UI
            self.lbl_fee_listing.config(text=f"${fee_listing:.2f}")
            self.lbl_fee_transaction.config(text=f"${fee_transaction:.2f}")
            self.lbl_fee_payment.config(text=f"${fee_payment:.2f}")
            self.lbl_fee_offsite.config(text=f"${fee_offsite:.2f}")
            self.lbl_fee_total.config(text=f"${total_fees:.2f}")
            
            self.lbl_net_profit.config(text=f"${net_profit:.2f}", bootstyle="success" if net_profit > 0 else "danger")
            self.lbl_margin.config(text=f"{margin:.1f}%")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")
