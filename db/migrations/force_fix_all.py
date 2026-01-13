import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import mysql.connector
from config.config import mysql_config as DB_CONFIG

# Hardcode table names to ensure we hit them both
TABLES_TO_FIX = ["products", "products_test"]

def force_fix_columns():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    columns_to_add = [
        ("fragrance_type", "VARCHAR(255) AFTER wax_rate"),
        ("total_cost", "DECIMAL(10, 2) DEFAULT 0.00 AFTER labor_rate")
    ]
    
    for table in TABLES_TO_FIX:
        print(f"Checking table '{table}'...")
        # Check if table exists first
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        if not cursor.fetchone():
            print(f"  Table '{table}' does not exist. Skipping.")
            continue
            
        for col_name, col_def in columns_to_add:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{col_name}'")
                if not cursor.fetchone():
                    print(f"  Adding column '{col_name}' to '{table}'...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                    print("    Success.")
                else:
                    print(f"  Column '{col_name}' already exists in '{table}'.")
            except mysql.connector.Error as err:
                print(f"  Error processing '{col_name}' on '{table}': {err}")
                
    conn.close()

if __name__ == "__main__":
    force_fix_columns()
