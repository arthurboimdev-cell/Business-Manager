from db.db_connection import get_db_connection
import mysql.connector

def run_migration():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tables = ["products", "products_test"]
    
    for table in tables:
        try:
            # Check if column exists
            cursor.execute(f"SHOW COLUMNS FROM {table} LIKE 'container_unit'")
            result = cursor.fetchone()
            
            if not result:
                print(f"Adding 'container_unit' to '{table}'...")
                # Default to 'pcs' to maintain backward compatibility
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN container_unit VARCHAR(10) DEFAULT 'pcs' AFTER container_quantity")
                conn.commit()
                print(f"Success: Added 'container_unit' to '{table}'")
            else:
                print(f"Skipping '{table}': 'container_unit' already exists.")
                
        except mysql.connector.Error as err:
            print(f"Error migrating '{table}': {err}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migration()
