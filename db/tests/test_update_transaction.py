import pytest
from db.transactions import write_transaction, read_transactions, update_transaction
from db.db_connection import get_db_connection

TEST_TABLE = "transactions_test"

from db.init_db import init_db
from config.config import TRANSACTIONS_SCHEMA

@pytest.fixture(autouse=True)
def clean_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {TEST_TABLE}")
    conn.commit()
    cursor.close()
    conn.close()
    
    init_db(TEST_TABLE, TRANSACTIONS_SCHEMA)
    yield
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TEST_TABLE}")
    conn.commit()
    cursor.close()
    conn.close()

def test_update_transaction():
    # 1. Create a transaction
    t_id = write_transaction('2025-01-01', 'Original', 1, 10.0, 'expense', table=TEST_TABLE)
    
    # 2. Update it
    update_transaction(
        t_id, 
        '2025-01-02', 
        'Updated', 
        2, 
        20.0, 
        'income', 
        supplier='New Supplier', 
        table=TEST_TABLE
    )
    
    # 3. Read back and verify
    rows = read_transactions(table=TEST_TABLE)
    assert len(rows) == 1
    row = rows[0]
    
    assert str(row['transaction_date']) == '2025-01-02'
    assert row['description'] == 'Updated'
    assert row['quantity'] == 2
    assert float(row['price']) == 20.0
    assert row['transaction_type'] == 'income'
    assert row['supplier'] == 'New Supplier'
    assert float(row['total']) == 40.0 # 2 * 20.0
