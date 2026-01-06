import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load local.env (same folder as this file)
env_path = Path(__file__).parent / "local.env"
load_dotenv(env_path)

# --- Load JSON Configuration ---
# Config is now inside the config folder, same as this script
CONFIG_PATH = Path(__file__).parent / 'config.json'
FEATURES_PATH = Path(__file__).parent / 'features.json'

config_from_json = {}
if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config_from_json = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}")

features_config = {
    "analytics": True,
    "export_csv": True,
    "search": True,
    "summary_stats": True,
    "dark_mode_toggle": True
}
if FEATURES_PATH.exists():
    try:
        with open(FEATURES_PATH, 'r') as f:
            file_data = json.load(f)
            for key, value in file_data.items():
                if isinstance(value, bool):
                    features_config[key] = value
                elif isinstance(value, dict) and "enabled" in value:
                    features_config[key] = value["enabled"]
    except Exception as e:
        print(f"Warning: Could not load features.json: {e}")

# Determine Database Name
# 1. Check if JSON defines a specific env var to use
db_env_var = config_from_json.get("data", {}).get("database_env_var")
if db_env_var:
    db_name = os.getenv(db_env_var)
else:
    # 2. Fallback to hardcoded JSON value or default env var
    db_name = config_from_json.get("data", {}).get("database") or os.getenv("DB_NAME")

mysql_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": db_name,
}

# Default Defaults (Fallback)
defaults = {
    "app": {"title": "Business Manager", "theme": "superhero"},
    "data": {"table_name": "transactions", "test_table": "transactions_test", 
             "columns": ["date", "description", "quantity", "price", "transaction_type", "total", "supplier"]},
    "ui": {
        "labels": {
            "date": "Date:", "description": "Description:", "quantity": "Qty:", 
            "price": "Price:", "supplier": "Supplier:", "type": "Type:"
        },
        "buttons": {
            "add": "Add", "update": "Update", "clear": "Clear", 
            "export": "Export", "filter": "Filter", "reset": "Reset"
        }
    },
    "transaction_types": ["expense", "income"]
}

config_data = defaults
if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, 'r') as f:
            file_config = json.load(f)
            # Merge logic could go here, for now simple override or direct use
            # We'll trust the file if it exists, maybe merging is safer but simple is better for now
            # Let's simple merge top keys
            for key in defaults:
                if key in file_config:
                    config_data[key] = file_config[key]
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}")

# Expose constants for existing code compatibility
TABLE_NAME = config_data["data"]["table_name"]
TEST_TABLE = config_data["data"]["test_table"]
WINDOW_TITLE = config_data["app"]["title"]
TREE_COLUMNS = config_data["data"]["columns"]
TRANSACTION_TYPES = config_data["transaction_types"]

# UI Text Constants
BUTTON_ADD = config_data["ui"]["buttons"].get("add", "Add Transaction")
BUTTON_UPDATE = config_data["ui"]["buttons"].get("update", "Update Transaction")
BUTTON_REFRESH = config_data["ui"]["buttons"].get("refresh", "Refresh")
BUTTON_CLEAR = config_data["ui"]["buttons"].get("clear", "Clear Entries")

# Labels (New dictionary to access from views)
UI_LABELS = config_data["ui"]["labels"]
UI_BUTTONS = config_data["ui"]["buttons"]
FEATURES = features_config
FEATURES = features_config
