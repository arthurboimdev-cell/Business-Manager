from db.db_connection import get_db_connection
import mysql.connector

def run_migration():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ["products", "products_test"]
    columns_to_add = [
        ("second_container_type", "VARCHAR(100)"),
        ("second_container_weight_g", "DECIMAL(10, 2) DEFAULT 0.00"),
        ("second_container_rate", "DECIMAL(10, 2) DEFAULT 0.00")
    ]
    
    for table in tables:
        print(f"Checking table '{table}'...")
        for col_name, col_def in columns_to_add:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table} LIKE '{col_name}'")
                result = cursor.fetchone()
                
                if not result:
                    print(f"  Adding '{col_name}'...")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
                    conn.commit()
                else:
                    print(f"  Skipping '{col_name}': already exists.")
                    
            except mysql.connector.Error as err:
                print(f"Error checking/adding '{col_name}' in '{table}': {err}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migration()
