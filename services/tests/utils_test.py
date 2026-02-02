import pytest
from services.utils import TransactionUtils

# Sample transactions for testing
SAMPLE_TRANSACTIONS = [
    {"transaction_date": "2025-01-05", "description": "Wax 464-45", "quantity": 17, "price": 12.5, "transaction_type": "expense", "total": 212.5},
    {"transaction_date": "2025-01-10", "description": "Candle Sale - Vanilla", "quantity": 10, "price": 25.0, "transaction_type": "income", "total": 250.0},
    {"transaction_date": "2025-02-15", "description": "Candle Sale - Chocolate", "quantity": 5, "price": 30.0, "transaction_type": "income", "total": 150.0},
    {"transaction_date": "2025-04-20", "description": "Wax Pillar", "quantity": 7, "price": 10.0, "transaction_type": "expense", "total": 70.0},
    {"transaction_date": "2024-12-31", "description": "Old Sale", "quantity": 3, "price": 20.0, "transaction_type": "income", "total": 60.0},
]

def test_calculate_summary():
    summary = TransactionUtils.calculate_summary(SAMPLE_TRANSACTIONS)

    assert summary['total_income'] == 460.0  # 250 + 150 + 60
    assert summary['total_expense'] == 282.5  # 212.5 + 70
    assert summary['balance'] == pytest.approx(177.5)
    assert summary['total_sold_units'] == 18  # 10 + 5 + 3
    assert summary['avg_price_per_unit'] == pytest.approx(460 / 18, 0.0001)

def test_calculate_summary_no_transactions():
    summary = TransactionUtils.calculate_summary([])
    assert summary['total_income'] == 0
    assert summary['total_expense'] == 0
    assert summary['balance'] == 0
    assert summary['total_sold_units'] == 0
    assert summary['avg_price_per_unit'] == 0

def test_calculate_summary_all_expenses():
    transactions = [t for t in SAMPLE_TRANSACTIONS if t['transaction_type'] == 'expense']
    summary = TransactionUtils.calculate_summary(transactions)
    assert summary['total_income'] == 0
    assert summary['total_expense'] > 0
    assert summary['balance'] == -summary['total_expense']
    assert summary['total_sold_units'] == 0
    assert summary['avg_price_per_unit'] == 0

def test_calculate_summary_all_income_zero_quantity():
    transactions = [{"transaction_date": "2025-01-01", "description": "Free Giveaway", "quantity": 0, "price": 0, "transaction_type": "income", "total": 0}]
    summary = TransactionUtils.calculate_summary(transactions)
    assert summary['total_income'] == 0
    assert summary['total_sold_units'] == 0
    assert summary['avg_price_per_unit'] == 0

# ---------------- Test filter_by_year ----------------
def test_filter_by_year():
    filtered = TransactionUtils.filter_by_year(SAMPLE_TRANSACTIONS, 2025)
    assert len(filtered) == 4
    for t in filtered:
        assert t['transaction_date'].startswith("2025-")

def test_filter_by_year_no_match():
    filtered = TransactionUtils.filter_by_year(SAMPLE_TRANSACTIONS, 2030)
    assert len(filtered) == 0

# ---------------- Test filter_by_month ----------------
def test_filter_by_month():
    filtered = TransactionUtils.filter_by_month(SAMPLE_TRANSACTIONS, 2025, 1)
    assert len(filtered) == 2  # Jan 2025: 1 expense + 1 income
    for t in filtered:
        assert t['transaction_date'].startswith("2025-01")

def test_filter_by_month_no_match():
    filtered = TransactionUtils.filter_by_month(SAMPLE_TRANSACTIONS, 2025, 12)
    assert len(filtered) == 0

# ---------------- Test filter_by_quarter ----------------
def test_filter_by_quarter():
    # Q1 2025 = Jan-Mar
    filtered = TransactionUtils.filter_by_quarter(SAMPLE_TRANSACTIONS, 2025, 1)
    assert len(filtered) == 3  # Jan + Feb transactions
    months = [int(t['transaction_date'][5:7]) for t in filtered]
    for m in months:
        assert 1 <= m <= 3

