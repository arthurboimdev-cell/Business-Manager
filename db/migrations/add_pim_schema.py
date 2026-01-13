import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from db.db_connection import get_db_connection
from config.config import PRODUCTS_TABLE_NAME

def add_pim_schema():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Add JSON columns to products table
        new_cols = [
            ("amazon_data", "JSON"),
            ("etsy_data", "JSON")
        ]
        
        print(f"--- Updating {PRODUCTS_TABLE_NAME} ---")
        for col_name, col_def in new_cols:
            cursor.execute(f"SHOW COLUMNS FROM {PRODUCTS_TABLE_NAME} LIKE '{col_name}'")
            if not cursor.fetchone():
                print(f"Adding {col_name}...")
                cursor.execute(f"ALTER TABLE {PRODUCTS_TABLE_NAME} ADD COLUMN {col_name} {col_def}")
            else:
                print(f"{col_name} already exists.")

        # 2. Create product_images table
        print("--- Creating product_images table ---")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                image_data LONGBLOB,
                image_url TEXT,
                display_order INT DEFAULT 0,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        print("product_images table ready.")
        
        conn.commit()
        print("PIM Schema update complete.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_pim_schema()
