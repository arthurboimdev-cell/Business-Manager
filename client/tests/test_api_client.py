import pytest
import requests
from unittest.mock import patch, MagicMock
from client.api_client import APIClient

def test_get_all_transactions_error():
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("Connection refused")
        
        # Should return empty list and print error (not crash)
        result = APIClient.get_all_transactions()
        assert result == []

def test_add_transaction_error():
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.RequestException("Server error")
        
        with pytest.raises(requests.exceptions.RequestException):
            APIClient.add_transaction("2025-01-01", "Test", 1, 10.0, "income")

def test_update_transaction_error():
    with patch('requests.put') as mock_put:
        mock_put.side_effect = requests.exceptions.RequestException("Server error")
        
        with pytest.raises(requests.exceptions.RequestException):
            APIClient.update_transaction(1, "2025-01-01", "Test", 1, 10.0, "income")

def test_delete_transaction_error():
    with patch('requests.delete') as mock_delete:
        mock_delete.side_effect = requests.exceptions.RequestException("Server error")
        
        with pytest.raises(requests.exceptions.RequestException):
            APIClient.delete_transaction(1)
