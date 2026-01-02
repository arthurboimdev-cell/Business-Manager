import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from gui.GUI import TransactionGUI


@pytest.fixture
def mock_gui(tk_root):
    """Create a TransactionGUI instance with mocked db calls"""
    with patch("gui.GUI.read_transactions") as mock_read, \
         patch("gui.GUI.write_transaction"), \
         patch("gui.GUI.delete_transaction"):
        
        # Setup initial data
        mock_read.return_value = [
            {"id": 1, "transaction_date": "2024-01-01", "description": "Apple", "quantity": 10, "price": 5.0, "total": 50.0, "transaction_type": "income", "supplier": "A"},
            {"id": 2, "transaction_date": "2024-02-01", "description": "Banana", "quantity": 5, "price": 2.0, "total": 10.0, "transaction_type": "expense", "supplier": "B"},
            {"id": 3, "transaction_date": "2023-12-31", "description": "Carrot", "quantity": 20, "price": 1.0, "total": 20.0, "transaction_type": "income", "supplier": "A"},
        ]
        
        gui = TransactionGUI(tk_root, table="test_table")
        # Ensure transactions are loaded
        gui.transactions = mock_read.return_value 
        return gui

def test_sort_by_date(mock_gui):
    """Test sorting by date column"""
    # First click: Ascending
    mock_gui.sort_by_column("date")
    dates = [t["transaction_date"] for t in mock_gui.transactions]
    assert dates == ["2023-12-31", "2024-01-01", "2024-02-01"]
    assert mock_gui.sort_descending is False

    # Second click: Descending
    mock_gui.sort_by_column("date")
    dates = [t["transaction_date"] for t in mock_gui.transactions]
    assert dates == ["2024-02-01", "2024-01-01", "2023-12-31"]
    assert mock_gui.sort_descending is True

def test_sort_by_price_numeric(mock_gui):
    """Test numeric sorting for price"""
    # First click: Ascending
    mock_gui.sort_by_column("price")
    prices = [t["price"] for t in mock_gui.transactions]
    assert prices == [1.0, 2.0, 5.0]

    # Second click: Descending
    mock_gui.sort_by_column("price")
    prices = [t["price"] for t in mock_gui.transactions]
    assert prices == [5.0, 2.0, 1.0]

def test_sort_by_description_string(mock_gui):
    """Test string sorting for description"""
    mock_gui.sort_by_column("description")
    descs = [t["description"] for t in mock_gui.transactions]
    assert descs == ["Apple", "Banana", "Carrot"]
    
    mock_gui.sort_by_column("description")
    descs = [t["description"] for t in mock_gui.transactions]
    assert descs == ["Carrot", "Banana", "Apple"]

def test_sort_reset_on_new_column(mock_gui):
    """Test that switching columns resets sort to Ascending"""
    # 1. Sort Price Descending
    mock_gui.sort_by_column("price") # Asc
    mock_gui.sort_by_column("price") # Desc
    assert mock_gui.sort_descending is True
    assert mock_gui.last_sorted_col == "price"

    # 2. Switch to Quantity -> Should be Ascending
    mock_gui.sort_by_column("quantity")
    quantities = [t["quantity"] for t in mock_gui.transactions]
    assert quantities == [5, 10, 20] # Ascending (5, 10, 20)
    assert mock_gui.sort_descending is False
    assert mock_gui.last_sorted_col == "quantity"
