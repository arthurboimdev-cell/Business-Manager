import sys
import pytest
from unittest.mock import MagicMock, patch
from importlib import reload
import unittest

@pytest.fixture
def mock_gui_modules():
    """Patches tkinter and ttkbootstrap for feature flag tests"""
    # Prepare mocks
    mock_tk = MagicMock()
    mock_tk.Tk = MagicMock
    mock_tk.Frame = MagicMock
    mock_tk.Label = MagicMock
    mock_tk.Entry = MagicMock
    mock_tk.Button = MagicMock
    mock_tk.Menu = MagicMock
    mock_tk.StringVar = MagicMock
    
    mock_ttk = MagicMock()
    mock_tk.ttk = mock_ttk
    
    # Mock ttkbootstrap
    mock_tb = MagicMock()
    
    class DummyBase:
        def __init__(self, *args, **kwargs):
            self.children = {}
            self.tk = MagicMock()
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
    mock_tb.Treeview = DummyBase
    mock_tb.Scrollbar = DummyBase
    mock_tb.Label = DummyBase
    mock_tb.Entry = DummyBase
    mock_tb.Button = DummyBase
    mock_tb.Radiobutton = DummyBase
    mock_tb.Combobox = DummyBase
    
    with patch.dict(sys.modules, {
        'tkinter': mock_tk,
        'tkinter.font': MagicMock(),
        'tkinter.ttk': mock_ttk,
        'tkinter.filedialog': MagicMock(),
        'tkinter.messagebox': MagicMock(),
        'tkinter.simpledialog': MagicMock(),
        'ttkbootstrap': mock_tb,
        'ttkbootstrap.constants': MagicMock(),
        'gui.charts': MagicMock()
    }):
        import gui.views
        reload(gui.views)
        yield gui.views
        if 'gui.views' in sys.modules:
             del sys.modules['gui.views']

@pytest.mark.usefixtures("mock_gui_modules")
class TestFeatureFlags(unittest.TestCase):
    def setUp(self):
        # We need the class to use the mocked modules, so we import it inside the test methods or here
        # But unittest setUp doesn't easily access the fixture yield.
        # So we can just rely on the side-effect of the fixture (patching sys.modules)
        # However, for the class to be available, we need to import it.
        # Since the fixture reloads gui.views, we can import it here.
        pass

    def get_main_window_class(self):
        # Helper to get the class from the currently loaded (mocked) module
        import gui.views
        return gui.views.MainWindow
        
    def test_all_enabled(self):
        self._test_features({
            "product_inventory": True,
            "materials_inventory": True,
            "marketplace": True
        })

    def _test_features(self, features):
        MainWindow = self.get_main_window_class()
        
        # Patch MarketplaceTab and ShippingTab to avoid them trying to do things
        with patch('gui.views.MarketplaceTab') as MockMarketplaceTab, \
             patch('gui.views.ShippingTab') as MockShippingTab:
             window = MainWindow("Test", features=features)
             
             if features.get("product_inventory"):
                 self.assertTrue(hasattr(window, 'tab_products'))
             else:
                 self.assertFalse(hasattr(window, 'tab_products'))
                 
             if features.get("materials_inventory"):
                 self.assertTrue(hasattr(window, 'tab_materials'))
             else:
                 self.assertFalse(hasattr(window, 'tab_materials'))

             if features.get("marketplace"):
                 self.assertTrue(hasattr(window, 'tab_marketplace'))
             else:
                 self.assertFalse(hasattr(window, 'tab_marketplace'))

    def test_all_disabled(self):
        self._test_features({
            "product_inventory": False,
            "materials_inventory": False,
            "marketplace": False
        })
        
    def test_products_only(self):
        self._test_features({
            "product_inventory": True,
            "materials_inventory": False,
            "marketplace": False
        })

    def test_materials_only(self):
        self._test_features({
            "product_inventory": False,
            "materials_inventory": True,
            "marketplace": False
        })
