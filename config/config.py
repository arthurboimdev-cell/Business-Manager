import os
from dotenv import load_dotenv
from pathlib import Path

# Load local.env (same folder as this file)
env_path = Path(__file__).parent / "local.env"
load_dotenv(env_path)

mysql_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# Safety check (fail fast)
missing = [k for k, v in mysql_config.items() if not v]
if missing:
    raise RuntimeError(f"Missing DB config values: {', '.join(missing)}")

# Default table used by the application
TABLE_NAME = "transactions"

# Database
TEST_TABLE = "transactions_test"

# GUI
WINDOW_TITLE = "Business Transactions Manager"

# Columns to display in the treeview
TREE_COLUMNS = ["date", "description", "quantity", "price", "transaction_type", "total", "supplier"]


# Button texts
BUTTON_ADD = "Add Transaction"
BUTTON_REFRESH = "Refresh"
BUTTON_CLEAR = "Clear Entries"

# Transaction types
TRANSACTION_TYPES = ["expense", "income"]
