"""
Shipping Tab for AurumCandles.
Shows estimated shipping costs (Chitchats, Etsy Labels, Canada Post)
for all products and provides an interactive calculator.
All prices in CAD. Ship from: L4N 6G5 (Barrie, ON).
"""

import tkinter as tk
from tkinter import ttk, messagebox

from client.api_client import APIClient
from services.shipping_service import (
    get_all_shipping_estimates,
    get_cheapest_by_destination,
    calculate_savings,
    format_shipping_summary,
    DEFAULT_PACKAGING_WEIGHT_G,
)


class ShippingTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.products = []

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_calculator_panel()
        self._build_product_list()
        self._build_results_panel()
        self.refresh()

    # ──────────────────────────────────────────────────────────────────
    # UI Builders
    # ──────────────────────────────────────────────────────────────────

    def _build_calculator_panel(self):
        frame = tk.LabelFrame(self, text="Shipping Calculator  (All prices CA$, ship from Barrie ON)", padx=8, pady=8)
        frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))

        # Row 0 — weight + packaging
        tk.Label(frame, text="Item Weight (g):").grid(row=0, column=0, sticky="w", padx=(0, 4))
        self.entry_weight = tk.Entry(frame, width=9)
        self.entry_weight.grid(row=0, column=1, sticky="w", padx=(0, 14))

        tk.Label(frame, text="Packaging (g):").grid(row=0, column=2, sticky="w", padx=(0, 4))
        self.entry_packaging = tk.Entry(frame, width=7)
        self.entry_packaging.grid(row=0, column=3, sticky="w", padx=(0, 14))
        self.entry_packaging.insert(0, str(DEFAULT_PACKAGING_WEIGHT_G))

        # Buttons
        tk.Button(frame, text="Calculate", command=self.calculate_manual,
                  bg="#2196F3", fg="white").grid(row=0, column=4, padx=4)
        tk.Button(frame, text="Clear", command=self._clear_calculator).grid(row=0, column=5, padx=4)

        # Shipping weight display
        self.lbl_shipping_weight = tk.Label(frame, text="", fg="gray")
        self.lbl_shipping_weight.grid(row=0, column=6, padx=10, sticky="w")

        for entry in [self.entry_weight, self.entry_packaging]:
            entry.bind("<Return>", lambda e: self.calculate_manual())

    def _build_product_list(self):
        frame = tk.LabelFrame(self, text="Products — Cheapest Shipping per Destination (Chitchats / Etsy / Canada Post)", padx=8, pady=8)
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=4)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        # Toolbar
        toolbar = tk.Frame(frame)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tk.Label(toolbar, text="Search:").pack(side="left")
        self.entry_search = tk.Entry(toolbar, width=20)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self._filter_product_list())
        tk.Button(toolbar, text="Refresh", command=self.refresh,
                  bg="#607D8B", fg="white").pack(side="left", padx=5)
        tk.Label(toolbar, text="(Click a row to see full breakdown below)",
                 fg="gray", font=("Arial", 8)).pack(side="left", padx=10)

        # Treeview — columns
        cols = ("ID", "Title", "SKU", "Weight (g)", "Ship Wt (g)",
                "Chitchats CA", "Chitchats US", "Etsy Label CA", "Etsy Label US",
                "Canada Post CA", "Canada Post US")
        self.product_tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        self.product_tree.grid(row=1, column=0, sticky="nsew")

        widths = [35, 180, 65, 65, 65, 85, 85, 85, 85, 85, 85]
        for col, w in zip(cols, widths):
            self.product_tree.heading(col, text=col)
            self.product_tree.column(col, width=w, anchor="center")
        self.product_tree.column("Title", anchor="w")

        # Tags for cheapest highlighting
        self.product_tree.tag_configure("normal", background="white")
        self.product_tree.tag_configure("warning", background="#FFF3E0")  # orange-ish for low margin

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.product_tree.yview)
        sb.grid(row=1, column=1, sticky="ns")
        self.product_tree.configure(yscrollcommand=sb.set)

        self.product_tree.bind("<<TreeviewSelect>>", self._on_product_select)
        self.product_tree.bind("<Double-1>", self._on_product_select)

    def _build_results_panel(self):
        frame = tk.LabelFrame(self, text="Rate Breakdown & Savings", padx=8, pady=8)
        frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(4, 10))
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # Left: rate table
        left = tk.Frame(frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(0, weight=1)

        self.results_label = tk.Label(left, text="Select a product or enter a weight above.", fg="gray", anchor="w")
        self.results_label.pack(fill="x", pady=(0, 4))

        cols = ("Carrier", "Destination", "Cost (CA$)", "Note")
        self.results_tree = ttk.Treeview(left, columns=cols, show="headings", height=7)
        self.results_tree.pack(fill="both", expand=True)
        col_widths = [100, 150, 90, 280]
        for col, w in zip(cols, col_widths):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=w, anchor="center")
        self.results_tree.column("Note", anchor="w")
        self.results_tree.tag_configure("cheapest", background="#E8F5E9", foreground="#2E7D32")
        self.results_tree.tag_configure("chitchats", background="#E3F2FD", foreground="#1565C0")
        self.results_tree.tag_configure("normal", background="white")

        # Right: savings summary
        right = tk.LabelFrame(frame, text="Chitchats Savings", padx=8, pady=8)
        right.grid(row=0, column=1, sticky="nsew")

        self.savings_labels = {}
        savings_rows = [
            ("save_vs_etsy_ca",  "vs Etsy Label (CA):"),
            ("save_vs_etsy_us",  "vs Etsy Label (US):"),
            ("save_vs_cp_ca",    "vs Canada Post (CA):"),
            ("save_vs_cp_us",    "vs Canada Post (US):"),
        ]
        for i, (key, text) in enumerate(savings_rows):
            tk.Label(right, text=text, anchor="w").grid(row=i, column=0, sticky="w", pady=2)
            lbl = tk.Label(right, text="—", anchor="e", fg="green", font=("Arial", 10, "bold"))
            lbl.grid(row=i, column=1, sticky="e", padx=(10, 0), pady=2)
            self.savings_labels[key] = lbl

        right.columnconfigure(1, weight=1)

    # ──────────────────────────────────────────────────────────────────
    # Data / Logic
    # ──────────────────────────────────────────────────────────────────

    def refresh(self):
        try:
            self.products = APIClient.get_products()
        except Exception as e:
            self.products = []
            messagebox.showwarning("Shipping Tab", f"Could not load products: {e}")
        self._populate_product_list(self.products)

    def _populate_product_list(self, products):
        for row in self.product_tree.get_children():
            self.product_tree.delete(row)

        for p in products:
            weight_g = float(p.get("weight_g") or 0)
            if weight_g <= 0:
                self.product_tree.insert("", "end", values=(
                    p.get("id", ""), p.get("title", ""), p.get("sku", ""),
                    "—", "—", "—", "—", "—", "—", "—", "—"))
                continue

            pkg = DEFAULT_PACKAGING_WEIGHT_G
            from services.shipping_service import (
                get_shipping_weight_g, calculate_chitchats_ca, calculate_chitchats_us,
                calculate_etsy_label_ca, calculate_etsy_label_us,
                calculate_canada_post_ca, calculate_canada_post_us,
            )
            sw = get_shipping_weight_g(weight_g, pkg)

            self.product_tree.insert("", "end", values=(
                p.get("id", ""),
                p.get("title", ""),
                p.get("sku", ""),
                f"{weight_g:.0f}",
                f"{sw:.0f}",
                f"${calculate_chitchats_ca(sw):.2f}",
                f"${calculate_chitchats_us(sw):.2f}",
                f"${calculate_etsy_label_ca(sw):.2f}",
                f"${calculate_etsy_label_us(sw):.2f}",
                f"${calculate_canada_post_ca(sw):.2f}",
                f"${calculate_canada_post_us(sw):.2f}",
            ))

    def _filter_product_list(self):
        term = self.entry_search.get().strip().lower()
        if not term:
            self._populate_product_list(self.products)
            return
        filtered = [
            p for p in self.products
            if term in (p.get("title") or "").lower()
            or term in (p.get("sku") or "").lower()
        ]
        self._populate_product_list(filtered)

    def _on_product_select(self, event=None):
        selected = self.product_tree.selection()
        if not selected:
            return
        values = self.product_tree.item(selected[0])["values"]
        p_id = str(values[0])
        product = next((p for p in self.products if str(p.get("id")) == p_id), None)
        if not product:
            return

        weight_g = float(product.get("weight_g") or 0)
        if weight_g <= 0:
            return

        self.entry_weight.delete(0, tk.END)
        self.entry_weight.insert(0, str(weight_g))
        self.calculate_manual(product_name=product.get("title", ""))

    def _clear_calculator(self):
        self.entry_weight.delete(0, tk.END)
        self.entry_packaging.delete(0, tk.END)
        self.entry_packaging.insert(0, str(DEFAULT_PACKAGING_WEIGHT_G))
        self.lbl_shipping_weight.config(text="")
        self._clear_results()

    def _clear_results(self):
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)
        self.results_label.config(text="Select a product or enter a weight above.", fg="gray")
        for lbl in self.savings_labels.values():
            lbl.config(text="—")

    def calculate_manual(self, product_name=None):
        try:
            item_weight_g = float(self.entry_weight.get() or 0)
        except ValueError:
            messagebox.showwarning("Input Error", "Weight must be a number.")
            return
        if item_weight_g <= 0:
            messagebox.showwarning("Input Error", "Please enter a weight greater than 0.")
            return

        try:
            pkg = float(self.entry_packaging.get() or DEFAULT_PACKAGING_WEIGHT_G)
        except ValueError:
            pkg = DEFAULT_PACKAGING_WEIGHT_G

        from services.shipping_service import get_shipping_weight_g
        sw = get_shipping_weight_g(item_weight_g, pkg)
        self.lbl_shipping_weight.config(text=f"Shipping weight: {sw:.0f}g ({sw/1000:.3f} kg)")

        estimates = get_all_shipping_estimates(item_weight_g, pkg)

        # Label
        label = f"Results for: {product_name}" if product_name else "Results for custom package"
        label += f"  |  {item_weight_g:.0f}g item + {pkg:.0f}g packaging = {sw:.0f}g shipped"
        self.results_label.config(text=label, fg="black")

        # Results tree
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        cheapest_cost = estimates[0]["cost"] if estimates else None
        for est in estimates:
            is_cheapest = (est["cost"] == cheapest_cost)
            is_chitchats = ("Chitchats" in est["carrier"])
            if is_cheapest:
                tag = "cheapest"
            elif is_chitchats:
                tag = "chitchats"
            else:
                tag = "normal"

            prefix = "* " if is_cheapest else "  "
            self.results_tree.insert("", "end", tags=(tag,), values=(
                est["carrier"],
                est["destination"],
                f"${est['cost']:.2f}",
                f"{prefix}{est['note']}",
            ))

        # Savings
        savings = calculate_savings(item_weight_g, pkg)
        for key, lbl in self.savings_labels.items():
            val = savings.get(key, 0)
            lbl.config(text=f"${val:.2f}", fg="green" if val > 0 else "red")
