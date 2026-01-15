import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.db_connection import get_db_connection

def add_fragrance_type_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ['products', 'products_test']
    
    try:
        for table in tables:
            print(f"--- Checking table: {table} ---")
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'fragrance_type'")
            if not cursor.fetchone():
                print(f"Adding fragrance_type to {table}...")
                try:
                    # Adding it after wax_rate for logical grouping, but order doesn't strictly matter
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN fragrance_type VARCHAR(100) AFTER wax_rate")
                    print("Success.")
                except Exception as e:
                    print(f"Failed to add column: {e}")
            else:
                print(f"Column fragrance_type already exists in {table}.")
                
        conn.commit()
        print("Migration complete.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_fragrance_type_column()
