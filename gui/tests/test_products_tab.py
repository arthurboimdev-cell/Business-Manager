
import pytest
from unittest.mock import MagicMock, patch
import sys

# Define explicit Mock classes
class MockFrame:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.winfo_children_val = []
    def grid(self, **kwargs): pass
    def pack(self, **kwargs): pass
    def place(self, **kwargs): pass
    def columnconfigure(self, *args, **kwargs): pass
    def rowconfigure(self, *args, **kwargs): pass
    def destroy(self): pass
    def bind(self, *args, **kwargs): pass
    def winfo_id(self): return 12345
    def winfo_children(self): return self.winfo_children_val

# Mock tkinter module structure
mock_tk = MagicMock()
mock_tk.Frame = MockFrame
mock_tk.LabelFrame = MockFrame
mock_tk.Toplevel = MockFrame 
mock_tk.Tk = MockFrame
# Ensure Entry returns a NEW mock each time
mock_tk.Entry.side_effect = lambda *args, **kwargs: MagicMock()

# We need to ensure these are in sys.modules BEFORE import/reload
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.filedialog'] = MagicMock()

# We also need to mock the new components to avoid ImportErrors or complex mocking logic?
# Actually we want to test integration with ProductForm, so we should allow it to be imported.
# But ProductForm imports tkinter too, which is mocked. So it should be fine.

import gui.forms.product_form
import gui.dialogs.create_product_dialog
import gui.tabs.products_tab
from importlib import reload

# KEY FIX: Reload modules in dependency order so they pick up the mocked tkinter
reload(gui.forms.product_form)
reload(gui.dialogs.create_product_dialog)
reload(gui.tabs.products_tab)

from gui.tabs.products_tab import ProductsTab

@pytest.fixture
def mock_api():
    # Patch in all locations where APIClient is imported
    with patch('gui.tabs.products_tab.APIClient') as mock_1, \
         patch('gui.forms.product_form.APIClient') as mock_2, \
         patch('gui.dialogs.create_product_dialog.APIClient') as mock_3:
        
        # Configure valid returns for all mocks to behave consistently
        for m in [mock_1, mock_2, mock_3]:
            m.get_products.return_value = []
            m.get_product_images.return_value = []
            m.add_product.return_value = {'id': 999}
            
        yield mock_1 # Return one, they should all be mocks now

@pytest.fixture
def products_tab(mock_api):
    parent = MagicMock()
    tab = ProductsTab(parent)
    return tab

def test_ui_widgets_created(products_tab):
    """Test that form widgets are created via the embedded form"""
    assert products_tab.form.entry_sku is not None
    assert products_tab.form.entry_price is not None
    assert products_tab.form.lbl_main_img_preview is not None
    assert products_tab.form.gallery_frame is not None

def test_update_product_logic(products_tab, mock_api):
    """Test that update logic gets data from form and calls API"""
    # Explicitly mock the tree to ensure we control selection behavior
    products_tab.tree = MagicMock()
    
    # CASE 1: No Selection
    products_tab.tree.selection.return_value = [] # Empty list -> False
    
    # Patch specifically where it is used
    with patch('gui.tabs.products_tab.messagebox.showwarning') as mock_warn:
        products_tab.update_product()
        mock_warn.assert_called_with("Warning", "No product selected to update")

    # CASE 2: Valid Selection
    products_tab.tree.selection.return_value = ["item1"]
    products_tab.tree.item.return_value = {'values': [123]} # Product ID 123
    
    # Mock Form Data
    products_tab.form.get_data = MagicMock(return_value={"id": 123, "title": "Updated Product"})
    
    with patch('gui.tabs.products_tab.messagebox.showinfo') as mock_info:
        products_tab.update_product()
        
        mock_api.update_product.assert_called_with(123, {"id": 123, "title": "Updated Product"})
        mock_info.assert_called_with("Success", "Product Updated")

def test_on_select_populates_form(products_tab):
    """Test that selecting a product calls load_product on form"""
    # Mock selection
    mock_tree = products_tab.tree
    mock_tree.selection.return_value = ["item1"]
    mock_tree.item.return_value = {'values': [101]}
    
    # Mock product list
    mock_product = {'id': 101, 'title': 'Test Pro'}
    products_tab.products = [mock_product]
    
    # Mock form.load_product
    products_tab.form.load_product = MagicMock()
    
    products_tab.on_product_select(None)
    
    products_tab.form.load_product.assert_called_with(mock_product)

def test_form_calculate_cogs(products_tab):
    """Test the calculation logic inside the embedded form"""
    form = products_tab.form
    
    # Mock entries on the form
    form.entry_wax_g.get.return_value = "100"
    form.entry_wax_rate.get.return_value = "0.05"
    form.entry_labor_time.get.return_value = "60"
    form.entry_labor_rate.get.return_value = "20"
    
    # Clear others to defaults
    for entry in [form.entry_fragrance_g, form.entry_frag_rate, form.entry_wick_rate, 
                  form.entry_container_rate, form.entry_box, form.entry_wrap, form.entry_biz_card]:
        entry.get.return_value = "0"
        
    form.entry_wick_qty.get.return_value = "1"
    form.entry_container_qty.get.return_value = "1"
    form.entry_box_qty.get.return_value = "1"
    
    # Run calculation
    total = form.calculate_cogs()
    
    # 100*0.05 = 5.00
    # (60/60)*20 = 20.00
    # Total = 25.00
    assert total == 25.00
    
    # Verify Tree
    inserts = form.cogs_tree.insert.call_args_list
    # Check for Labor
    labor_found = False
    for call in inserts:
        vals = call.kwargs.get('values')
        if vals and vals[0] == "Labor":
            assert vals[3] == "$20.00"
            labor_found = True
    assert labor_found

def test_static_calculation_logic():
    """Test the static method used by ProductsTab for the list view"""
    data = {
        'wax_weight_g': 100, 'wax_rate': 0.10,
        'labor_time': 30, 'labor_rate': 20.00
    }
    # 10.00 + 10.00 = 20.00
    cost = ProductsTab.calculate_product_cost_static(data)
    assert abs(cost - 20.00) < 0.001
