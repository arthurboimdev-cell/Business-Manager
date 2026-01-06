import os
from db.db_connection import get_db_connection
from config.config import DB_SCHEMA

def generate_create_table_sql(table_name, schema):
    if not schema:
        print("Warning: DB_SCHEMA is empty. Cannot generate SQL.")
        return None
    
    columns_sql = []
    for col_name, col_def in schema.items():
        columns_sql.append(f"    {col_name} {col_def}")
    
    columns_block = ",\n".join(columns_sql)
    return f"CREATE TABLE IF NOT EXISTS {table_name} (\n{columns_block}\n);"

def init_db(table_name):
    """
    Checks if table exists. If not, generates SQL from DB_SCHEMA and creates it.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"Table '{table_name}' already exists.")
        else:
            print(f"Table '{table_name}' does not exist. Creating...")
            create_sql = generate_create_table_sql(table_name, DB_SCHEMA)
            
            if create_sql:
                cursor.execute(create_sql)
                conn.commit()
                print(f"Table '{table_name}' created successfully.")
            else:
                print(f"Failed to create table '{table_name}': No schema defined.")
                
    except Exception as e:
        print(f"Database initialization failed: {e}")
    finally:
        cursor.close()
        conn.close()
