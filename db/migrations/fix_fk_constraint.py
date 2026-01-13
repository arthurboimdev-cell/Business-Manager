
from config.config import PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA
from db.db_connection import get_db_connection

def fix_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"Dropping table {PRODUCT_IMAGES_TABLE}...")
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {PRODUCT_IMAGES_TABLE}")
        conn.commit()
    except Exception as e:
        print(f"Error dropping table: {e}")

    print(f"Re-creating table {PRODUCT_IMAGES_TABLE}...")
    schema_str = ", ".join([f"{col} {dtype}" for col, dtype in PRODUCT_IMAGES_SCHEMA.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {PRODUCT_IMAGES_TABLE} ({schema_str})"
    print(f"SQL: {sql}")
    
    try:
        cursor.execute(sql)
        conn.commit()
        print("Table recreated successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    fix_table()
