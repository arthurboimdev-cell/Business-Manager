
from config.config import PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA
from db.db_connection import get_db_connection

def create_gallery_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"Creating table {PRODUCT_IMAGES_TABLE}...")
    schema_str = ", ".join([f"{col} {dtype}" for col, dtype in PRODUCT_IMAGES_SCHEMA.items()])
    sql = f"CREATE TABLE IF NOT EXISTS {PRODUCT_IMAGES_TABLE} ({schema_str})"
    
    try:
        cursor.execute(sql)
        conn.commit()
        print("Table created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_gallery_table()
