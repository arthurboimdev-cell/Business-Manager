from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from server.main import app
from server.routes import router

client = TestClient(app)

def test_get_transactions_error():
    with patch('db.transactions.read_transactions') as mock_read:
        mock_read.side_effect = Exception("DB Error")
        
        response = client.get("/transactions")
        assert response.status_code == 500
        assert "DB Error" in response.json()['detail']

def test_add_transaction_error():
    with patch('db.transactions.write_transaction') as mock_write:
        mock_write.side_effect = Exception("DB Write Error")
        
        payload = {"date": "2025-01-01", "description": "T", "quantity": 1, "price": 1, "type": "income"}
        response = client.post("/transactions", json=payload)
        assert response.status_code == 500
        assert "DB Write Error" in response.json()['detail']

def test_add_transaction_validation_error():
    # Value Error handling (400)
    with patch('db.transactions.write_transaction') as mock_write:
        mock_write.side_effect = ValueError("Invalid data")
        
        payload = {"date": "2025-01-01", "description": "T", "quantity": 1, "price": 1, "type": "income"}
        response = client.post("/transactions", json=payload)
        assert response.status_code == 400
        assert "Invalid data" in response.json()['detail']

def test_update_transaction_error():
    with patch('db.transactions.update_transaction') as mock_update:
        mock_update.side_effect = Exception("Update Failed")
        
        payload = {"date": "2025-01-01", "description": "T", "quantity": 1, "price": 1, "type": "income"}
        response = client.put("/transactions/1", json=payload)
        assert response.status_code == 500

def test_delete_transaction_error():
    with patch('db.transactions.delete_transaction') as mock_delete:
        mock_delete.side_effect = Exception("Delete Failed")
        
        response = client.delete("/transactions/1")
        assert response.status_code == 500

def test_summary_error():
    with patch('db.transactions.read_transactions') as mock_read:
        mock_read.side_effect = Exception("Summary Error")
        
        response = client.get("/summary")
        assert response.status_code == 500
