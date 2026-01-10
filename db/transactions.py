from db.db_connection import get_db_connection
from config.config import TABLE_NAME

ALLOWED_TABLES = {"transactions", "transactions_test"}


def write_transaction(
    transaction_date,
    description,
    quantity,
    price,
    transaction_type,
    supplier=None,
    product_id=None,
    table=TABLE_NAME
):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f"""
            INSERT INTO {table}
            (transaction_date, description, quantity, price, supplier, transaction_type, product_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            transaction_date,
            description,
            quantity,
            price,
            supplier,
            transaction_type,
            product_id
        ))
        conn.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        conn.close()


def read_transactions(table=TABLE_NAME):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(f"""
            SELECT
                id,
                transaction_date,
                description,
                quantity,
                price,
                total,
                transaction_type,
                supplier,
                product_id,
                created_at
            FROM {table}
            ORDER BY transaction_date DESC
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

def delete_transaction(transaction_id, table=TABLE_NAME):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE id=%s", (transaction_id,))
    conn.commit()
    cursor.close()
    conn.close()

    conn.close()


def update_transaction(
    transaction_id,
    transaction_date,
    description,
    quantity,
    price,
    transaction_type,
    supplier=None,
    table=TABLE_NAME
):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f"""
            UPDATE {table}
            SET
                transaction_date = %s,
                description = %s,
                quantity = %s,
                price = %s,
                supplier = %s,
                transaction_type = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            transaction_date,
            description,
            quantity,
            price,
            supplier,
            transaction_type,
            transaction_id
        ))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
