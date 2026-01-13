import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from db.db_connection import get_db_connection

def check_columns():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ['products', 'products_test']
    
    for table in tables:
        print(f"--- Checking table: {table} ---")
        try:
            cursor.execute(f"SHOW COLUMNS FROM {table}")
            columns = [row[0] for row in cursor.fetchall()]
            print(f"Columns: {columns}")
            
            missing = []
            for col in ['labor_time', 'labor_rate', 'wax_rate']:
                if col not in columns:
                    missing.append(col)
            
            if missing:
                print(f"MISSING columns in {table}: {missing}")
            else:
                print(f"All expected columns present in {table}.")
                
        except Exception as e:
            print(f"Error checking {table}: {e}")
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_columns()
