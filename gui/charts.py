import tkinter as tk
import ttkbootstrap as tb
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import services.utils as utils

class AnalyticsFrame(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)

        # Matplotlib Figures
        self.fig_pie = Figure(figsize=(5, 4), dpi=100)
        self.ax_pie = self.fig_pie.add_subplot(111)

        self.fig_bar = Figure(figsize=(5, 4), dpi=100)
        self.ax_bar = self.fig_bar.add_subplot(111)

        # Canvas
        self.canvas_pie = FigureCanvasTkAgg(self.fig_pie, self)
        self.canvas_pie.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas_bar = FigureCanvasTkAgg(self.fig_bar, self)
        self.canvas_bar.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    def refresh_charts(self, transactions):
        self.ax_pie.clear()
        self.ax_bar.clear()

        if not transactions:
            self.canvas_pie.draw()
            self.canvas_bar.draw()
            return
            
        summary = utils.TransactionUtils.calculate_summary(transactions)
        
        # --- Pie Chart: Income vs Expense ---
        labels = ['Income', 'Expense']
        sizes = [summary['total_income'], summary['total_expense']]
        colors = ['#2ecc71', '#e74c3c'] # Green, Red
        
        # Avoid pie crash if both 0
        if sum(sizes) > 0:
            self.ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            self.ax_pie.set_title("Income vs Expense")
        else:
            self.ax_pie.text(0.5, 0.5, "No Data", ha='center')

        # --- Bar Chart: Income/Expense ---
        self.ax_bar.bar(labels, sizes, color=colors)
        self.ax_bar.set_title("Financial Overview")
        
        self.canvas_pie.draw()
        self.canvas_bar.draw()
