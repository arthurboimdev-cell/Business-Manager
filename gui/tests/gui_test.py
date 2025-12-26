import pytest
import tkinter as tk
from gui.GUI import TransactionGUI

@pytest.fixture
def tk_root():
    """Create a real hidden Tk root window for testing and destroy it after."""
    root = tk.Tk()
    root.withdraw()  # Hide the window
    yield root
    root.destroy()

def test_gui_initialization(tk_root):
    gui = TransactionGUI(tk_root)
    assert gui.master == tk_root
