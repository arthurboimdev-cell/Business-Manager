import pytest
from unittest.mock import MagicMock, patch
import sys

# Dummy base class for widgets
class DummyBase:
    def __init__(self, *args, **kwargs):
        pass
    def pack(self, *args, **kwargs): pass
    def grid(self, *args, **kwargs): pass
    def columnconfigure(self, *args, **kwargs): pass

# Factories to return clean Mocks
def mock_widget_factory(*args, **kwargs):
    m = MagicMock()
    # Ensure get exists and returns something by default to avoid issues
    m.get.return_value = ""
    return m

mock_tk = MagicMock()
mock_tk.Frame = DummyBase
mock_tk.LabelFrame = DummyBase
mock_tk.Label = mock_widget_factory
mock_tk.Entry = mock_widget_factory
mock_tk.Button = mock_widget_factory
mock_tk.Checkbutton = mock_widget_factory
mock_tk.IntVar = MagicMock
mock_tk.BooleanVar = MagicMock
mock_tk.StringVar = MagicMock
mock_tk.DoubleVar = MagicMock

mock_tb = MagicMock()
mock_tb.Frame = DummyBase 
mock_tb.LabelFrame = DummyBase
mock_tb.Label = mock_widget_factory
mock_tb.Entry = mock_widget_factory
mock_tb.Button = mock_widget_factory
mock_tb.Checkbutton = mock_widget_factory
mock_tb.Separator = MagicMock

@pytest.fixture
def marketplace_tab_module():
    mock_mb = MagicMock()
    # Ensure mock_tk.messagebox points to the same mock as sys.modules['tkinter.messagebox']
    mock_tk.messagebox = mock_mb
    
    with patch.dict(sys.modules, {
        'tkinter': mock_tk,
        'tkinter.ttk': MagicMock(),
        'tkinter.messagebox': mock_mb,
        'ttkbootstrap': mock_tb,
        'ttkbootstrap.constants': MagicMock()
    }):
        import gui.tabs.marketplace_tab
        from importlib import reload
        reload(gui.tabs.marketplace_tab)
        yield gui.tabs.marketplace_tab

@pytest.fixture
def marketplace_tab(marketplace_tab_module):
    # Instantiate the tab with a mock parent
    MarketplaceTab = marketplace_tab_module.MarketplaceTab
    
    # We need to simulate the UI creation
    # The __init__ calls methods that create widgets. 
    # Since we mocked the widget classes, they return Mocks.
    
    parent = MagicMock()
    tab = MarketplaceTab(parent)
    
    # We need to attach mocked entry and label widgets regarding the logic
    # The CreateInput methods use setattr, so they should exist on 'tab'
    # BUT, since we mocked 'tb.Entry', tab.entry_price is a Mock object.
    
    # Inject var_offsite mock since we mocked BooleanVar class logic away
    tab.var_offsite = MagicMock()
    tab.var_offsite.get.return_value = False # Default off
    
    yield tab

def test_initialization(marketplace_tab):
    assert hasattr(marketplace_tab, 'entry_price')
    assert hasattr(marketplace_tab, 'btn_calc')

def test_calculation_logic(marketplace_tab):
    # Setup inputs on the mock widgets
    # .get() should return values
    marketplace_tab.entry_price.get.return_value = "100"
    marketplace_tab.entry_shipping.get.return_value = "0"
    marketplace_tab.entry_cost.get.return_value = "20"
    
    # Run calculation
    marketplace_tab.calculate()
    
    # Verify outputs
    # The code calls .config(text=...) on labels
    
    # helper
    def get_text(mock_lbl):
        args = mock_lbl.config.call_args
        if args:
            return args.kwargs.get('text')
        return None

    assert get_text(marketplace_tab.lbl_fee_listing) == "$0.20"
    assert get_text(marketplace_tab.lbl_fee_transaction) == "$6.50"
    assert get_text(marketplace_tab.lbl_fee_payment) == "$3.25"
    assert get_text(marketplace_tab.lbl_fee_total) == "$9.95"
    assert get_text(marketplace_tab.lbl_net_profit) == "$70.05"
    # Python rounding of 70.05 might result in 70.0%
    assert get_text(marketplace_tab.lbl_margin) == "70.0%" # 70.05 rounded to 1 decimal place

def test_calculation_with_shipping(marketplace_tab):
    marketplace_tab.entry_price.get.return_value = "50"
    marketplace_tab.entry_shipping.get.return_value = "10"
    marketplace_tab.entry_cost.get.return_value = "10"
    
    marketplace_tab.calculate()
    
    # Revenue: 60
    # Fees: 0.20 + 3.90 (6.5%) + 2.05 (3%+0.25) = 6.15
    # Net: 60 - 6.15 - 10 = 43.85
    
    def get_text(mock_lbl):
        args = mock_lbl.config.call_args
        return args.kwargs.get('text') if args else None

    assert get_text(marketplace_tab.lbl_fee_total) == "$6.15"
    assert get_text(marketplace_tab.lbl_net_profit) == "$43.85"

def test_calculation_with_offsite_ads(marketplace_tab):
    marketplace_tab.entry_price.get.return_value = "100"
    marketplace_tab.entry_shipping.get.return_value = "0"
    marketplace_tab.entry_cost.get.return_value = "20"
    
    # Enable offsite ads
    marketplace_tab.var_offsite.get.return_value = True
    
    marketplace_tab.calculate()
    
    # Revenue: 100
    # Base Fees: 0.20 + 6.50 + 3.25 = 9.95
    # Offsite Fee: 15.00 (15% of 100)
    # Total Fees: 24.95
    # Net: 100 - 24.95 - 20 = 55.05
    
    def get_text(mock_lbl):
        args = mock_lbl.config.call_args
        return args.kwargs.get('text') if args else None

    assert get_text(marketplace_tab.lbl_fee_offsite) == "$15.00"
    assert get_text(marketplace_tab.lbl_fee_total) == "$24.95"
    assert get_text(marketplace_tab.lbl_net_profit) == "$55.05"

def test_invalid_input(marketplace_tab):
    marketplace_tab.entry_price.get.return_value = "abc"
    
    # The module imports messagebox from tkinter
    # We mocked tkinter.messagebox in sys.modules
    
    mock_msgbox = sys.modules['tkinter.messagebox']
    
    marketplace_tab.calculate()
    
    print(f"DEBUG: MsgBox Calls: {mock_msgbox.mock_calls}")
    print(f"DEBUG: MsgBox ShowError Calls: {mock_msgbox.showerror.mock_calls}")
    
    mock_msgbox.showerror.assert_called_once()
    assert "valid numeric values" in mock_msgbox.showerror.call_args[0][1]
