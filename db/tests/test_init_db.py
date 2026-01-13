import pytest
from unittest.mock import MagicMock, patch
from db.init_db import init_db, generate_create_table_sql, create_table

def test_generate_create_table_sql_empty():
    """Test using empty schema"""
    assert generate_create_table_sql("tbl", {}) is None

def test_generate_create_table_sql_valid():
    """Test generating SQL from schema dict"""
    schema = {
        "id": "INT PRIMARY KEY",
        "name": "VARCHAR(255)"
    }
    sql = generate_create_table_sql("users", schema)
    
    expected_start = "CREATE TABLE IF NOT EXISTS users ("
    assert sql.startswith(expected_start)
    assert "id INT PRIMARY KEY" in sql
    assert "name VARCHAR(255)" in sql

def test_init_db_table_missing():
    """Test that creation SQL is executed if table missing"""
    with patch("db.init_db.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        # SHOW TABLES returns None (false)
        mock_cursor.fetchone.return_value = None
        
        # Patch DB_SCHEMA to ensure it's not empty
        test_schema = {"col1": "INT"}
        
        # Call create_table directly to test single table logic
        create_table("missing_table", test_schema)
        
        # verify execute called with valid SQL
        call_args = mock_cursor.execute.call_args_list
        # First call is SHOW TABLES
        assert "SHOW TABLES" in call_args[0][0][0]
        # Second call should be CREATE TABLE
        create_query = call_args[1][0][0]
        assert "CREATE TABLE" in create_query
        assert "col1 INT" in create_query
        
        mock_conn.return_value.commit.assert_called_once()
