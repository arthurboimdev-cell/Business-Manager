from db.db_connection import get_db_connection
from config.config import MATERIALS_TABLE

def add_material(name, category, stock_quantity, unit_cost, unit_type, table=MATERIALS_TABLE):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"""
            INSERT INTO {table} (name, category, stock_quantity, unit_cost, unit_type)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, category, stock_quantity, unit_cost, unit_type))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_materials(table=MATERIALS_TABLE):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM {table} ORDER BY category, name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_material(material_id, name, category, stock_quantity, unit_cost, unit_type, table=MATERIALS_TABLE):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = f"""
            UPDATE {table}
            SET name=%s, category=%s, stock_quantity=%s, unit_cost=%s, unit_type=%s
            WHERE id=%s
        """
        cursor.execute(query, (name, category, stock_quantity, unit_cost, unit_type, material_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def delete_material(material_id, table=MATERIALS_TABLE):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {table} WHERE id=%s", (material_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def deduct_stock_by_name(name, amount, table=MATERIALS_TABLE):
    """
    Find material by exact name (case-insensitive) and deduct quantity.
    """
    if not name:
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Find ID
        cursor.execute(f"SELECT id, stock_quantity FROM {table} WHERE name = %s", (name,))
        row = cursor.fetchone()
        
        if row:
            m_id = row[0]
            # 2. Update
            cursor.execute(f"UPDATE {table} SET stock_quantity = stock_quantity - %s WHERE id = %s", (amount, m_id))
            conn.commit()
            return True, f"Deducted {amount} from {name}"
        else:
            return False, f"Material '{name}' not found"
    except Exception as e:
        print(f"Error deducting material stock: {e}")
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
