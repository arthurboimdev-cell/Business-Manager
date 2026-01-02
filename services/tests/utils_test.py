import pytest
from services.utils import TransactionUtils

# Sample transactions for testing
SAMPLE_TRANSACTIONS = [
    {"date": "2025-01-05", "description": "Wax 464-45", "quantity": 17, "price": 12.5, "transaction_type": "expense", "total": 212.5},
    {"date": "2025-01-10", "description": "Candle Sale - Vanilla", "quantity": 10, "price": 25.0, "transaction_type": "income", "total": 250.0},
    {"date": "2025-02-15", "description": "Candle Sale - Chocolate", "quantity": 5, "price": 30.0, "transaction_type": "income", "total": 150.0},
    {"date": "2025-04-20", "description": "Wax Pillar", "quantity": 7, "price": 10.0, "transaction_type": "expense", "total": 70.0},
    {"date": "2024-12-31", "description": "Old Sale", "quantity": 3, "price": 20.0, "transaction_type": "income", "total": 60.0},
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
    transactions = [{"date": "2025-01-01", "description": "Free Giveaway", "quantity": 0, "price": 0, "transaction_type": "income", "total": 0}]
    summary = TransactionUtils.calculate_summary(transactions)
    assert summary['total_income'] == 0
    assert summary['total_sold_units'] == 0
    assert summary['avg_price_per_unit'] == 0

# ---------------- Test filter_by_year ----------------
def test_filter_by_year():
    filtered = TransactionUtils.filter_by_year(SAMPLE_TRANSACTIONS, 2025)
    assert len(filtered) == 4
    for t in filtered:
        assert t['date'].startswith("2025-")

def test_filter_by_year_no_match():
    filtered = TransactionUtils.filter_by_year(SAMPLE_TRANSACTIONS, 2030)
    assert len(filtered) == 0

# ---------------- Test filter_by_month ----------------
def test_filter_by_month():
    filtered = TransactionUtils.filter_by_month(SAMPLE_TRANSACTIONS, 2025, 1)
    assert len(filtered) == 2  # Jan 2025: 1 expense + 1 income
    for t in filtered:
        assert t['date'].startswith("2025-01")

def test_filter_by_month_no_match():
    filtered = TransactionUtils.filter_by_month(SAMPLE_TRANSACTIONS, 2025, 12)
    assert len(filtered) == 0

# ---------------- Test filter_by_quarter ----------------
def test_filter_by_quarter():
    # Q1 2025 = Jan-Mar
    filtered = TransactionUtils.filter_by_quarter(SAMPLE_TRANSACTIONS, 2025, 1)
    assert len(filtered) == 3  # Jan + Feb transactions
    months = [int(t['date'][5:7]) for t in filtered]
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