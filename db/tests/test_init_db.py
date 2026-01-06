import pytest
from unittest.mock import MagicMock, mock_open, patch
from db.init_db import init_db, load_creation_sql

def test_load_creation_sql_missing_file():
    """Test behavior when SQL file is missing"""
    with patch("db.init_db.CONFIG_PATH") as mock_path:
        mock_path.parent.__truediv__.return_value.exists.return_value = False
        assert load_creation_sql("any_table") is None

def test_load_creation_sql_success():
    """Test that SQL is loaded and placeholder replaced"""
    with patch("db.init_db.CONFIG_PATH") as mock_path:
        mock_file_path = MagicMock()
        mock_file_path.exists.return_value = True
        mock_path.parent.__truediv__.return_value = mock_file_path
        
        with patch("builtins.open", mock_open(read_data="CREATE TABLE {table_name} (id INT);")):
            sql = load_creation_sql("my_table")
            assert sql == "CREATE TABLE my_table (id INT);"

def test_init_db_table_exists():
    """Test that no SQL is executed if table exists"""
    with patch("db.init_db.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        # SHOW TABLES returns a row (True)
        mock_cursor.fetchone.return_value = (1,) 
        
        with patch("db.init_db.load_creation_sql") as mock_load:
            init_db("existing_table")
            
            # Should check table existence
            mock_cursor.execute.assert_called_with("SHOW TABLES LIKE %s", ("existing_table",))
            # Should NOT load SQL or execute creation
            mock_load.assert_not_called()

def test_init_db_table_missing():
    """Test that creation SQL is executed if table missing"""
    with patch("db.init_db.get_db_connection") as mock_conn:
        mock_cursor = mock_conn.return_value.cursor.return_value
        # SHOW TABLES returns None (False)
        mock_cursor.fetchone.return_value = None
        
        with patch("db.init_db.load_creation_sql", return_value="CREATE TABLE sql"):
            init_db("missing_table")
            
            # Should execute creation SQL
            mock_cursor.execute.assert_any_call("CREATE TABLE sql")
            mock_conn.return_value.commit.assert_called_once()
