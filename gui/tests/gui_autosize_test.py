import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from gui.views import TreeFrame

@pytest.fixture
def mock_callbacks():
    return {
        'on_delete': MagicMock(),
        'on_edit': MagicMock(),
        'on_search': MagicMock(),
        'on_export': MagicMock()
    }

def test_autosize_columns(tk_root, mock_callbacks):
    """Test that columns are resized based on content length using TreeFrame"""
    
    # 1. Setup Data
    columns = ["date", "description", "price"]
    
    # 2. Initialize TreeFrame
    # We need a parent. tk_root works.
    frame = TreeFrame(
        tk_root, 
        columns, 
        mock_callbacks['on_delete'], 
        mock_callbacks['on_edit'], 
        mock_callbacks['on_search'], 
        mock_callbacks['on_export'],
        lambda x: None,
        features={}
    )
    
    # 3. Insert Data
    # Row 1: Short description
    frame.insert(("2024-01-01", "Short", "10.0"))
    # Row 2: Long description
    frame.insert(("2024-01-02", "A Very Long Description Indeed", "100.0"))
    
    # 4. Patch Font measurement
    # Logic: string length * 10 pixels
    def mock_measure(text):
        if text is None: return 0
        return len(str(text)) * 10

    # We patch tk.font.Font so that Font().measure calls our mock
    with patch("tkinter.font.Font") as mock_font_cls:
        mock_font_instance = MagicMock()
        mock_font_instance.measure.side_effect = mock_measure
        mock_font_cls.return_value = mock_font_instance
        
        # 5. Call Autosize
        frame.autosize_columns()
        
        # 6. Verify Column Widths
        # Formula in code: measure(text) + 20
        
        # Column "description"
        # Header "Description" (11 chars) -> 110 + 20 = 130
        # Row 2 value (30 chars) -> 300 + 20 = 320
        # Expected max: 320
        assert frame.tree.column("description", "width") == 320
        
        # Column "date"
        # Header "Date" (4 chars) -> 40 + 20 = 60
        # Value "2024-01-01" (10 chars) -> 100 + 20 = 120
        # Expected max: 120
        assert frame.tree.column("date", "width") == 120
