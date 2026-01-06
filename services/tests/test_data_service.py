import pytest
import os
import csv
from services.data_service import DataService

def test_export_to_csv(tmp_path):
    # 1. Setup Data
    transactions = [
        {"id": 1, "transaction_date": "2025-01-01", "description": "Test Item", "quantity": 10, "price": 5.0, "total": 50.0, "transaction_type": "income", "supplier": "Sup A"},
        {"id": 2, "transaction_date": "2025-01-02", "description": "Expense Item", "quantity": 1, "price": 10.0, "total": 10.0, "transaction_type": "expense", "supplier": "Sup B"}
    ]
    
    # 2. Define output file
    output_file = tmp_path / "test_export.csv"
    
    # 3. Call Export
    DataService.export_to_csv(str(output_file), transactions)
    
    # 4. Verify File Creation
    assert os.path.exists(output_file)
    
    # 5. Verify Content
    with open(output_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        
        # Header + 2 data rows = 3 rows
        assert len(rows) == 3
        
        # Check Header
        assert rows[0] == ["id", "transaction_date", "description", "quantity", "price", "total", "transaction_type", "supplier"]
        
        # Check Data Row 1
        # CSV reader reads all as strings
        assert rows[1][2] == "Test Item"
        assert rows[1][5] == "50.0"
        
        # Check Data Row 2
        assert rows[2][2] == "Expense Item"

def test_export_empty_list(tmp_path):
    output_file = tmp_path / "empty.csv"
    DataService.export_to_csv(str(output_file), [])
    # Should not create file or just do nothing? 
    # Current implementation returns if not transactions
    assert not os.path.exists(output_file)
