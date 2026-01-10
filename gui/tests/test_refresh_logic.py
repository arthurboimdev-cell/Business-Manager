import pytest
from unittest.mock import MagicMock
from gui.controller import TransactionController
from gui.tabs.materials_tab import MaterialsTab
from gui.tabs.products_tab import ProductsTab

@pytest.fixture
def mock_controller(mocker):
    # Mock dependencies that require GUI
    mocker.patch('gui.controller.MainWindow', MagicMock())
    mocker.patch('gui.controller.InputFrame', MagicMock())
    mocker.patch('gui.controller.TreeFrame', MagicMock())
    mocker.patch('gui.controller.SummaryFrame', MagicMock())
    mocker.patch('gui.controller.AnalyticsFrame', MagicMock())
    
    # Mock Tabs
    mocker.patch('gui.controller.MaterialsTab', MagicMock())
    mocker.patch('gui.controller.ProductsTab', MagicMock())
    
    # Mock Model
    mocker.patch('gui.controller.TransactionModel', MagicMock())
    
    ctrl = TransactionController("transactions_test")
    return ctrl

def test_refresh_ui_calls_tabs(mock_controller):
    # Setup mocks
    mock_controller.products_tab = MagicMock()
    mock_controller.materials_tab = MagicMock()
    
    # Call refresh_ui
    mock_controller.refresh_ui()
    
    # Verify calls
    mock_controller.products_tab.refresh_prods_and_mats.assert_called_once()
    mock_controller.materials_tab.refresh.assert_called_once()
