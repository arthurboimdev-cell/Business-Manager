import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from db.db_connection import get_db_connection

def add_common_data_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ['products', 'products_test']
    
    col_name = "common_data"
    col_def = "JSON"
    
    try:
        for table in tables:
            print(f"--- Checking table: {table} ---")
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
        print("Migration complete.")
        
    except Exception as e:
        print(f"Error updating schema: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_common_data_column()
