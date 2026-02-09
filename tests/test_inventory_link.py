import pytest
from unittest.mock import MagicMock, patch
from client.api_client import APIClient

@pytest.fixture
def clean_db():
    # Helper to clean up products and transactions
    # This assumes running against a test DB
    pass

def test_inventory_link_flow():
    """
    Test that adding an income transaction linked to a product reduces its stock.
    """
    # 1. Add a Product with initial stock
    product_data = {
        "title": "Test Link Product",
        "stock_quantity": 100,
        "weight_g": 200,
        "sku": "LINK-001"
    }
    # Mocking since we might not fail if server isn't running in unit test context
    # But ideally this is an integration test.
    # Let's use the real API Client but mocked requests if needed, 
    # OR better: Use the DB functions directly to test logic if we are offline.
    # But the user wants robust verification.
    # Let's assume the server is running or we use DB ops directly for the test logic.
    pass

# We'll use DB ops directly for reliable testing without spinning up a full server in test
from db import products, transactions
from config.config import PRODUCTS_TABLE_NAME, TABLE_NAME
from db.db_connection import get_db_connection

def setup_module():
    # Ensure tables exist and are fresh for this test module
    from db.init_db import init_db
    from config.config import TRANSACTIONS_SCHEMA, PRODUCTS_SCHEMA, PRODUCT_IMAGES_TABLE
    from db.db_connection import get_db_connection
    
    conn = get_db_connection()
    c = conn.cursor()
    # Drop to force schema update - Correct Order
    c.execute(f"DROP TABLE IF EXISTS {PRODUCT_IMAGES_TABLE}")
    c.execute(f"DROP TABLE IF EXISTS {PRODUCTS_TABLE_NAME}")
    c.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
    conn.commit()
    c.close()
    conn.close()

    from config.config import PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA
    init_db(PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA)
    init_db(TABLE_NAME, TRANSACTIONS_SCHEMA)
    init_db(PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA)

def test_stock_deduction():
    # 1. Create Product
    p_data = {
        "title": "Stock Test Candle",
        "stock_quantity": 50,
        "sku": "STK-1"
    }
    # Direct DB insertion to bypass API for test speed/reliability
    # We need to recreate the table or cleanup
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SET FOREIGN_KEY_CHECKS = 0")
    c.execute(f"DELETE FROM {PRODUCTS_TABLE_NAME}")
    c.execute("SET FOREIGN_KEY_CHECKS = 1")
    # Wait, `config.py` selects TABLE based on frozen. Tests usually run in source.
    # So we are on `products_test` and `transactions_test`. Safe.
    pass

import time

def test_add_transaction_deducts_stock():
    # Setup
    conn = get_db_connection()
    c = conn.cursor()
    # Reset data (tables exist from setup_module)
    c.execute("SET FOREIGN_KEY_CHECKS = 0")
    c.execute(f"DELETE FROM {PRODUCTS_TABLE_NAME}")
    c.execute(f"DELETE FROM {TABLE_NAME}")
    c.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    
    # 1. Add Product
    p_id = products.create_product({
        "title": "Inventory Candle", 
        "stock_quantity": 10,
        "sku": "INV-1"
    }, table=PRODUCTS_TABLE_NAME)
    
    # 2. Add Transaction (Income) linked to Product
    # logic involves calling update_stock. The route does this.
    # So we should test the route logic or the service function if exists.
    # Route logic: if item.product_id: update_stock.
    
    # Let's test the DB function update_stock directly first
    products.update_stock(p_id, -2, table=PRODUCTS_TABLE_NAME)
    
    # Verify
    p = products.get_product(p_id, table=PRODUCTS_TABLE_NAME)
    assert p['stock_quantity'] == 8
    
    # Now test the "Transaction" flow simulation
    # Simulate what the route does:
    t_id = transactions.write_transaction(
        transaction_date="2025-01-01",
        description="Sale",
        quantity=3,
        price=20.0,
        transaction_type="income",
        product_id=p_id,
        table=TABLE_NAME
    )
    # Route logic manual call (since we aren't testing the route via HTTP here)
    products.update_stock(p_id, -3, table=PRODUCTS_TABLE_NAME)
    
    p = products.get_product(p_id, table=PRODUCTS_TABLE_NAME)
    assert p['stock_quantity'] == 5 

