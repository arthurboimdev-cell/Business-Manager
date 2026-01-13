import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from db.db_connection import get_db_connection

def fix_all_columns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ['products', 'products_test']
    
    # Columns to ensure exist
    columns_to_add = [
        ("labor_time", "INT DEFAULT 0"),
        ("labor_rate", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("wax_rate", "DECIMAL(10, 4) DEFAULT 0.0000"),
        ("fragrance_rate", "DECIMAL(10, 4) DEFAULT 0.0000"),
        ("wick_rate", "DECIMAL(10, 4) DEFAULT 0.0000"),
        ("container_rate", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("wick_quantity", "INT DEFAULT 1"),
        ("container_quantity", "INT DEFAULT 1"),
        ("box_quantity", "INT DEFAULT 1"),
        ("box_type", "VARCHAR(100)"),
        ("selling_price", "DECIMAL(10, 2) DEFAULT 0.00")
    ]
    
    try:
        for table in tables:
            print(f"--- Fixing table: {table} ---")
            for col_name, col_def in columns_to_add:
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{col_name}'")
                if not cursor.fetchone():
                    print(f"Adding {col_name} to {table}...")
                    try:
                        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                    except Exception as e:
                        print(f"Failed to add {col_name}: {e}")
                else:
                    print(f"{col_name} exists in {table}.")
            
        conn.commit()
        print("Schema sync complete.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_all_columns()
