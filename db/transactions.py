from db.db_connection import get_db_connection
from config.config import TABLE_NAME

ALLOWED_TABLES = {"transactions", "transactions_test"}


def write_transaction(
    transaction_date,
    description,
    quantity,
    price,
    transaction_type,
    table=TABLE_NAME
):
    if table not in ALLOWED_TABLES:
        raise ValueError("Invalid table name")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = f"""
            INSERT INTO {table}
            (transaction_date, description, quantity, price, transaction_type)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            transaction_date,
            description,
            quantity,
            price,
            transaction_type
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

