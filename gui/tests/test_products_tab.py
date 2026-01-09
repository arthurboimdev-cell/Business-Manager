
import pytest
from unittest.mock import MagicMock, patch
import sys

# Define explicit Mock classes to avoid MagicMock inheritance recursion issues
class MockFrame:
    def __init__(self, master=None, **kwargs):
        self.master = master
    def grid(self, **kwargs): pass
    def pack(self, **kwargs): pass
    def place(self, **kwargs): pass
    def columnconfigure(self, *args, **kwargs): pass
    def rowconfigure(self, *args, **kwargs): pass
    def destroy(self): pass
    def bind(self, *args, **kwargs): pass
    def winfo_id(self): return 12345

# Mock tkinter module structure
mock_tk = MagicMock()
mock_tk.Frame = MockFrame
mock_tk.LabelFrame = MockFrame
mock_tk.Tk = MockFrame
# Ensure Entry returns a NEW mock each time
mock_tk.Entry.side_effect = lambda *args, **kwargs: MagicMock()

# We need to ensure these are in sys.modules BEFORE import/reload
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

import gui.tabs.products_tab
from importlib import reload
reload(gui.tabs.products_tab)
from gui.tabs.products_tab import ProductsTab

@pytest.fixture
def mock_api():
    with patch('gui.tabs.products_tab.APIClient') as mock:
        mock.get_materials.return_value = []
        mock.get_products.return_value = []
        yield mock

@pytest.fixture
def products_tab(mock_api):
    parent = MagicMock()
    # Now ProductsTab inherits from MockFrame, so init is safe
    tab = ProductsTab(parent)
    return tab

def test_ui_widgets_created(products_tab):
    """Test that entry widgets are created"""
    assert products_tab.entry_sku is not None
    assert products_tab.entry_upc is not None
    assert products_tab.entry_box is not None
    assert products_tab.entry_wrap is not None

def test_save_product_logic(products_tab, mock_api):
    """Test that save logic reads from the mocked entries"""
    # Configure mock entries (which are MagicMocks created by tk.Entry calls)
    products_tab.entry_name.get.return_value = "Test Product"
    products_tab.entry_sku.get.return_value = "SKU-999"
    products_tab.entry_upc.get.return_value = "UPC-888"
    products_tab.entry_stock.get.return_value = "10"
    
    # Mock numeric fields validation (defaults)
    products_tab.entry_l.get.return_value = "0"
    products_tab.entry_w.get.return_value = "0"
    products_tab.entry_h.get.return_value = "0"
    products_tab.entry_weight.get.return_value = "0"
    products_tab.entry_wax_g.get.return_value = "0"
    products_tab.entry_fragrance_g.get.return_value = "0"
    products_tab.entry_box.get.return_value = "0"
    products_tab.entry_wrap.get.return_value = "0"
    
    # Suppress messagebox
    with patch('gui.tabs.products_tab.messagebox.showinfo') as mock_info:
        products_tab.add_product()
        
        # Verify API called with correct data
        mock_api.add_product.assert_called_once()
        args = mock_api.add_product.call_args[0][0]
        
        assert args['name'] == "Test Product"
        assert args['sku'] == "SKU-999"
        assert args['upc'] == "UPC-888"

def test_on_select_populates_fields(products_tab):
    """Test that selecting a product populates the mocked entries"""
    # Mock selected item
    mock_tree = products_tab.tree
    mock_tree.selection.return_value = ["item1"]
    mock_tree.item.return_value = {'values': [101]} # ID 101
    
    # Mock product data
    mock_product = {
        'id': 101, 
        'name': 'Loaded Product',
        'sku': 'LOADED-SKU',
        'upc': 'LOADED-UPC',
        'stock_quantity': 5
    }
    products_tab.products = [mock_product]
    
    products_tab.on_product_select(None)
    
    # Verify insert called on mocked entries
    products_tab.entry_name.insert.assert_called_with(0, 'Loaded Product')
    products_tab.entry_sku.insert.assert_called_with(0, 'LOADED-SKU')
    products_tab.entry_upc.insert.assert_called_with(0, 'LOADED-UPC')
