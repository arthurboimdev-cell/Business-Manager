import pytest
from gui.models import TransactionModel
from db.db_connection import get_db_connection
from db.transactions import read_transactions

TEST_TABLE = "transactions_test"

@pytest.fixture(autouse=True)
def clean_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TEST_TABLE}")
    conn.commit()
    cursor.close()
    conn.close()
    yield
    # Cleanup
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TEST_TABLE}")
    conn.commit()
    cursor.close()
    conn.close()

def test_model_add_and_get():
    model = TransactionModel(TEST_TABLE)
    model.add_transaction('2025-01-01', 'Model Test', 5, 10.0, 'income')
    
    rows = model.get_all_transactions()
    assert len(rows) == 1
    assert rows[0]['description'] == 'Model Test'

def test_model_update():
    model = TransactionModel(TEST_TABLE)
    t_id = model.add_transaction('2025-01-01', 'To Update', 1, 1.0, 'expense')
    
    model.update_transaction(t_id, '2025-01-01', 'Updated', 2, 2.0, 'expense')
    
    rows = model.get_all_transactions()
    assert rows[0]['description'] == 'Updated'
    assert rows[0]['quantity'] == 2

def test_model_delete():
    model = TransactionModel(TEST_TABLE)
    t_id = model.add_transaction('2025-01-01', 'To Delete', 1, 1.0, 'expense')
    
    model.delete_transaction(t_id)
    
    rows = model.get_all_transactions()
    assert len(rows) == 0
