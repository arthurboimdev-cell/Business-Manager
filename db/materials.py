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
