import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from db.db_connection import get_db_connection
from config.config import PRODUCTS_TABLE_NAME

def add_labor_columns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if columns exist
        cursor.execute(f"SHOW COLUMNS FROM {PRODUCTS_TABLE_NAME} LIKE 'labor_time'")
        if not cursor.fetchone():
            print("Adding labor_time column...")
            cursor.execute(f"ALTER TABLE {PRODUCTS_TABLE_NAME} ADD COLUMN labor_time INT DEFAULT 0")
        else:
            print("labor_time column already exists.")

        cursor.execute(f"SHOW COLUMNS FROM {PRODUCTS_TABLE_NAME} LIKE 'labor_rate'")
        if not cursor.fetchone():
            print("Adding labor_rate column...")
            cursor.execute(f"ALTER TABLE {PRODUCTS_TABLE_NAME} ADD COLUMN labor_rate FLOAT DEFAULT 0.0")
        else:
            print("labor_rate column already exists.")
            
        conn.commit()
        print("Schema update complete.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_labor_columns()
