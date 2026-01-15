import json
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
        "title", "sku", "upc", "description", "stock_quantity", "weight_g", "length_cm", "width_cm", "height_cm",
        "wax_type", "wax_weight_g", "wax_rate", 
        "fragrance_type", "fragrance_weight_g", "fragrance_rate",
        "wick_type", "wick_rate", "wick_quantity", 
        "container_type", "container_rate", "container_quantity", "container_unit", "container_details",
        "second_container_type", "second_container_weight_g", "second_container_rate",
        "box_type", "box_price", "box_quantity", "wrap_price", "business_card_cost", "labor_time", "labor_rate", "selling_price", 
        "amazon_data", "etsy_data", "common_data", 'image'
    ]
    
    # Filter data to only valid columns
    data = {k: v for k, v in product_data.items() if k in columns}
    
    # JSON Serialization
    if 'amazon_data' in data and not isinstance(data['amazon_data'], str):
        data['amazon_data'] = json.dumps(data['amazon_data'])
    if 'etsy_data' in data and not isinstance(data['etsy_data'], str):
        data['etsy_data'] = json.dumps(data['etsy_data'])
    if 'common_data' in data and not isinstance(data['common_data'], str):
        data['common_data'] = json.dumps(data['common_data'])
    
    cols_str = ", ".join(data.keys())
    # placeholders: %s
    placeholders = ", ".join(["%s"] * len(data))
    
    sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
    
    sql = f"INSERT INTO {table} ({cols_str}) VALUES ({placeholders})"
    
    cursor.execute(sql, list(data.values()))
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return new_id

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
        "title", "sku", "upc", "description", "stock_quantity", "weight_g", "length_cm", "width_cm", "height_cm",
        "wax_type", "wax_weight_g", "wax_rate", 
        "fragrance_type", "fragrance_weight_g", "fragrance_rate",
        "wick_type", "wick_rate", "wick_quantity",
        "container_type", "container_rate", "container_quantity", "container_unit", "container_details",
        "second_container_type", "second_container_weight_g", "second_container_rate",
        "box_type", "box_price", "box_quantity", "wrap_price", "business_card_cost", "labor_time", "labor_rate", "total_cost", "selling_price",
        "amazon_data", "etsy_data", "common_data", 'image'
    ]
    
    data = {k: v for k, v in product_data.items() if k in columns}
    
    # JSON Serialization
    if 'amazon_data' in data and not isinstance(data['amazon_data'], str):
        data['amazon_data'] = json.dumps(data['amazon_data'])
    if 'etsy_data' in data and not isinstance(data['etsy_data'], str):
        data['etsy_data'] = json.dumps(data['etsy_data'])
    if 'common_data' in data and not isinstance(data['common_data'], str):
        data['common_data'] = json.dumps(data['common_data'])
        
    set_clause = ", ".join([f"{k} = %s" for k in data.keys()])
    values = list(data.values())
    values.append(product_id)
    
    sql = f"UPDATE {table} SET {set_clause} WHERE id = %s"
    
    sql = f"UPDATE {table} SET {set_clause} WHERE id = %s"
    
    cursor.execute(sql, values)
    conn.commit()
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

# --- Image Management ---
def add_product_image(product_id, image_data, display_order=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO product_images (product_id, image_data, display_order) VALUES (%s, %s, %s)"
        cursor.execute(sql, (product_id, image_data, display_order))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        print(f"Error adding image: {err}")
    finally:
        cursor.close()
        conn.close()

def get_product_images(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = "SELECT * FROM product_images WHERE product_id = %s ORDER BY display_order ASC"
        cursor.execute(sql, (product_id,))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error fetching images: {err}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_product_image(image_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "DELETE FROM product_images WHERE id = %s"
        cursor.execute(sql, (image_id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error deleting image: {err}")
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
