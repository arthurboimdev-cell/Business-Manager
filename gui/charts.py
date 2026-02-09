import tkinter as tk
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import services.utils as utils
from datetime import datetime

class AnalyticsFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        self.transactions = []
        
        # --- Control Frame (Year Selection) ---
        self.control_frame = tb.Frame(self)
        self.control_frame.pack(fill='x', pady=(0, 10))
        
        tb.Label(self.control_frame, text="Select Year:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
        
        self.year_var = tk.StringVar()
        self.year_combo = tb.Combobox(
            self.control_frame, 
            textvariable=self.year_var, 
            state="readonly", 
            width=10,
            bootstyle="primary"
        )
        self.year_combo.pack(side=tk.LEFT, padx=5)
        self.year_combo.bind("<<ComboboxSelected>>", self.on_year_change)

        # --- Chart ---
        # A single figure for the Monthly Chart
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Use tight_layout for better automatic spacing
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind to configure event to handle window resizing
        self.bind("<Configure>", self._on_resize)

    def on_year_change(self, event):
        self.refresh_charts(self.transactions, keep_year=True)

    def refresh_charts(self, transactions, keep_year=False):
        self.transactions = transactions
        self.ax.clear()

        # 1. Update Year Options
        years = set()
        for t in transactions:
            try:
                date_str = str(t['transaction_date'])
                if len(date_str) >= 4:
                    years.add(date_str[:4])
            except:
                pass
        
        current_year = str(datetime.now().year)
        years.add(current_year)
        years.add("2025")  # Always include 2025
        
        sorted_years = sorted(list(years), reverse=True)
        self.year_combo['values'] = sorted_years
        
        # Determine Selected Year
        if not keep_year or self.year_var.get() not in sorted_years:
            if current_year in sorted_years:
                self.year_var.set(current_year)
            elif sorted_years:
                self.year_var.set(sorted_years[0])
            else:
                self.year_var.set("2024") # Fallback

        if not self.year_combo.get():
             self.year_combo.current(0)

        selected_year = int(self.year_var.get())

        # 2. Get Data
        breakdown = utils.TransactionUtils.calculate_monthly_breakdown(transactions, selected_year)

        months = range(1, 13)
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        incomes = [breakdown[m]['income'] for m in months]
        expenses = [breakdown[m]['expense'] for m in months]

        # 3. Plot Grouped Bar Chart
        x = list(range(len(months))) # 0..11
        width = 0.35
        
        # Manual offsets for x-axis
        x_income = [i - width/2 for i in x]
        x_expense = [i + width/2 for i in x]

        self.ax.bar(x_income, incomes, width, label='Income', color='#2ecc71')
        self.ax.bar(x_expense, expenses, width, label='Expense', color='#e74c3c')

        # Add Value Labels
        for i, v in enumerate(incomes):
            if v > 0:
                self.ax.text(x_income[i], v, f"{int(v)}", ha='center', va='bottom', fontsize=8)
        
        for i, v in enumerate(expenses):
            if v > 0:
                self.ax.text(x_expense[i], v, f"{int(v)}", ha='center', va='bottom', fontsize=8)

        # Calculate year balance
        total_income = sum(incomes)
        total_expense = sum(expenses)
        balance = total_income - total_expense

        title_text = f"Income vs Expenses - {selected_year}\nBalance: ${balance:,.2f}"
        self.ax.set_title(title_text, fontsize=12)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(month_labels)
        self.ax.legend()
        
        # Grid for easier reading
        self.ax.yaxis.grid(True, linestyle='--', alpha=0.7)

        self.canvas.draw()
    
    def _on_resize(self, event):
        """Handle window resize events to ensure chart scales properly"""
        try:
            self.fig.tight_layout(pad=3.0)
            self.canvas.draw_idle()
        except:
            pass  # Ignore errors during resize
