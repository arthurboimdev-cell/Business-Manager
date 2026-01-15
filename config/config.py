import os
import sys
import json
from dotenv import load_dotenv
from pathlib import Path

# Load local.env (same folder as this file)
# Load local.env (same folder as this file)
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    # 1. Try external config/local.env next to exe (allows user override)
    base_dir = Path(sys.executable).parent
    external_env = base_dir / "config" / "local.env"
    
    if external_env.exists():
        env_path = external_env
    else:
        # 2. Fallback to internal bundled file
        # PyInstaller extracts to sys._MEIPASS
        env_path = Path(getattr(sys, "_MEIPASS", ".")) / "config" / "local.env"
else:
    # Running as script
    env_path = Path(__file__).parent / "local.env"

load_dotenv(env_path)

# --- Load JSON Configuration ---
# Config is now inside the config folder, same as this script
# Handle paths for frozen app
if getattr(sys, 'frozen', False):
    # If frozen, use the executable's directory or _internal depending on PyInstaller mode
    # Usually relative to sys._MEIPASS or sys.executable
    # For external config (editable by user), usually next to exe:
    BASE_DIR = Path(sys.executable).parent
    # Check if we should look in internal or external
    # Let's verify if 'config/config.json' exists next to exe
    if (BASE_DIR / 'config' / 'config.json').exists():
         CONFIG_PATH = BASE_DIR / 'config' / 'config.json'
         FEATURES_PATH = BASE_DIR / 'config' / 'features.json'
    else:
         # Fallback to internal (bundled)
         CONFIG_PATH = Path(__file__).parent / 'config.json'
         FEATURES_PATH = Path(__file__).parent / 'features.json'
else:
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

# Shipping Configuration
CHIT_CHATS_CLIENT_ID = os.getenv("CHIT_CHATS_CLIENT_ID", "")
CHIT_CHATS_ACCESS_TOKEN = os.getenv("CHIT_CHATS_ACCESS_TOKEN", "")
CHIT_CHATS_API_URL = os.getenv("CHIT_CHATS_API_URL", "https://chitchats.com/api/v1")

