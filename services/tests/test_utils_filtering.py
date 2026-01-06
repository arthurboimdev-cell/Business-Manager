import pytest
from services.utils import TransactionUtils

@pytest.fixture
def sample_transactions():
    return [
        {"transaction_date": "2023-01-15", "total": 100},
        {"transaction_date": "2023-02-20", "total": 200},
        {"transaction_date": "2023-05-10", "total": 300},
        {"transaction_date": "2024-01-05", "total": 400},
    ]

def test_filter_by_year(sample_transactions):
    results = TransactionUtils.filter_by_year(sample_transactions, 2023)
    assert len(results) == 3
    assert all(t['transaction_date'].startswith("2023") for t in results)

    results_2024 = TransactionUtils.filter_by_year(sample_transactions, 2024)
    assert len(results_2024) == 1
    assert results_2024[0]['transaction_date'] == "2024-01-05"

def test_filter_by_month(sample_transactions):
    # Filter for January 2023
    results = TransactionUtils.filter_by_month(sample_transactions, 2023, 1)
    assert len(results) == 1
    assert results[0]['transaction_date'] == "2023-01-15"

def test_filter_by_quarter(sample_transactions):
    # Q1: Jan, Feb, Mar
    results_q1 = TransactionUtils.filter_by_quarter(sample_transactions, 2023, 1)
    assert len(results_q1) == 2  # Jan and Feb
    assert {"transaction_date": "2023-01-15", "total": 100} in results_q1
    assert {"transaction_date": "2023-02-20", "total": 200} in results_q1

    # Q2: Apr, May, Jun
    results_q2 = TransactionUtils.filter_by_quarter(sample_transactions, 2023, 2)
    assert len(results_q2) == 1
    assert results_q2[0]['transaction_date'] == "2023-05-10"
