import pytest
import tkinter as tk
from gui.GUI import TransactionGUI


def test_gui_initialization(tk_root):
    gui = TransactionGUI(tk_root)
    assert gui.master == tk_root
