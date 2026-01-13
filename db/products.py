from db.db_connection import get_db_connection
from config.config import PRODUCTS_TABLE_NAME
import mysql.connector

def create_product(product_data, table=PRODUCTS_TABLE_NAME):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # keys: name, description, weight_g, length_cm, width_cm, height_cm, 
    #       wax_type, wax_weight_g, wick_type, container_type, container_details, 
    #       box_price, wrap_price, image (BLOB)
    
    # We'll construct the query dynamically based on keys present, 
    # but strict adherence to schema is safer.
    
    columns = [
        "name", "sku", "upc", "description", "stock_quantity", "weight_g", "length_cm", "width_cm", "height_cm",
        "wax_type", "wax_weight_g", "wick_type", "container_type", "container_details",
        "box_price", "wrap_price", "business_card_cost", "labor_time", "labor_rate", 'image'
    ]
    
    # Filter data to only valid columns
    data = {k: v for k, v in product_data.items() if k in columns}
    
    cols_str = ", ".join(data.keys())
    # placeholders: %s
    placeholders = ", ".join(["%s"] * len(data))
    
    sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
    
    try:
        cursor.execute(sql, list(data.values()))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def get_products(table=PRODUCTS_TABLE_NAME):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(f"SELECT * FROM {table}")
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_product(product_id, table=PRODUCTS_TABLE_NAME):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (product_id,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def update_product(product_id, product_data, table=PRODUCTS_TABLE_NAME):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = [
        "name", "sku", "upc", "description", "stock_quantity", "weight_g", "length_cm", "width_cm", "height_cm",
        "wax_type", "wax_weight_g", "wick_type", "container_type", "container_details",
        "box_price", "wrap_price", "business_card_cost", "labor_time", "labor_rate", 'image'
    ]
    
    data = {k: v for k, v in product_data.items() if k in columns}
    
    set_clause = ", ".join([f"{col} = %s" for col in data.keys()])
    values = list(data.values())
    values.append(product_id)
    
    sql = f"UPDATE {table} SET {set_clause} WHERE id = %s"
    
    try:
        cursor.execute(sql, values)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def delete_product(product_id, table=PRODUCTS_TABLE_NAME):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"DELETE FROM {table} WHERE id = %s", (product_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
def update_stock(product_id: int, delta: int, table=PRODUCTS_TABLE_NAME):
    """
    Update product stock quantity. 
    delta can be positive (add) or negative (deduct).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check current stock first (optional, but good for validation)
        # For now, just direct update
        sql = f"UPDATE {table} SET stock_quantity = stock_quantity + %s WHERE id = %s"
        cursor.execute(sql, (delta, product_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating stock: {e}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
