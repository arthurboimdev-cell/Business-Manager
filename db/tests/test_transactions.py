import pytest
from db.transactions import write_transaction, read_transactions
from db.db_connection import get_db_connection

TEST_TABLE = "transactions_test"

# ---------------- FIXTURE: clean table before each test ----------------
@pytest.fixture(autouse=True)
def clean_table():
    """Delete all rows from the test table before each test"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TEST_TABLE}")
    conn.commit()
    cursor.close()
    conn.close()
    yield
    # Optional cleanup after test
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {TEST_TABLE}")
    conn.commit()
    cursor.close()
    conn.close()

# ---------------- TESTS ----------------

def test_write_and_read_transactions():
    """Test basic write and read with supplier"""
    write_transaction('2025-01-05', 'Wax 464-45', 17, 12.50, 'expense', supplier="Supplier A", table=TEST_TABLE)
    write_transaction('2025-01-10', 'Candle Sale - Vanilla', 10, 25.00, 'income', supplier="Supplier B", table=TEST_TABLE)

    rows = read_transactions(table=TEST_TABLE)
    assert len(rows) == 2
    assert rows[0]['description'] == 'Candle Sale - Vanilla'
    assert rows[0]['supplier'] == 'Supplier B'
    assert rows[1]['description'] == 'Wax 464-45'
    assert rows[1]['supplier'] == 'Supplier A'


def test_total_income_and_expense():
    """Check total income and expense calculations"""
    write_transaction('2025-01-05', 'Wax 464-45', 17, 12.50, 'expense', supplier="Supplier A", table=TEST_TABLE)
    write_transaction('2025-01-10', 'Candle Sale - Vanilla', 10, 25.00, 'income', supplier="Supplier B", table=TEST_TABLE)

    rows = read_transactions(table=TEST_TABLE)
    total_income = float(sum(r['total'] for r in rows if r['transaction_type'] == 'income'))
    total_expense = float(sum(r['total'] for r in rows if r['transaction_type'] == 'expense'))

    assert total_income == pytest.approx(250.00)
    assert total_expense == pytest.approx(212.50)


def test_balance_calculation():
    """Test balance = income - expenses"""
    write_transaction('2025-01-05', 'Wax 464-45', 17, 12.50, 'expense', supplier="Supplier A", table=TEST_TABLE)
    write_transaction('2025-01-10', 'Candle Sale - Vanilla', 10, 25.00, 'income', supplier="Supplier B", table=TEST_TABLE)

    rows = read_transactions(table=TEST_TABLE)
    total_income = float(sum(r['total'] for r in rows if r['transaction_type'] == 'income'))
    total_expense = float(sum(r['total'] for r in rows if r['transaction_type'] == 'expense'))
    balance = total_income - total_expense

    assert balance == pytest.approx(37.50)


def test_total_sold_units_and_avg_price():
    """Test total units sold and average price per unit"""
    write_transaction('2025-01-10', 'Candle Sale - Vanilla', 10, 25.00, 'income', supplier="Supplier B", table=TEST_TABLE)
    write_transaction('2025-01-12', 'Candle Sale - Chocolate', 5, 30.00, 'income', supplier="Supplier C", table=TEST_TABLE)

    rows = read_transactions(table=TEST_TABLE)
    sold_units = sum(r['quantity'] for r in rows if r['transaction_type'] == 'income')
    total_income = float(sum(r['total'] for r in rows if r['transaction_type'] == 'income'))
    avg_price = total_income / sold_units if sold_units > 0 else 0

    assert sold_units == 15
    assert avg_price == pytest.approx(26.6667, 0.0001)


def test_only_expenses():
    """Test table with only expenses"""
    write_transaction('2025-01-15', 'Wax Refill', 5, 20.00, 'expense', supplier="Supplier A", table=TEST_TABLE)

    rows = read_transactions(table=TEST_TABLE)
    total_income = float(sum(r['total'] for r in rows if r['transaction_type'] == 'income'))
    total_expense = float(sum(r['total'] for r in rows if r['transaction_type'] == 'expense'))

    assert total_income == 0
    assert total_expense == pytest.approx(100.00)


def test_only_income():
    """Test table with only income"""
    write_transaction('2025-01-20', 'Candle Sale - Lemon', 8, 15.00, 'income', supplier="Supplier B", table=TEST_TABLE)

    rows = read_transactions(table=TEST_TABLE)
    total_income = float(sum(r['total'] for r in rows if r['transaction_type'] == 'income'))
    total_expense = float(sum(r['total'] for r in rows if r['transaction_type'] == 'expense'))

    assert total_income == pytest.approx(120.00)
    assert total_expense == 0


def test_delete_transaction():
    """Test deleting a transaction"""
    # Create a transaction
    t_id = write_transaction('2025-01-25', 'To Delete', 1, 10.00, 'expense', table=TEST_TABLE)
    
    # Verify it exists
    rows = read_transactions(table=TEST_TABLE)
    assert len(rows) == 1
    assert rows[0]['id'] == t_id
    
    # Delete it
    from db.transactions import delete_transaction
    delete_transaction(t_id, table=TEST_TABLE)
    
    # Verify it's gone
    rows = read_transactions(table=TEST_TABLE)
    assert len(rows) == 0


def test_read_empty_table():
    """Test reading from an empty table"""
    rows = read_transactions(table=TEST_TABLE)
    assert rows == []


def test_invalid_table_name():
    """Test that using an invalid table name raises ValueError"""
    with pytest.raises(ValueError, match="Invalid table name"):
        write_transaction('2025-01-01', 'Fail', 1, 1, 'expense', table="invalid_table")
        
    with pytest.raises(ValueError, match="Invalid table name"):
        read_transactions(table="invalid_table")
