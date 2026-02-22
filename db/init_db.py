import os
from db.db_connection import get_db_connection
from config.config import (
    TABLE_NAME, PRODUCTS_TABLE_NAME, MATERIALS_TABLE, PRODUCT_IMAGES_TABLE,
    TRANSACTIONS_SCHEMA, PRODUCTS_SCHEMA, MATERIALS_SCHEMA, PRODUCT_IMAGES_SCHEMA,
    DB_SCHEMA
)

def generate_create_table_sql(table_name, schema):
    if not schema:
        print("Warning: DB_SCHEMA is empty. Cannot generate SQL.")
        return None
    
    columns_sql = []
    for col_name, col_def in schema.items():
        columns_sql.append(f"    {col_name} {col_def}")
    
    columns_block = ",\n".join(columns_sql)
    return f"CREATE TABLE IF NOT EXISTS {table_name} (\n{columns_block}\n);"

def create_table(table_name, schema):
    """
    Checks if table exists. If not, generates SQL from schema and creates it.
    If it does exist, it checks for missing columns and adds them via ALTER TABLE.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"Table '{table_name}' already exists. Checking for missing columns...")
            if not schema:
                print("Warning: DB_SCHEMA is empty. Cannot check columns.")
                return

            # Get existing columns
            cursor.execute(f"DESCRIBE {table_name}")
            existing_columns = [row['Field'] for row in cursor.fetchall()]

            # Find missing columns
            for col_name, col_def in schema.items():
                # Ignore foreign keys from this basic check
                if "FOREIGN KEY" in col_name.upper() or "PRIMARY KEY" in col_name.upper():
                    continue
                
                if col_name not in existing_columns:
                    print(f"Adding missing column '{col_name}' to '{table_name}'...")
                    alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def};"
                    try:
                        cursor.execute(alter_sql)
                        conn.commit()
                        print(f"Added '{col_name}' successfully.")
                    except Exception as alt_err:
                        print(f"Failed to add column '{col_name}': {alt_err}")
        else:
            print(f"Table '{table_name}' does not exist. Creating...")
            create_sql = generate_create_table_sql(table_name, schema)
            
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

def init_db(table_name=TABLE_NAME, schema=TRANSACTIONS_SCHEMA):
    create_table(table_name, schema)
    create_table(PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA)
    create_table(MATERIALS_TABLE, MATERIALS_SCHEMA)
    create_table(PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA)
