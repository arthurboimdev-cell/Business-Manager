import pytest
from unittest.mock import patch, MagicMock
from gui.models import TransactionModel

TEST_TABLE = "transactions_test"

@pytest.fixture
def mock_api():
    with patch("gui.models.APIClient") as mock:
        yield mock

def test_model_add_and_get(mock_api):
    model = TransactionModel(TEST_TABLE)
    
    # Setup mock return values
    mock_api.get_all_transactions.return_value = [
        {'id': 1, 'description': 'Model Test', 'quantity': 5, 'price': 10.0, 'transaction_type': 'income'}
    ]
    
    model.add_transaction('2025-01-01', 'Model Test', 5, 10.0, 'income')
    rows = model.get_all_transactions()
    
    # Verify API called
    mock_api.add_transaction.assert_called_with('2025-01-01', 'Model Test', 5, 10.0, 'income', None)
    mock_api.get_all_transactions.assert_called_once()
    
    assert len(rows) == 1
    assert rows[0]['description'] == 'Model Test'

def test_model_update(mock_api):
    model = TransactionModel(TEST_TABLE)
    
    # Mock add return
    mock_api.add_transaction.return_value = 123
    t_id = model.add_transaction('2025-01-01', 'To Update', 1, 1.0, 'expense')
    
    model.update_transaction(t_id, '2025-01-01', 'Updated', 2, 2.0, 'expense')
    
    mock_api.update_transaction.assert_called_with(123, '2025-01-01', 'Updated', 2, 2.0, 'expense', None)

def test_model_delete(mock_api):
    model = TransactionModel(TEST_TABLE)
    t_id = 99
    
    model.delete_transaction(t_id)
    
    mock_api.delete_transaction.assert_called_with(t_id)
