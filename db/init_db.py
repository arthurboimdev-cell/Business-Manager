import os
from db.db_connection import get_db_connection
from config.config import CONFIG_PATH

def load_creation_sql(table_name):
    # SQL file is in the same directory as config.json
    sql_path = CONFIG_PATH.parent / "create_table.sql"
    if not sql_path.exists():
        print(f"Warning: {sql_path} not found. Skipping table creation.")
        return None
    
    with open(sql_path, "r") as f:
        sql = f.read()
    
    return sql.replace("{table_name}", table_name)

def init_db(table_name):
    """
    Checks if table exists. If not, reads create_table.sql and creates it.
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
            create_sql = load_creation_sql(table_name)
            if create_sql:
                # Multiple statements might complicate things, but here we expect one block.
                # cursor.execute(create_sql) might fail if it contains multiple statements depending on driver.
                # But our SQL is a single CREATE TABLE statement.
                cursor.execute(create_sql)
                conn.commit()
                print(f"Table '{table_name}' created successfully.")
                
    except Exception as e:
        print(f"Database initialization failed: {e}")
    finally:
        cursor.close()
        conn.close()
