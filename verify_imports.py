import sys
try:
    print("Importing tkinter...")
    import tkinter as tk
    print("Importing ttkbootstrap...")
    import ttkbootstrap as tb
    print("Importing matplotlib...")
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    print("Importing views...")
    from gui.views import MainWindow
    print("Importing controller...")
    from gui.controller import TransactionController
    print("All imports successful.")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
