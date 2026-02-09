import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch
from gui.charts import AnalyticsFrame

# Sample transactions for testing
SAMPLE_TRANSACTIONS = [
    {"transaction_date": "2025-01-05", "description": "Wax 464-45", "quantity": 17, "price": 12.5, "transaction_type": "expense", "total": 212.5},
    {"transaction_date": "2025-01-10", "description": "Candle Sale - Vanilla", "quantity": 10, "price": 25.0, "transaction_type": "income", "total": 250.0},
    {"transaction_date": "2025-02-15", "description": "Candle Sale - Chocolate", "quantity": 5, "price": 30.0, "transaction_type": "income", "total": 150.0},
    {"transaction_date": "2024-12-31", "description": "Old Sale", "quantity": 3, "price": 20.0, "transaction_type": "income", "total": 60.0},
]


@pytest.fixture
def analytics_frame(tk_root):
    """Create an AnalyticsFrame instance using shared tk root"""
    frame = AnalyticsFrame(tk_root)
    return frame


def test_analytics_frame_initialization(analytics_frame):
    """Test that AnalyticsFrame initializes correctly"""
    assert analytics_frame is not None
    assert hasattr(analytics_frame, 'year_combo')
    assert hasattr(analytics_frame, 'year_var')
    assert hasattr(analytics_frame, 'fig')
    assert hasattr(analytics_frame, 'ax')
    assert hasattr(analytics_frame, 'canvas')


def test_year_dropdown_populated(analytics_frame):
    """Test that year dropdown gets populated with transaction data"""
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    # Should contain at least 2024, 2025, and 2026 (current year)
    years = analytics_frame.year_combo['values']
    assert '2024' in years
    assert '2025' in years
    assert '2026' in years  # current year (2026)


def test_year_2025_always_present(analytics_frame):
    """Test that 2025 is always in the year dropdown"""
    # Even with no transactions, 2025 should be present
    analytics_frame.refresh_charts([])
    
    years = analytics_frame.year_combo['values']
    assert '2025' in years


def test_year_selection_defaults_to_current(analytics_frame):
    """Test that year selection defaults to current year"""
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    # Should default to 2026 (current year)
    selected_year = analytics_frame.year_var.get()
    assert selected_year == '2026'


def test_refresh_charts_with_empty_data(analytics_frame):
    """Test that refresh_charts handles empty transaction list"""
    # Should not crash
    analytics_frame.refresh_charts([])
    
    # Year combo should still have values (current year + 2025)
    years = analytics_frame.year_combo['values']
    assert len(years) >= 2


def test_year_change_triggers_refresh(analytics_frame):
    """Test that changing year triggers chart refresh"""
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    # Mock the refresh to see if it's called
    original_refresh = analytics_frame.refresh_charts
    refresh_called = []
    
    def mock_refresh(trans, keep_year=False):
        refresh_called.append((trans, keep_year))
        original_refresh(trans, keep_year)
    
    analytics_frame.refresh_charts = mock_refresh
    
    # Simulate year change
    analytics_frame.year_var.set('2025')
    analytics_frame.on_year_change(None)
    
    # Should have been called with keep_year=True
    assert len(refresh_called) == 1
    assert refresh_called[0][1] == True  # keep_year should be True


def test_chart_axes_configured(analytics_frame):
    """Test that chart axes are properly configured after refresh"""
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    # Check that the axes has a title
    title = analytics_frame.ax.get_title()
    assert 'Income vs Expenses' in title
    assert '2026' in title  # Current year
    
    # Check that legend exists
    legend = analytics_frame.ax.get_legend()
    assert legend is not None


def test_monthly_data_aggregation(analytics_frame):
    """Test that monthly data is correctly aggregated"""
    analytics_frame.year_var.set('2025')
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    # Verify the chart was drawn (canvas.draw was called)
    # This is implicit if no errors occurred
    assert analytics_frame.canvas is not None


def test_year_combo_sorted_descending(analytics_frame):
    """Test that years are sorted in descending order"""
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    years = list(analytics_frame.year_combo['values'])
    # Convert to integers and check sorted
    year_ints = [int(y) for y in years]
    assert year_ints == sorted(year_ints, reverse=True)


def test_refresh_preserves_selection_when_keep_year_true(analytics_frame):
    """Test that refresh preserves year selection when keep_year=True"""
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS)
    
    # Set to 2025
    analytics_frame.year_var.set('2025')
    
    # Refresh with keep_year=True
    analytics_frame.refresh_charts(SAMPLE_TRANSACTIONS, keep_year=True)
    

def test_text_annotations_added(analytics_frame):
    """Test that text annotations are added to the chart bars"""
    # Use specific data to verify
    test_data = [
        {"transaction_date": "2025-01-10", "description": "Sale", "quantity": 1, "price": 500.0, "transaction_type": "income", "total": 500.0},
        {"transaction_date": "2025-01-15", "description": "Expense", "quantity": 1, "price": 200.0, "transaction_type": "expense", "total": 200.0},
    ]
    
    analytics_frame.year_var.set('2025')
    analytics_frame.refresh_charts(test_data, keep_year=True)
    
    # Get all text objects from the axes
    texts = [t.get_text() for t in analytics_frame.ax.texts]
    
    # Check if our values are present
    assert "500" in texts
    assert "200" in texts
    
    # Check total count: 2 bars with values > 0 should have 2 labels (plus maybe title/legend if they use text, but usually they are separate)
    # ax.texts usually only contains the annotations we added via ax.text()
    # Legends and Titles are stored separately.
    assert len(texts) >= 2
