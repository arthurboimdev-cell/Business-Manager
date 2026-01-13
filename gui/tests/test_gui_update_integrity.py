import pytest
from unittest.mock import MagicMock, patch
import tkinter as tk
from gui.tabs.products_tab import ProductsTab
from client.api_client import APIClient

@pytest.fixture
def products_tab(tk_root):
    # Mock APIClient methods before creating tab to avoid network calls
    with patch('client.api_client.APIClient.get_products', return_value=[]):
        tab = ProductsTab(tk_root)
        return tab

def test_list_view_cost_calculation_uses_kg_logic(products_tab):
    """
    Verify that the product list calculates cost using $/kg logic (dividing by 1000)
    for Wax and Fragrance, instead of treating input rate as $/g.
    """
    # Mock product data from API
    # Wax: 100g @ $50/kg = $5.00
    # Labor: 60min @ $20/h = $20.00
    # Total Expected: $25.00
    mock_product = {
        "id": 1,
        "title": "Test Candle",
        "sku": "SKU-1",
        "selling_price": 50.00,
        "wax_weight_g": 100,
        "wax_rate": 50, # $/kg
        "fragrance_weight_g": 0,
        "fragrance_rate": 0,
        "labor_time": 60,
        "labor_rate": 20
    }
    
    # Inject into tab
    with patch('client.api_client.APIClient.get_products', return_value=[mock_product]):
        products_tab.refresh_product_list()
        
    # Get item from tree
    item_id = products_tab.tree.get_children()[0]
    values = products_tab.tree.item(item_id)['values']
    
    # values: ID, Title, SKU, Stock, COST, Price
    captured_cost_str = values[4] # e.g. "$25.00"
    captured_cost = float(captured_cost_str.replace("$", ""))
    
    # Check if logic is correct
    # If incorrect (old logic), it would be 100 * 50 = 5000 + 20 = 5020
    assert captured_cost == 25.00, f"Expected $25.00, got {captured_cost_str}. Logic mismatch!"

def test_update_flow_field_by_field(products_tab):
    """
    Simulate selecting a product, changing fields, and clicking Update.
    Verify API is called with new values.
    """
    mock_product = {
        "id": 1,
        "title": "Old Title",
        "sku": "SKU-1",
        "selling_price": 10.00,
        "wax_weight_g": 100,
        "wax_rate": 50,
        "container_quantity": 1
    }
    
    # 1. Setup List
    with patch('client.api_client.APIClient.get_products', return_value=[mock_product]):
        products_tab.refresh_product_list()
        
    # 2. Select the product
    item_id = products_tab.tree.get_children()[0]
    products_tab.tree.selection_set(item_id)
    # Trigger selection event manually (or rely on bind if tk mock supports it, explicit is safer)
    products_tab.on_product_select(None)
    
    # 3. Verify Form Loaded
    assert products_tab.form.entry_title.get() == "Old Title"
    
    # 4. Change Fields (Field by Field)
    products_tab.form.entry_title.delete(0, "end")
    products_tab.form.entry_title.insert(0, "New Title")
    
    products_tab.form.entry_sku.delete(0, "end")
    products_tab.form.entry_sku.insert(0, "NEW-SKU")
    
    # Change BOM: Wax Rate 50 -> 60
    products_tab.form.entry_wax_rate.delete(0, "end")
    products_tab.form.entry_wax_rate.insert(0, "60")
    
    # 5. Click Update
    with patch('client.api_client.APIClient.update_product') as mock_update:
        products_tab.update_product()
        
        # 6. Verify API Call
        assert mock_update.called
        args, _ = mock_update.call_args
        p_id_arg = args[0]
        data_arg = args[1]
        
        assert str(p_id_arg) == "1"
        assert data_arg['title'] == "New Title"
        assert data_arg['sku'] == "NEW-SKU"
        assert data_arg['wax_rate'] == 60.0
