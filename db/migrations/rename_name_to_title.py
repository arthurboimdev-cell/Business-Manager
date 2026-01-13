
import mysql.connector
from config.config import DB_CONFIG, DB_NAME, TEST_DB_NAME

def rename_column():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    try:
        # 1. Update Main DB
        print(f"Renaming column in {DB_NAME}...")
        cursor.execute(f"USE {DB_NAME}")
        
        # Checking if column exists before renaming to avoid errors if run multiple times
        cursor.execute("SHOW COLUMNS FROM products LIKE 'title'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE products CHANGE COLUMN name title VARCHAR(255) NOT NULL")
            print("Renamed 'name' to 'title' in products table.")
        else:
            print("Column 'title' already exists.")

        # 2. Update Test DB
        print(f"Renaming column in {TEST_DB_NAME}...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME}")
        cursor.execute(f"USE {TEST_DB_NAME}")
        
        # Check table existence first
        cursor.execute("SHOW TABLES LIKE 'products_test'")
        if cursor.fetchone():
             cursor.execute("SHOW COLUMNS FROM products_test LIKE 'title'")
             if not cursor.fetchone():
                cursor.execute("ALTER TABLE products_test CHANGE COLUMN name title VARCHAR(255) NOT NULL")
                print("Renamed 'name' to 'title' in products_test table.")
             else:
                print("Column 'title' already exists in test db.")
        
        conn.commit()
        print("Migration successful.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    rename_column()
