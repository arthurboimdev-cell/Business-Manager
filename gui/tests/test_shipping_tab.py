import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
import sys

# Mocking tkinter modules to avoid GUI display issues during tests
class MockFrame:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.children = []
    def grid(self, **kwargs): pass
    def pack(self, **kwargs): pass
    def place(self, **kwargs): pass
    def columnconfigure(self, *args, **kwargs): pass
    def rowconfigure(self, *args, **kwargs): pass
    def destroy(self): pass
    def bind(self, *args, **kwargs): pass
    def winfo_id(self): return 12345
    def get_children(self): return self.children
    def delete(self, *args): pass
    def insert(self, *args, **kwargs): pass
    def heading(self, *args, **kwargs): pass
    def column(self, *args, **kwargs): pass
    def after(self, ms, func, *args): func(*args) # Execute immediately
    def __str__(self): return "MockFrame"

mock_tk = MagicMock()
mock_tk.Frame = MockFrame
mock_tk.LabelFrame = MockFrame
mock_tk.Tk = MockFrame
mock_tk.DoubleVar = MagicMock
mock_tk.StringVar = MagicMock
mock_tk.IntVar = MagicMock
mock_tk.Button = MagicMock
mock_tk.Label = MagicMock
mock_tk.Entry.side_effect = lambda *args, **kwargs: MagicMock()

sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['ttkbootstrap'] = MagicMock()
sys.modules['ttkbootstrap.constants'] = MagicMock()

import gui.tabs.shipping_tab
from importlib import reload
reload(gui.tabs.shipping_tab)
from gui.tabs.shipping_tab import ShippingTab

@pytest.fixture
def shipping_tab():
    with patch('gui.tabs.shipping_tab.ChitChatsProvider') as MockProvider:
        parent = MagicMock()
        tab = ShippingTab(parent)
        yield tab, MockProvider.return_value

def test_get_rates_calls_provider(shipping_tab):
    tab, mock_provider = shipping_tab
    
    # Setup inputs
    tab.entry_name.get.return_value = "Jane Doe"
    tab.entry_country.get.return_value = "CA"
    tab.entry_weight.get.return_value = "100"
    
    # Mock return
    mock_provider.get_rates.return_value = [
        {"postage_carrier": "TestCarrier", "postage_label_price": "10.00"}
    ]
    
    # Trigger action
    tab.get_rates()
    
    # Verify provider called
    mock_provider.get_rates.assert_called_once()
    recipient = mock_provider.get_rates.call_args[0][0]
    package = mock_provider.get_rates.call_args[0][1]
    
    assert recipient['name'] == "Jane Doe"
    assert recipient['country_code'] == "CA"
    assert package['weight'] == 100.0
    
    # Verify Treeview updated (Mocked)
    # Since tree is mocked, we check if delete was called on children (clearing)
    # and insert was called with new data
    assert tab.tree.insert.called
    args = tab.tree.insert.call_args[1]
    assert "Testcarrier" in args['values'][0]

def test_invalid_input_handles_error(shipping_tab):
    tab, mock_provider = shipping_tab
    
    # Setup invalid non-numeric weight
    tab.entry_weight.get.return_value = "abc"
    
    with patch('gui.tabs.shipping_tab.messagebox.showerror') as mock_error:
        tab.get_rates()
        mock_error.assert_called_once()
        assert "valid numeric values" in mock_error.call_args[0][1]
        
    mock_provider.get_rates.assert_not_called()

def test_clear_inputs(shipping_tab):
    tab, _ = shipping_tab
    
    tab.clear_inputs()
    
    # Verify all entries cleared
    tab.entry_name.delete.assert_called_with(0, mock_tk.END)
    tab.entry_weight.delete.assert_called_with(0, mock_tk.END)
    # Verify tree cleared
    # tab.tree.delete called for children
