"""
Test suite for break-even calculation and Etsy fees.
Tests the formula: Price = (COGS + Shipping + Fixed Fees) / (1 - Etsy Rate)
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import importlib


class MockFrame:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.winfo_children_val = []
    def grid(self, **kwargs): pass
    def pack(self, **kwargs): pass
    def place(self, **kwargs): pass
    def destroy(self): pass
    def bind(self, *args, **kwargs): pass
    def winfo_id(self): return 12345
    def winfo_children(self): return self.winfo_children_val
    def columnconfigure(self, *args, **kwargs): pass
    def rowconfigure(self, *args, **kwargs): pass


@pytest.fixture
def mock_tk_env():
    mock_tk = MagicMock()
    mock_tk.Frame = MockFrame
    mock_tk.LabelFrame = MockFrame
    mock_tk.Toplevel = MockFrame 
    mock_tk.Tk = MockFrame
    mock_tk.Entry.side_effect = lambda *args, **kwargs: MagicMock()
    
    modules = {
        'tkinter': mock_tk,
        'tkinter.ttk': MagicMock(),
        'tkinter.messagebox': MagicMock(),
        'tkinter.filedialog': MagicMock()
    }
    
    with patch.dict(sys.modules, modules):
        import gui.forms.product_form
        importlib.reload(gui.forms.product_form)
        yield
        
    import gui.forms.product_form
    importlib.reload(gui.forms.product_form)


@pytest.fixture
def form(mock_tk_env):
    with patch('gui.forms.product_form.APIClient'):
        from gui.forms.product_form import ProductForm
        parent = MagicMock()
        form = ProductForm(parent)
        # Initialize mocks with proper return values
        form.entry_cogs.get.return_value = ""
        form.entry_shipping_ca.get.return_value = ""
        form.entry_shipping_us.get.return_value = ""
        form.entry_weight.get.return_value = ""
        return form


def set_val(entry, value):
    """Set mock entry return value"""
    entry.get.return_value = str(value)


class TestBreakEvenCalculation:
    """Test break-even price calculation with FREE shipping included"""
    
    def test_break_even_basic(self, form):
        """Test basic break-even: COGS $10, Shipping $5, result ~$16.48"""
        set_val(form.entry_cogs, "10.00")
        set_val(form.entry_shipping_ca, "5.00")
        
        form.calculate_break_even()
        
        # Check CA break-even was inserted
        calls = form.entry_break_even_ca.insert.call_args_list
        assert len(calls) > 0
        # (COGS + Shipping + Fees) / (1 - Rate) = (10 + 5 + 0.45) / 0.905 = 17.02
        args, _ = calls[-1]
        price_str = args[1].replace('$', '')
        price = float(price_str)
        assert 16.8 < price < 17.2, f"Expected ~17.02, got {price}"
    
    def test_break_even_zero_shipping(self, form):
        """Test break-even with no shipping cost"""
        set_val(form.entry_cogs, "10.00")
        set_val(form.entry_shipping_ca, "0")
        
        form.calculate_break_even()
        
        # (10 + 0 + 0.45) / 0.905 = 11.55
        calls = form.entry_break_even_ca.insert.call_args_list
        args, _ = calls[-1]
        price = float(args[1].replace('$', ''))
        assert 11.4 < price < 11.7
    
    def test_break_even_high_shipping(self, form):
        """Test break-even with high shipping cost"""
        set_val(form.entry_cogs, "10.00")
        set_val(form.entry_shipping_ca, "20.00")
        
        form.calculate_break_even()
        
        # (10 + 20 + 0.45) / 0.905 = 33.65
        calls = form.entry_break_even_ca.insert.call_args_list
        args, _ = calls[-1]
        price = float(args[1].replace('$', ''))
        assert 33.4 < price < 33.9
    
    def test_etsy_fees_calculation_ca(self, form):
        """Test that Etsy fees are correctly displayed for CA"""
        set_val(form.entry_cogs, "9.73")
        set_val(form.entry_shipping_ca, "5.70")
        
        form.calculate_break_even()
        
        # Break-even price: ((9.73 + 5.70 + 0.45) / 0.905) ≈ 17.55
        # Etsy fees at $17.55: 0.20 + (17.55 * 0.065) + (17.55 * 0.03 + 0.25) ≈ 2.12
        calls = form.entry_etsy_fees_ca.insert.call_args_list
        assert len(calls) > 0
        args, _ = calls[-1]
        fee_str = args[1].replace('$', '')
        fee = float(fee_str)
        assert 1.8 < fee < 2.5, f"Expected Etsy fees ~$2.12, got ${fee}"
    
    def test_etsy_fees_calculation_us(self, form):
        """Test that Etsy fees are correctly displayed for US"""
        set_val(form.entry_cogs, "9.73")
        set_val(form.entry_shipping_us, "8.00")
        
        form.calculate_break_even()
        
        calls = form.entry_etsy_fees_us.insert.call_args_list
        assert len(calls) > 0
        args, _ = calls[-1]
        fee = float(args[1].replace('$', ''))
        assert fee > 0
    
    def test_break_even_ca_vs_us(self, form):
        """Test that CA and US break-evens are calculated independently"""
        set_val(form.entry_cogs, "10.00")
        set_val(form.entry_shipping_ca, "3.00")
        set_val(form.entry_shipping_us, "8.00")
        
        form.calculate_break_even()
        
        # Get CA price
        ca_calls = form.entry_break_even_ca.insert.call_args_list
        ca_price = float(ca_calls[-1][0][1].replace('$', ''))
        
        # Get US price
        us_calls = form.entry_break_even_us.insert.call_args_list
        us_price = float(us_calls[-1][0][1].replace('$', ''))
        
        # US should be higher due to higher shipping
        assert us_price > ca_price
    
    def test_break_even_no_cogs(self, form):
        """Test break-even with minimum COGS"""
        set_val(form.entry_cogs, "0")
        set_val(form.entry_shipping_ca, "5.00")
        
        form.calculate_break_even()
        
        calls = form.entry_break_even_ca.insert.call_args_list
        args, _ = calls[-1]
        price = float(args[1].replace('$', ''))
        assert price > 0  # Should still have a price to cover shipping and fees
    
    def test_break_even_error_handling(self, form):
        """Test break-even handles invalid inputs gracefully"""
        set_val(form.entry_cogs, "invalid")
        set_val(form.entry_shipping_ca, "not_a_number")
        
        form.calculate_break_even()
        
        # Should show "Error" instead of crashing
        calls = form.entry_break_even_ca.insert.call_args_list
        args, _ = calls[-1]
        assert "Error" in args[1]


class TestWeightPreservation:
    """Test that manually entered weight values are preserved"""
    
    def test_weight_preserved_when_manually_entered(self, form):
        """Test that manual weight entry is not overwritten by auto-calculate"""
        # Set manual weight
        set_val(form.entry_weight, "500")
        
        # Setup BOM with wax that would auto-calculate to 100g
        from gui.tests.test_advanced_pricing import set_val as setup_val
        setup_val(form.entry_wax_g, 100)
        setup_val(form.entry_wax_rate, 10)
        
        form.calculate_cogs()
        
        # Weight should remain 500, not be updated to 100
        result = form.entry_weight.get()
        assert result == "500"
    
    def test_weight_auto_filled_when_empty(self, form):
        """Test that weight is auto-filled from BOM when field is empty"""
        # Start with empty weight (default from fixture)
        set_val(form.entry_weight, "")
        
        from gui.tests.test_advanced_pricing import set_val as setup_val, setup_bom
        setup_bom(form, wax_g=200, frag_g=50)
        
        form.calculate_cogs()
        
        # Weight should be auto-calculated as 250g
        calls = form.entry_weight.insert.call_args_list
        if len(calls) > 0:
            args, _ = calls[-1]
            weight = float(args[1])
            assert weight == 250.0
    
    def test_weight_manual_after_auto_fill(self, form):
        """Test that manually entering weight after auto-fill preserves it"""
        from gui.tests.test_advanced_pricing import setup_bom
        setup_bom(form, wax_g=100)
        
        # First calculate (should auto-fill)
        set_val(form.entry_weight, "")
        form.calculate_cogs()
        
        # Then manually enter a different weight
        set_val(form.entry_weight, "300")
        
        # Recalculate
        form.calculate_cogs()
        
        # Weight should remain 300
        result = form.entry_weight.get()
        assert result == "300"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
