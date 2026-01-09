import pytest
from unittest.mock import MagicMock, patch
from gui.controller import TransactionController

@pytest.fixture
def mock_view():
    with patch('gui.controller.MainWindow') as mock_window_cls:
        with patch('gui.controller.InputFrame') as mock_input_cls:
            with patch('gui.controller.TreeFrame') as mock_tree_cls:
                with patch('gui.controller.SummaryFrame') as mock_summary_cls:
                    with patch('gui.controller.AnalyticsFrame') as mock_analytics_cls:
                        with patch('gui.controller.messagebox') as mock_mb:
                            with patch('gui.controller.filedialog') as mock_fd:
                                # Setup mock instance
                                mock_window = mock_window_cls.return_value
                                
                                # Mock the tabs (Frames)
                                mock_window.tab_transactions = MagicMock()
                                mock_window.tab_analytics = MagicMock()
                                
                                yield {
                                    'window': mock_window,
                                    'input': mock_input_cls,
                                    'tree': mock_tree_cls,
                                    'summary': mock_summary_cls,
                                    'analytics': mock_analytics_cls,
                                    'mb': mock_mb,
                                    'mb': mock_mb,
                                    'fd': mock_fd
                                        }

@pytest.fixture(autouse=True)
def mock_products_tab():
    with patch('gui.controller.ProductsTab') as mock:
        yield mock

@pytest.fixture(autouse=True)
def mock_materials_tab():
    with patch('gui.controller.MaterialsTab') as mock:
        yield mock

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
    mock_view['analytics'].assert_called()

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

def test_filter_transactions(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    # Mock data
    t1 = {'id': 1, 'description': 'Apple', 'supplier': 'Farm A', 'transaction_date': '2025', 'quantity': 1, 'price': 1, 'transaction_type': 'income', 'total': 1}
    t2 = {'id': 2, 'description': 'Banana', 'supplier': 'Farm B', 'transaction_date': '2025', 'quantity': 1, 'price': 1, 'transaction_type': 'income', 'total': 1}
    mock_model.get_all_transactions.return_value = [t1, t2]
    
    # 1. Filter "Apple"
    controller.filter_transactions("Apple")
    # Should insert 1 item
    assert controller.tree_frame.insert.call_count == 1
    
    # 2. Filter "Farm" (matches both)
    controller.tree_frame.insert.reset_mock()
    controller.filter_transactions("Farm")
    assert controller.tree_frame.insert.call_count == 2
    
    # 3. Filter "Zucchini" (matches none)
    controller.tree_frame.insert.reset_mock()
    controller.filter_transactions("Zucchini")
    assert controller.tree_frame.insert.call_count == 0

def test_export_csv_cancel(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    # Mock file dialog returning None/Empty
    mock_view['fd'].asksaveasfilename.return_value = ""
    
    with patch('services.data_service.DataService.export_to_csv') as mock_export:
        controller.export_csv()
        mock_export.assert_not_called()

def test_export_csv_success(mock_view, mock_model):
    controller = TransactionController("test_table")
    
    # Mock file dialog returning path
    mock_view['fd'].asksaveasfilename.return_value = "C:/test.csv"
    mock_model.get_all_transactions.return_value = [{'id':1}]
    
    with patch('services.data_service.DataService.export_to_csv') as mock_export:
        controller.export_csv()
        mock_export.assert_called_with("C:/test.csv", [{'id':1}])
        mock_view['mb'].showinfo.assert_called()
