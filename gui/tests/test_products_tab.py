import pytest
from unittest.mock import MagicMock, patch
import sys
import importlib

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

@pytest.fixture
def mock_tk_env():
    # Mock tkinter module structure
    mock_tk = MagicMock()
    mock_tk.Frame = MockFrame
    mock_tk.LabelFrame = MockFrame
    mock_tk.Toplevel = MockFrame 
    mock_tk.Tk = MockFrame
    # Ensure Entry returns a NEW mock each time
    mock_tk.Entry.side_effect = lambda *args, **kwargs: MagicMock()

    modules_to_patch = {
        'tkinter': mock_tk,
        'tkinter.ttk': MagicMock(),
        'tkinter.messagebox': MagicMock(),
        'tkinter.filedialog': MagicMock()
    }
    
    with patch.dict(sys.modules, modules_to_patch):
        # Reload modules so they pick up the mocked tkinter
        import gui.forms.product_form
        import gui.dialogs.create_product_dialog
        import gui.tabs.products_tab
        
        importlib.reload(gui.forms.product_form)
        importlib.reload(gui.dialogs.create_product_dialog)
        importlib.reload(gui.tabs.products_tab)
        
        yield
        
    # Cleanup/Restore relies on patch.dict context manager, 
    # BUT we must reload again to restore real tkinter types if other tests need them?
    # Actually, other tests running in same process might need real modules.
    # So we should reload them back to original state?
    # Yes, otherwise they stick with the mocked imports if sys.modules restored but the 'gui.*' modules still hold references to mocks.
    # Ideally, we reload on exit.
    import gui.forms.product_form
    import gui.dialogs.create_product_dialog
    import gui.tabs.products_tab
    importlib.reload(gui.forms.product_form)
    importlib.reload(gui.dialogs.create_product_dialog)
    importlib.reload(gui.tabs.products_tab)


@pytest.fixture
def mock_api():
    # Patch in all locations where APIClient is imported
    # Note: We must patch strictly where it is used.
    # Since we are using reloaded modules in the fixture, we might need to match those.
    with patch('gui.tabs.products_tab.APIClient') as mock_1, \
         patch('gui.forms.product_form.APIClient') as mock_2, \
         patch('gui.dialogs.create_product_dialog.APIClient') as mock_3:
        
        # Configure valid returns for all mocks to behave consistently
        for m in [mock_1, mock_2, mock_3]:
            m.get_products.return_value = []
            m.get_product_images.return_value = []
            m.add_product.return_value = {'id': 999}
            
        yield mock_1 

@pytest.fixture
def products_tab(mock_tk_env, mock_api):
    # Import INSIDE fixture or ensure it refers to the reloaded module
    from gui.tabs.products_tab import ProductsTab
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
    form.entry_wax_rate.get.return_value = "50" # $50/kg = $0.05/g
    form.entry_labor_time.get.return_value = "60"
    form.entry_labor_rate.get.return_value = "20"
    
    # Clear others to defaults
    for entry in [form.entry_fragrance_g, form.entry_frag_rate, form.entry_wick_rate, 
                  form.entry_container_rate, form.entry_second_container_g, form.entry_second_container_rate, 
                  form.entry_box, form.entry_wrap, form.entry_biz_card]:
        entry.get.return_value = "0"
        
    form.entry_wick_qty.get.return_value = "1"
    form.entry_container_qty.get.return_value = "1"
    form.entry_box_qty.get.return_value = "1"
    
    # Run calculation
    total = form.calculate_cogs()
    
    # 100*0.05 = 5.00
    # (60/60)*20 = 20.00
    # Total = 25.00
    # Total = 25.00
    assert total == pytest.approx(25.00, 0.01)
    
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
    # NOTE: This test does not use products_tab fixture, so it runs without the mock_tk_env!
    # Which is GOOD because we want to test the static method which is pure logic.
    # BUT, we need to import ProductsTab. 
    # If the module was poisoned by previous import, it might be bad?
    # But since we fixed the collection-time poison, it should be clean.
    
    from gui.tabs.products_tab import ProductsTab
    
    data = {
        'wax_weight_g': 100, 'wax_rate': 100.00, # Updated rate to match expected calc
        'labor_time': 30, 'labor_rate': 20.00
    }
    # Wax: 100g * (100 $/kg / 1000) = 100 * 0.1 = 10.00
    # Labor: 30/60 * 20 = 10.00
    # Total: 20.00
    cost = ProductsTab.calculate_product_cost_static(data)
    assert abs(cost - 20.00) < 0.001
