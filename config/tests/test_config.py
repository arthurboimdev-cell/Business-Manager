import json
from pathlib import Path
import pytest
import sys
import os

# Add project root to sys.path to allow imports from config
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config import config

def test_config_json_validity():
    """Test that config.json is valid JSON."""
    config_path = Path(__file__).parent.parent / 'config.json'
    assert config_path.exists(), "config.json not found"
    
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    assert isinstance(data, dict), "Root element should be a dict"
    assert "app" in data, "'app' key missing"
    assert "data" in data, "'data' key missing"
    assert "ui" in data, "'ui' key missing"

def test_config_loading():
    """Test that config.py correctly loads values."""
    # Check a few key values to ensure they match what's in the JSON
    # Note: These assertions depend on the current content of config.json
    
    # App
    assert config.WINDOW_TITLE == "Business Transactions Manager"
    
    # Data
    # In non-frozen environment (like tests), we expect the test table
    assert config.TABLE_NAME == "transactions_test"
    assert "date" in config.TREE_COLUMNS
    
    # UI
    # We might need to access the raw dictionary if config.py doesn't expose everything as top-level constants yet
    # But checking exposed constants is better for integration testing
    assert config.BUTTON_ADD == "Add Transaction"
