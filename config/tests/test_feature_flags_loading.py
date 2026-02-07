
import pytest
import sys
import json
from unittest.mock import patch, mock_open
from pathlib import Path

# We need to import the config module to test its logic
# Since config executes on import, we might need to reload it in tests
import config.config
from importlib import reload

@pytest.fixture
def mock_features_json():
    return json.dumps({
        "marketplace": {"enabled": False},
        "shipping": {"enabled": True}
    })

@pytest.fixture(autouse=True)
def cleanup_config():
    """Ensure config is restored to normal dev state after tests."""
    yield
    # Restore normal state (sys.frozen is False by default in pytest)
    with patch('sys.frozen', False, create=True):
         reload(config.config)

def test_load_features_dev_mode(mock_features_json):
    """Test loading features.json in normal dev mode."""
    with patch('sys.frozen', False, create=True):
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            with patch('builtins.open', mock_open(read_data=mock_features_json)):
                reload(config.config)
                
                assert config.config.features_config['marketplace'] is False
                assert config.config.features_config['shipping'] is True

def test_load_features_frozen_mode(mock_features_json):
    """Test loading features.json in frozen (PyInstaller) mode."""
    # Simulate frozen environment
    with patch('sys.frozen', True, create=True):
        with patch('sys.executable', r'C:\dist\main.exe'):
            # Mock Path checks to simulate external config exists
            with patch('pathlib.Path.exists') as mock_exists:
                # We want the external path check to return True
                # The logic checks (BASE_DIR / 'config' / 'config.json').exists()
                mock_exists.side_effect = lambda: True
                
                with patch('builtins.open', mock_open(read_data=mock_features_json)):
                    reload(config.config)
                    
                    # Verify it loaded from the external path
                    # We can check if FEATURES_PATH is correct
                    expected_path = Path(r'C:\dist\config\features.json')
                    assert config.config.FEATURES_PATH == expected_path
                    assert config.config.features_config['marketplace'] is False

def test_load_features_frozen_fallback(mock_features_json):
    """Test fallback to internal features.json if external is missing in frozen mode."""
    with patch('sys.frozen', True, create=True):
        with patch('sys.executable', r'C:\dist\main.exe'):
                # Mock Path checks
            with patch('pathlib.Path.exists') as mock_exists:
                # First check is for external config (False), subsequent checks are for internal (True)
                # It checks config.json external, then config.json internal, then features.json internal
                # Use iterator to ensure we don't run out of values (StopIteration)
                mock_exists.side_effect = (x for x in [False] + [True]*100)
                
                # Internal fallback
                with patch('builtins.open', mock_open(read_data=mock_features_json)):
                    reload(config.config)
                    
                    # Should point to internal path (parent of config.py)
                    # Note: exact path depends on where config.py thinks it is
                    assert config.config.features_config['marketplace'] is False
