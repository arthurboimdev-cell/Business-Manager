import pytest
from unittest.mock import MagicMock, patch, mock_open
from gui.controller import TransactionController

@pytest.fixture
def mock_controller():
    with patch('gui.controller.TransactionController.refresh_ui'): # Patch refresh_ui instead of load_data
        with patch('gui.controller.TransactionModel'):
            with patch('gui.controller.MainWindow', MagicMock()):
                with patch('gui.controller.InputFrame', MagicMock()):
                    with patch('gui.controller.TreeFrame', MagicMock()):
                         with patch('gui.controller.SummaryFrame', MagicMock()):
                            with patch('gui.controller.AnalyticsFrame', MagicMock()):
                                with patch('gui.controller.ProductsTab', MagicMock()):
                                    ctrl = TransactionController("test_table")
                                    ctrl.view = MagicMock()
                                    ctrl.model = MagicMock()
                                    return ctrl

def test_add_transaction_empty_fields(mock_controller):
    """Test that adding transaction with empty numeric fields shows error"""
    # Keys matching what controller expects: qty, price, desc
    mock_controller.view.input_frame.get_data.return_value = {
        'date': '', 'desc': '', 'qty': '', 'price': '', 'type': '', 'supplier': ''
    }
    
    with patch('tkinter.messagebox.showerror') as mock_error:
        data = mock_controller.view.input_frame.get_data.return_value
        mock_controller.add_transaction(data)
        
        mock_error.assert_called() # ValueError int('')
        mock_controller.model.add_transaction.assert_not_called()

def test_add_transaction_invalid_numbers(mock_controller):
    """Test that adding transaction with non-numeric qty/price shows error"""
    data = {
        'date': '2025-01-01', 'desc': 'Test', 'qty': 'abc', 'price': '10', 'type': 'income', 'supplier': ''
    }
    
    with patch('tkinter.messagebox.showerror') as mock_error:
        mock_controller.add_transaction(data)
        mock_error.assert_called()
        mock_controller.model.add_transaction.assert_not_called()

@pytest.mark.skip(reason="User disabled export tests")
def test_export_to_csv_cancel(mock_controller):
    """Test cancellation of export dialog"""
    with patch('tkinter.filedialog.asksaveasfilename', return_value=""): # User cancelled
        with patch('services.data_service.DataService.export_to_csv') as mock_export:
            mock_controller.export_csv() # Method name is export_csv
            mock_export.assert_not_called()

@pytest.mark.skip(reason="User disabled export tests")
def test_export_to_csv_success(mock_controller):
    """Test successful export"""
    # Mock data
    mock_controller.model.get_all_transactions.return_value = [
        {'id': 1, 'transaction_date': '2025-01-01', 'description': 'Test', 'quantity': 1, 'price': 10.0, 'total': 10.0, 'transaction_type': 'income', 'supplier': 'Sup'}
    ]
    
    with patch('tkinter.filedialog.asksaveasfilename', return_value="test.csv"):
        with patch('builtins.open', mock_open()) as mock_file:
             with patch('csv.writer') as mock_writer_cls:
                mock_writer = mock_writer_cls.return_value
                
                mock_controller.export_csv()
                
                # Verify header written
                mock_writer.writerow.assert_called()
