import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from gui.forms.product_form import ProductForm

# Mock APIClient to avoid connection errors during init
@patch('gui.forms.product_form.APIClient')
def test_pricing_calculation(mock_api):
    # Mock config_data
    test_config = {
        "pricing": {
            "enabled": True,
            "markup_max": 5.0,
            "markup_min": 1.5,
            "decay_factor": 20.0
        },
        "ui": {"labels": {}, "buttons": {}} # Minimal needed?
    }
    
    with patch('config.config.config_data', test_config):
        # Setup Tkinter root
        try:
            root = tk.Tk()
        except tk.TclError:
            pytest.skip("Skipping GUI test: Tkinter not available (headless?)")
        
        # Instantiate Form
        form = ProductForm(root)
        
        # Helper to set value
        def set_val(entry, val):
            entry.delete(0, "end")
            entry.insert(0, str(val))
            
        # Case 1: Low Cost
        # Material: Wax 100g @ $20/kg = $2.00
        # Labor: 0
        set_val(form.entry_wax_g, 100)
        set_val(form.entry_wax_rate, 20) # $20/kg
        set_val(form.entry_labor_time, 0)
        
        # Trigger Calculation
        form.calculate_cogs()
        rec_val_str = form.entry_rec_price.get()
        print(f"Low Cost Rec Price: {rec_val_str}")
        assert "$" in rec_val_str
        
        # Case 2: High Cost
        # Material: $100
        set_val(form.entry_wax_g, 1000)
        set_val(form.entry_wax_rate, 100) # $100 cost
        
        form.calculate_cogs()
        rec_val_str = form.entry_rec_price.get()
        print(f"High Cost Rec Price: {rec_val_str}")
        val_part = rec_val_str.split(" ")[0].replace("$", "")
        # Cost 100. M = 1.5 + 3.5 / (1 + 5) = 1.5 + 0.583 = 2.083. Price ~208.33
        assert 208.0 < float(val_part) < 209.0
        
        # Case 3: With Labor
        # Material $10, Labor $10
        set_val(form.entry_wax_g, 1000)
        set_val(form.entry_wax_rate, 10) # $10
        set_val(form.entry_labor_time, 60) # 1 hr
        set_val(form.entry_labor_rate, 10) # $10/hr
        
        form.calculate_cogs()
        rec_val_str = form.entry_rec_price.get()
        print(f"Labor Case Rec Price: {rec_val_str}")
        val_part = rec_val_str.split(" ")[0].replace("$", "")
        # Mat 10. M = 1.5 + 3.5/(1+0.5) = 1.5 + 2.33 = 3.83.
        # Price = 10*3.83 + 10 = 48.33
        assert 48.0 < float(val_part) < 49.0
        
        root.destroy()
