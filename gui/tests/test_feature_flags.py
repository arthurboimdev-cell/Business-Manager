import sys
from unittest.mock import MagicMock, patch
import unittest

# --- Top Level Mocking ---
# We must do this BEFORE importing the module under test to ensure it picks up the mocks
mock_tk = MagicMock()
mock_tk.Tk = MagicMock
mock_tk.Frame = MagicMock
mock_tk.Label = MagicMock
mock_tk.Entry = MagicMock
mock_tk.Button = MagicMock
mock_tk.Menu = MagicMock
mock_tk.StringVar = MagicMock

# Submodules
mock_ttk = MagicMock()
mock_tk.ttk = mock_ttk

# Assign to sys.modules
sys.modules['tkinter'] = mock_tk
sys.modules['tkinter.font'] = MagicMock()
sys.modules['tkinter.ttk'] = mock_ttk
sys.modules['tkinter.filedialog'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()

# Mock ttkbootstrap
mock_tb = MagicMock()

# MagicMock as a base class causes issues because its __init__ expects specific mock-config args.
# We use a DummyBase that accepts anything.
class DummyBase:
    def __init__(self, *args, **kwargs):
        self.children = {}
    def title(self, *args): pass
    def geometry(self, *args): pass
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def add(self, *args, **kwargs): pass
    def forget(self, *args, **kwargs): pass
    def mainloop(self): pass
    def columnconfigure(self, *args, **kwargs): pass
    def bind(self, *args, **kwargs): pass

mock_tb.Window = DummyBase
mock_tb.Notebook = DummyBase
mock_tb.Frame = DummyBase
# For other widgets not subclassed, MagicMock is fine if instantiated, 
# but consistent DummyBase is safer if they are used as base classes or instantiated with complex args.
mock_tb.Treeview = DummyBase
mock_tb.Scrollbar = DummyBase
mock_tb.Label = DummyBase
mock_tb.Entry = DummyBase
mock_tb.Button = DummyBase
mock_tb.Radiobutton = DummyBase
mock_tb.Combobox = DummyBase

sys.modules['ttkbootstrap'] = mock_tb
sys.modules['ttkbootstrap.constants'] = MagicMock()

# Now import the class under test
import gui.views
from importlib import reload
# Reload to ensure it binds to our fresh mocks if tests are re-run or imported multiple times
reload(gui.views)
from gui.views import MainWindow

class TestFeatureFlags(unittest.TestCase):
    def setUp(self):
        # Patch ShippingTab to avoid it trying to do things
        self.patcher_shipping = patch('gui.views.ShippingTab')
        self.MockShippingTab = self.patcher_shipping.start()
        
        # Patch matplotlib imports inside charts which might be imported by views
        # actually views imports AnalyticsFrame from gui.charts
        # so we might need to patch that too if it causes issues, but top level sys.modules usually handles it?
        # Let's hope so.

    def tearDown(self):
        self.patcher_shipping.stop()

    def test_all_enabled(self):
        features = {
            "product_inventory": True,
            "materials_inventory": True,
            "shipping": True
        }
        window = MainWindow("Test", features=features)
        
        self.assertTrue(hasattr(window, 'tab_products'), "Products tab should exist")
        self.assertTrue(hasattr(window, 'tab_materials'), "Materials tab should exist")
        self.assertTrue(hasattr(window, 'tab_shipping'), "Shipping tab should exist")

    def test_all_disabled(self):
        features = {
            "product_inventory": False,
            "materials_inventory": False,
            "shipping": False
        }
        window = MainWindow("Test", features=features)
        
        self.assertFalse(hasattr(window, 'tab_products'), "Products tab should NOT exist")
        self.assertFalse(hasattr(window, 'tab_materials'), "Materials tab should NOT exist")
        self.assertFalse(hasattr(window, 'tab_shipping'), "Shipping tab should NOT exist")

    def test_products_only(self):
        features = {
            "product_inventory": True,
            "materials_inventory": False,
            "shipping": False
        }
        window = MainWindow("Test", features=features)
        
        self.assertTrue(hasattr(window, 'tab_products'))
        self.assertFalse(hasattr(window, 'tab_materials'))
        self.assertFalse(hasattr(window, 'tab_shipping'))

    def test_materials_only(self):
        features = {
            "product_inventory": False,
            "materials_inventory": True,
            "shipping": False
        }
        window = MainWindow("Test", features=features)
        
        self.assertFalse(hasattr(window, 'tab_products'))
        self.assertTrue(hasattr(window, 'tab_materials'))
        self.assertFalse(hasattr(window, 'tab_shipping'))
        
    def test_shipping_only(self):
        features = {
            "product_inventory": False,
            "materials_inventory": False,
            "shipping": True
        }
        window = MainWindow("Test", features=features)
        
        self.assertFalse(hasattr(window, 'tab_products'))
        self.assertFalse(hasattr(window, 'tab_materials'))
        self.assertTrue(hasattr(window, 'tab_shipping'))
