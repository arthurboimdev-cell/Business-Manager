import pytest
from unittest.mock import MagicMock
from gui.controller import TransactionController

# We need to test the logic in __init__.
# Since TransactionController imports FEATURES from config, we need to mock that import or the logic that uses it.
# Ideally we pass features as dependency injection, but for now we patch config.config.FEATURES

@pytest.fixture
def mock_controller_no_analytics():
    # Mock dependencies
    with pytest.MonkeyPatch.context() as m:
        m.setattr("gui.controller.MainWindow", MagicMock())
        m.setattr("gui.controller.InputFrame", MagicMock())
        m.setattr("gui.controller.TreeFrame", MagicMock())
        m.setattr("gui.controller.SummaryFrame", MagicMock())
        m.setattr("gui.controller.AnalyticsFrame", MagicMock())
        m.setattr("gui.controller.TransactionModel", MagicMock())
        
        # Patch FEATURES to disable analytics
        features = {
            "analytics": False,
            "summary_stats": True, 
            "search": True,
            "export_csv": True
        }
        m.setattr("gui.controller.FEATURES", features)

        ctrl = TransactionController("test_table")
        return ctrl

@pytest.fixture
def mock_controller_no_summary():
    with pytest.MonkeyPatch.context() as m:
        m.setattr("gui.controller.MainWindow", MagicMock())
        m.setattr("gui.controller.InputFrame", MagicMock())
        m.setattr("gui.controller.TreeFrame", MagicMock())
        # SummaryFrame constructor mock
        m.setattr("gui.controller.SummaryFrame", MagicMock())
        m.setattr("gui.controller.AnalyticsFrame", MagicMock())
        m.setattr("gui.controller.TransactionModel", MagicMock())
        
        features = {
            "analytics": True,
            "summary_stats": False,
            "search": True,
            "export_csv": True
        }
        m.setattr("gui.controller.FEATURES", features)

        ctrl = TransactionController("test_table")
        return ctrl

def test_analytics_disabled(mock_controller_no_analytics):
    """Test that AnalyticsFrame is not created when disabled"""
    ctrl = mock_controller_no_analytics
    
    # Check that analytics_frame is None
    assert ctrl.analytics_frame is None
    
    # Check that hide_analytics_tab was called on view
    ctrl.view.hide_analytics_tab.assert_called_once()

def test_summary_disabled(mock_controller_no_summary):
    """Test that SummaryFrame is not created when disabled"""
    ctrl = mock_controller_no_summary
    
    assert ctrl.summary_frame is None
    
    # refresh_ui shouldn't crash
    ctrl.refresh_ui()

# To test TreeFrame features (search/export) we need to inspect the TreeFrame calls or implementation
# In Controller init:
# self.tree_frame = TreeFrame(..., features=FEATURES)
# We can verify that features are passed correctly.

def test_features_passed_to_tree_frame():
    with pytest.MonkeyPatch.context() as m:
        m.setattr("gui.controller.MainWindow", MagicMock())
        m.setattr("gui.controller.InputFrame", MagicMock())
        mock_tree_class = MagicMock()
        m.setattr("gui.controller.TreeFrame", mock_tree_class) # Mock the class
        m.setattr("gui.controller.SummaryFrame", MagicMock())
        m.setattr("gui.controller.AnalyticsFrame", MagicMock())
        m.setattr("gui.controller.TransactionModel", MagicMock())
        
        custom_features = {"search": False, "export_csv": False, "analytics": True, "summary_stats": True}
        m.setattr("gui.controller.FEATURES", custom_features)
        
        ctrl = TransactionController("test_table")
        
        # Verify TreeFrame initialized with our features
        call_args = mock_tree_class.call_args
        # kwargs should contain features
        assert call_args.kwargs['features'] == custom_features
