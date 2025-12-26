import mysql.connector
from config.config import mysql_config


def get_db_connection():
    """
    Returns a MySQL connection.

    Args:
        test (bool): If True, connect to the test database.

    Returns:
        mysql.connector.connection.MySQLConnection
    """
    return mysql.connector.connect(**mysql_config)
