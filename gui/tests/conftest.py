import pytest
import tkinter as tk

@pytest.fixture(scope="session")
def tk_root():
    """Create a single shared Tk root window for the entire test session."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    try:
        root.destroy()
    except tk.TclError:
        pass
