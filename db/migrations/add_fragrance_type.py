import sys
import os

# Add parent directory to path to allow importing config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import mysql.connector
from config.config import mysql_config as DB_CONFIG, PRODUCTS_TABLE_NAME

def add_fragrance_type_column():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print(f"Checking {PRODUCTS_TABLE_NAME} for fragrance_type column...")
        cursor.execute(f"SHOW COLUMNS FROM {PRODUCTS_TABLE_NAME} LIKE 'fragrance_type'")
        result = cursor.fetchone()
        
        if not result:
            print("Adding fragrance_type column...")
            # Add it after wax_rate for logical grouping, but order doesn't strictly matter
            cursor.execute(f"ALTER TABLE {PRODUCTS_TABLE_NAME} ADD COLUMN fragrance_type VARCHAR(255) AFTER wax_rate")
            print("Column added successfully.")
        else:
            print("Column fragrance_type already exists.")
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_fragrance_type_column()
