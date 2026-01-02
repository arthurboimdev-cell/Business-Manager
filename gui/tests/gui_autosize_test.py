import pytest
import tkinter.font as tkfont
from unittest.mock import MagicMock, patch
from gui.GUI import TransactionGUI

def test_autosize_columns(tk_root):
    """Test that columns are resized based on content length"""
    
    # 1. Setup mock data
    mock_transactions = [
        {"transaction_date": "2024-01-01", "description": "Short", "price": 10.0, "quantity": 1, "total": 10.0, "transaction_type": "expense", "supplier": "A"},
        {"transaction_date": "2024-01-02", "description": "A Very Long Description Indeed", "price": 100000.0, "quantity": 100, "total": 100000.0, "transaction_type": "income", "supplier": "B"},
    ]

    # 2. Patch font measurement to return length of string
    # This simulates a font where 1 char = 10 pixels for simplicity
    def mock_measure(text):
        return len(text) * 10

    with patch("tkinter.font.nametofont") as mock_font_cls:
        mock_font = MagicMock()
        mock_font.measure.side_effect = mock_measure
        mock_font_cls.return_value = mock_font
        
        # 3. Initialize GUI with mocked reading
        with patch("gui.GUI.read_transactions", return_value=mock_transactions):
            gui = TransactionGUI(tk_root) # calling init triggers refresh -> autosize
            
            # 4. Check width of 'description' column
            # Header "Description" len=11 -> 110px + 20pad = 130
            # Row 1 "Short" len=5 -> 50px + 20pad = 70
            # Row 2 "A Very Long Description Indeed" len=30 -> 300px + 20pad = 320
            # Expected width = 320
            
            # We need to spy on tree.column calls or inspect the tree
            # Tkinter tree.column returns a dict of options if no option specified, 
            # but we can just check the last call to column('description') if we mock the tree or just inspect it.
            
            # Since we are using a real treeview (via tk_root), we can actually query it!
            # However, in a unit test with mocked font, checking the *call* to width is safer.
            
            # Let's verify expectations based on our mock_measure:
            # "Description" header: 11 chars * 10 = 110 + 20 = 130
            # Longest value: 30 chars * 10 = 300 + 20 = 320
            # So width should be 320.
            
            col_opts = gui.tree.column("description")
            # In unit tests with real Tk, the width might be constrained or default, 
            # but let's check if our logic ran.
            
            # Ideally we check the width. 
            # Note: tree.column('col')['width'] returns the current width.
            
            assert gui.tree.column("description", "width") == 320
            
            # Check 'transaction_type'
            # Header "Transaction_type" -> 160 + 20 = 180
            # Value "expense" -> 70+20=90
            # Value "income" -> 60+20=80
            # Expected: 180 (Header is wider)
            assert gui.tree.column("transaction_type", "width") == 180
