import pytest
from unittest.mock import MagicMock, patch
from gui.controller import TransactionController

@pytest.fixture
def mock_view():
    with patch('gui.controller.MainWindow') as mock_window:
        with patch('gui.controller.InputFrame') as mock_input:
            with patch('gui.controller.TreeFrame') as mock_tree:
                with patch('gui.controller.SummaryFrame') as mock_summary:
                    with patch('gui.controller.messagebox') as mock_mb:
                        yield {
                            'window': mock_window,
                            'input': mock_input,
                            'tree': mock_tree,
                            'summary': mock_summary,
                            'mb': mock_mb
                        }

@pytest.fixture
def mock_model():
    with patch('gui.controller.TransactionModel') as mock_class:
        mock_instance = mock_class.return_value
        yield mock_instance

def test_controller_initialization(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    mock_model.get_all_transactions.assert_called_once()
    # Check that frames are created
    mock_view['input'].assert_called()
    mock_view['tree'].assert_called()
    mock_view['summary'].assert_called()

def test_add_transaction_success(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    data = {
        "date": "2025-01-01",
        "desc": "Test Item",
        "qty": "5",
        "price": "10.0",
        "type": "income",
        "supplier": "Test Supplier"
    }
    
    controller.add_transaction(data)
    
    # Check model called
    mock_model.add_transaction.assert_called_with(
        "2025-01-01", "Test Item", 5, 10.0, "income", "Test Supplier"
    )
    # Check UI refresh
    controller.input_frame.clear_fields.assert_called()
    assert mock_model.get_all_transactions.call_count == 2 # Init + Refresh

def test_add_transaction_invalid_input(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    data = {"qty": "invalid", "price": "10"} # Invalid qty
    
    controller.add_transaction(data)
    
    mock_model.add_transaction.assert_not_called()
    mock_view['mb'].showerror.assert_called()

def test_update_transaction(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    data = {
        "date": "2025-01-01",
        "desc": "Updated",
        "qty": "3",
        "price": "50.0",
        "type": "expense",
        "supplier": "New Supp"
    }
    
    controller.update_transaction(123, data)
    
    mock_model.update_transaction.assert_called_with(
        123, "2025-01-01", "Updated", 3, 50.0, "expense", "New Supp"
    )
    mock_view['mb'].showinfo.assert_called_with("Success", "Transaction Updated")

def test_prep_edit_transaction_found(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    # Mock data in model
    mock_t = {
        'id': 99,
        'transaction_date': '2025-01-01',
        'description': 'Target',
        'quantity': 1,
        'price': 100.0,
        'transaction_type': 'income',
        'total': 100.0,
        'supplier': 'S'
    }
    mock_model.get_all_transactions.return_value = [mock_t]
    
    # Tree item values (strings mostly)
    tree_item = {
        'values': ['2025-01-01', 'Target', '1', '100.0', 'income', '100.0', 'S']
    }
    
    controller.prep_edit_transaction(tree_item)
    
    controller.input_frame.load_for_editing.assert_called_with(99, mock_t)

def test_prep_edit_transaction_not_found(mock_view, mock_model):
    controller = TransactionController("test_table")
    mock_model.get_all_transactions.return_value = [] # Empty DB
    
    tree_item = {'values': ['2025-01-01', 'Target', '1', '100.0', 'income', '100.0', 'S']}
    
    controller.prep_edit_transaction(tree_item)
    
    controller.input_frame.load_for_editing.assert_not_called()
    mock_view['mb'].showerror.assert_called()