def test_filter_by_quarter_no_match():
    filtered = TransactionUtils.filter_by_quarter(SAMPLE_TRANSACTIONS, 2025, 3)  # Jul-Sep, no transactions
    assert len(filtered) == 0

@pytest.mark.parametrize(
    "input_text, expected",
    [
        ("   hello world   ", "hello world"),                   # leading/trailing spaces
        ("hello   world", "hello world"),                       # multiple spaces
        ("hello\tworld", "hello world"),                        # tab
        ("hello\nworld", "hello world"),                        # newline
        ("  hello \t\n world  ", "hello world"),               # combination
        ("", ""),                                               # empty string
        (None, ""),                                             # None input
        ("singleword", "singleword"),                           # no change
        ("  multiple   spaces\tand\nnewlines  ", "multiple spaces and newlines")
    ]
)
def test_normalize_text(input_text, expected):
    assert TransactionUtils.normalize_text(input_text) == expected

# ---------------- Test calculate_monthly_breakdown ----------------
def test_calculate_monthly_breakdown_2025():
    """Test monthly breakdown for 2025 with mixed transactions"""
    breakdown = TransactionUtils.calculate_monthly_breakdown(SAMPLE_TRANSACTIONS, 2025)
    
    # Should have 12 months
    assert len(breakdown) == 12
    
    # January 2025: 1 income (250.0) + 1 expense (212.5)
    assert breakdown[1]['income'] == 250.0
    assert breakdown[1]['expense'] == 212.5
    
    # February 2025: 1 income (150.0)
    assert breakdown[2]['income'] == 150.0
    assert breakdown[2]['expense'] == 0.0
    
    # March 2025: no transactions
    assert breakdown[3]['income'] == 0.0
    assert breakdown[3]['expense'] == 0.0
    
    # April 2025: 1 expense (70.0)
    assert breakdown[4]['income'] == 0.0
    assert breakdown[4]['expense'] == 70.0
    
    # May-December 2025: all zeros
    for month in range(5, 13):
        assert breakdown[month]['income'] == 0.0
        assert breakdown[month]['expense'] == 0.0

def test_calculate_monthly_breakdown_2024():
    """Test monthly breakdown for 2024"""
    breakdown = TransactionUtils.calculate_monthly_breakdown(SAMPLE_TRANSACTIONS, 2024)
    
    # December 2024: 1 income (60.0)
    assert breakdown[12]['income'] == 60.0
    assert breakdown[12]['expense'] == 0.0
    
    # All other months should be zero
    for month in range(1, 12):
        assert breakdown[month]['income'] == 0.0
        assert breakdown[month]['expense'] == 0.0

def test_calculate_monthly_breakdown_no_transactions():
    """Test monthly breakdown with empty transaction list"""
    breakdown = TransactionUtils.calculate_monthly_breakdown([], 2025)
    
    # All months should have zero income and expense
    for month in range(1, 13):
        assert breakdown[month]['income'] == 0.0
        assert breakdown[month]['expense'] == 0.0

def test_calculate_monthly_breakdown_wrong_year():
    """Test monthly breakdown for a year with no data"""
    breakdown = TransactionUtils.calculate_monthly_breakdown(SAMPLE_TRANSACTIONS, 2030)
    
    # All months should have zero income and expense
    for month in range(1, 13):
        assert breakdown[month]['income'] == 0.0
        assert breakdown[month]['expense'] == 0.0

def test_calculate_monthly_breakdown_multiple_same_month():
    """Test monthly breakdown with multiple transactions in same month"""
    transactions = [
        {"transaction_date": "2025-03-01", "transaction_type": "income", "total": 100.0},
        {"transaction_date": "2025-03-15", "transaction_type": "income", "total": 200.0},
        {"transaction_date": "2025-03-20", "transaction_type": "expense", "total": 50.0},
    ]
    breakdown = TransactionUtils.calculate_monthly_breakdown(transactions, 2025)
    
    # March should have summed values
    assert breakdown[3]['income'] == 300.0  # 100 + 200
    assert breakdown[3]['expense'] == 50.0