# Default Defaults (Fallback)
defaults = {
    "app": {"title": "Business Manager", "theme": "superhero"},
    "data": {
        "transactions_table": "transactions",
        "transactions_test_table": "transactions_test",
        "products_table": "products",
        "products_test_table": "products_test",
        "transaction_columns": ["date", "description", "quantity", "price", "transaction_type", "total", "supplier"],
        "transactions_schema": {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "transaction_date": "DATE",
            "description": "VARCHAR(255)",
            "quantity": "INT",
            "price": "DECIMAL(10, 2)",
            "transaction_type": "VARCHAR(50)",
            "total": "DECIMAL(10, 2)",
            "supplier": "VARCHAR(255)",
            "product_id": "INT DEFAULT NULL"
        },
        "products_schema": {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "title": "VARCHAR(255) NOT NULL",
            "sku": "VARCHAR(50)",
            "upc": "VARCHAR(50)",
            "description": "TEXT",
            "weight_g": "DECIMAL(10, 2)",
            "length_cm": "DECIMAL(10, 2)",
            "width_cm": "DECIMAL(10, 2)",
            "height_cm": "DECIMAL(10, 2)",
            "wax_type": "VARCHAR(100)",
            "wax_weight_g": "DECIMAL(10, 2)",
            "wax_rate": "DECIMAL(10, 4) DEFAULT 0.0000",
            "fragrance_type": "VARCHAR(100)",
            "fragrance_weight_g": "DECIMAL(10, 2)",
            "fragrance_rate": "DECIMAL(10, 4) DEFAULT 0.0000",
            "wick_type": "VARCHAR(100)",
            "wick_rate": "DECIMAL(10, 4) DEFAULT 0.0000",
            "wick_quantity": "INT DEFAULT 1",
            "container_type": "VARCHAR(100)",
            "container_rate": "DECIMAL(10, 2) DEFAULT 0.00",
            "container_quantity": "INT DEFAULT 1",
            "container_details": "VARCHAR(255)",
            "box_type": "VARCHAR(100)",
            "box_price": "DECIMAL(10, 2)",
            "box_quantity": "INT DEFAULT 1",
            "wrap_price": "DECIMAL(10, 2)",
            "business_card_cost": "DECIMAL(10, 2)",
            "labor_time": "INT DEFAULT 0",
            "labor_rate": "DECIMAL(10, 2) DEFAULT 0.00",
            "selling_price": "DECIMAL(10, 2) DEFAULT 0.00",
            "amazon_data": "JSON", 
            "etsy_data": "JSON", 
            "common_data": "JSON",
            "image": "LONGBLOB" # Legacy single image, keeping for compatibility
        },
        "product_images_schema": {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "product_id": "INT", 
            "image_data": "LONGBLOB",
            "image_url": "TEXT",
            "display_order": "INT DEFAULT 0",
            "FOREIGN KEY (product_id)": "REFERENCES products(id) ON DELETE CASCADE"
        },
        "materials_table": "materials",
        "materials_test_table": "materials_test",
        "materials_schema": {
            "id": "INT AUTO_INCREMENT PRIMARY KEY",
            "name": "VARCHAR(255)",
            "category": "VARCHAR(50)",
            "stock_quantity": "DECIMAL(10, 2) DEFAULT 0.00",
            "unit_cost": "DECIMAL(10, 4)",
            "unit_type": "VARCHAR(20)"
        },
        "default_labor_rate": 17.60
    },
    "pricing": {
        "enabled": True,
        "markup_max": 5.0,
        "markup_min": 1.5,
        "decay_factor": 20.0
    },
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
            # Merge logic: update defaults with file content, allowing new keys
            config_data.update(file_config)
    except Exception as e:
        print(f"Warning: Could not load config.json: {e}")

# Expose constants for existing code compatibility
import sys

# ... previous imports ...

# Expose constants for existing code compatibility
# Logic: If running as compiled exe (frozen), use production table.
#        If running as script (dev/IDE), use test table to protect real data.
is_frozen = getattr(sys, 'frozen', False)

if is_frozen:
     TABLE_NAME = config_data["data"]["transactions_table"]
     PRODUCTS_TABLE_NAME = config_data["data"]["products_table"]
     MATERIALS_TABLE_NAME = config_data["data"]["materials_table"]
else:
     TABLE_NAME = config_data["data"]["transactions_test_table"]
     PRODUCTS_TABLE_NAME = config_data["data"]["products_test_table"]
     MATERIALS_TABLE_NAME = config_data["data"]["materials_test_table"]

TEST_TABLE = config_data["data"]["transactions_test_table"]
DB_SCHEMA = config_data["data"].get("transactions_schema", {}) # Backward compat
TRANSACTIONS_SCHEMA = config_data["data"].get("transactions_schema", {})
PRODUCTS_SCHEMA = config_data["data"].get("products_schema", {})
PRODUCT_IMAGES_SCHEMA = config_data["data"].get("product_images_schema", {})
# Fix FK to point to correct table (test vs prod)
if "FOREIGN KEY (product_id)" in PRODUCT_IMAGES_SCHEMA:
    PRODUCT_IMAGES_SCHEMA["FOREIGN KEY (product_id)"] = f"REFERENCES {PRODUCTS_TABLE_NAME}(id) ON DELETE CASCADE"
    
MATERIALS_SCHEMA = config_data["data"].get("materials_schema", {})
MATERIALS_TABLE = MATERIALS_TABLE_NAME
PRODUCT_IMAGES_TABLE = "product_images" # Default, or from config if added later

WINDOW_TITLE = config_data["app"]["title"]
TREE_COLUMNS = config_data["data"]["transaction_columns"]
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
# Server Configuration
SERVER_HOST = config_data.get("app", {}).get("server", {}).get("host", "127.0.0.1")
SERVER_PORT = config_data.get("app", {}).get("server", {}).get("port", 8000)
SERVER_URL = f"http://{SERVER_HOST}:{SERVER_PORT}"

FEATURES = features_config

# Labor Configuration
DEFAULT_LABOR_RATE = float(os.getenv("DEFAULT_LABOR_RATE", 17.60))

# Manufacturing / BOM
MANUFACTURING_CONFIG = config_data.get("manufacturing", {})
BOM_LAYOUT = MANUFACTURING_CONFIG.get("bom_layout", [])
