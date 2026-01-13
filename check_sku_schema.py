
import mysql.connector
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import mysql_config, TABLE_NAME, PRODUCTS_TABLE_NAME

def check_schema():
    try:
        conn = mysql.connector.connect(**mysql_config)
        cursor = conn.cursor(dictionary=True)
        
        print(f"Checking schema for table: products")
        cursor.execute(f"DESCRIBE products")
        columns = cursor.fetchall()
        
        for col in columns:
            if col['Field'] == 'sku':
                print(f"Found SKU column: {col}")
                
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
