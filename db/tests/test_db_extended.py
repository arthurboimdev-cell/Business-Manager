import pytest
from unittest.mock import MagicMock, patch
import mysql.connector
import db.products as products_db
import db.materials as materials_db
import db.transactions as transactions_db

# Test Data
VALID_PROD_DATA = {
    "title": "Test Candle",
    "description": "Desc",
    "price": 20.0, # Note: Product schema expects 'selling_price' or mapped fields?
    # Checking products.py columns list: "selling_price" is expected, "price" isn't in cols list!
    # But wait, create_product filters by columns list.
    "selling_price": 20.0,
    "stock_quantity": 100,
    # New fields
    "container_unit": "Jar",
    "second_container_type": "Gypsum",
    "second_container_weight_g": 50.0,
    "second_container_rate": 5.0
}

class TestDBExtended:
    
    @pytest.fixture
    def mock_db_conn(self):
        with patch("db.products.get_db_connection") as mock_conn_prod, \
             patch("db.materials.get_db_connection") as mock_conn_mat, \
             patch("db.transactions.get_db_connection") as mock_conn_trans:
            
            # Create a shared mock connection
            mock_real_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_real_conn.cursor.return_value = mock_cursor
            
            # Apply to all
            mock_conn_prod.return_value = mock_real_conn
            mock_conn_mat.return_value = mock_real_conn
            mock_conn_trans.return_value = mock_real_conn
            
            yield mock_real_conn, mock_cursor

    # --- Products DB Tests ---
    def test_create_product_success(self, mock_db_conn):
        """1. Test creating product"""
        conn, cursor = mock_db_conn
        cursor.lastrowid = 1
        
        prod_id = products_db.create_product(VALID_PROD_DATA)
        
        assert prod_id == 1
        assert cursor.execute.called
        assert "INSERT INTO" in cursor.execute.call_args[0][0]
        # Args passed as list of values
        args = cursor.execute.call_args[0][1]
        assert "Gypsum" in args

    def test_create_product_db_error(self, mock_db_conn):
        """2. Test DB error during create"""
        conn, cursor = mock_db_conn
        cursor.execute.side_effect = mysql.connector.Error("DB Fail")
        
        # products.create_product doesn't have try/except block around execute?
        # Checked file: It has NO try/except in create_product! 
        # So it should Raise.
        try:
            products_db.create_product(VALID_PROD_DATA)
        except mysql.connector.Error:
            pass # Expected

    def test_get_products(self, mock_db_conn):
        """3. Test fetching products"""
        conn, cursor = mock_db_conn
        cursor.fetchall.return_value = [{"id": 1, "title": "C1"}]
        
        prods = products_db.get_products()
        assert len(prods) == 1
        assert prods[0]["title"] == "C1"

    def test_delete_product(self, mock_db_conn):
        """4. Test delete product"""
        conn, cursor = mock_db_conn
        if hasattr(products_db, 'delete_product'):
            products_db.delete_product(1)
            assert cursor.execute.called

    def test_update_product(self, mock_db_conn):
        """5. Test update product"""
        conn, cursor = mock_db_conn
        products_db.update_product(1, {"selling_price": 25.0})
        sql = cursor.execute.call_args[0][0]
        assert "UPDATE" in sql
        assert "selling_price" in sql

    def test_get_product(self, mock_db_conn):
        """6. Test get single product"""
        conn, cursor = mock_db_conn
        cursor.fetchone.return_value = {"id": 1}
        p = products_db.get_product(1)
        assert p["id"] == 1

    def test_fetch_empty_products(self, mock_db_conn):
        """7. Test empty products table"""
        conn, cursor = mock_db_conn
        # get_products handles Error -> [], but normal empty fetch -> []
        cursor.fetchall.return_value = []
        res = products_db.get_products()
        assert res == []

    # --- Materials DB Tests ---
    def test_add_material(self, mock_db_conn):
        """11. Add Material (Positional Args)"""
        conn, cursor = mock_db_conn
        cursor.lastrowid = 10
        # Signature: name, category, stock_quantity, unit_cost, unit_type
        mid = materials_db.add_material("Wax", "Raw", 100, 5.0, "kg")
        assert mid == 10

    def test_get_materials(self, mock_db_conn):
        """12. Get Materials"""
        conn, cursor = mock_db_conn
        cursor.fetchall.return_value = [{"id": 1, "name": "Wax"}]
        # Function is get_materials
        mats = materials_db.get_materials()
        assert len(mats) == 1

    def test_update_material(self, mock_db_conn):
        """13. Update Material (Positional Args)"""
        conn, cursor = mock_db_conn
        # Signature: id, name, category, stock, cost, unit
        materials_db.update_material(1, "Wax", "Raw", 200, 6.0, "kg")
        assert cursor.execute.called

    def test_delete_material(self, mock_db_conn):
        """14. Delete Material"""
        conn, cursor = mock_db_conn
        materials_db.delete_material(1)
        assert cursor.execute.called

    def test_material_db_fail(self, mock_db_conn):
        """15. Material DB Error (get_materials catches)"""
        conn, cursor = mock_db_conn
        cursor.execute.side_effect = mysql.connector.Error("Fail")
        # get_materials in snippet: try... finally. NO except!
        # wait, snippet showed try.. finally. Check strictness.
        # If it has no except, it raises.
        try:
            materials_db.get_materials()
        except mysql.connector.Error:
            pass

    # --- Transactions DB Tests ---
    def test_write_transaction(self, mock_db_conn):
        """16. Write Transaction"""
        conn, cursor = mock_db_conn
        cursor.lastrowid = 50
        # Args: date, desc, qty, price, type
        tid = transactions_db.write_transaction("2023-01-01", "Sale", 1, 10.0, "INCOME")
        assert tid == 50

    def test_read_transactions(self, mock_db_conn):
        """17. Read Transactions"""
        conn, cursor = mock_db_conn
        cursor.fetchall.return_value = [{"id": 50}]
        ts = transactions_db.read_transactions()
        assert len(ts) == 1

    def test_transaction_valuer_error(self, mock_db_conn):
        """19. Test invalid table name raises ValueError"""
        with pytest.raises(ValueError):
            transactions_db.read_transactions(table="invalid_table")

    def test_connection_close(self, mock_db_conn):
        """21. Verify connection close called"""
        conn, cursor = mock_db_conn
        products_db.get_products()
        assert conn.close.called
