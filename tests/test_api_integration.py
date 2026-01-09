import subprocess
import sys
import time
import requests
import pytest
import os

from config.config import SERVER_HOST, SERVER_PORT, SERVER_URL

@pytest.fixture(scope="module")
def api_server():
    """Start the server for the test session"""
    print("Starting test server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", SERVER_HOST, "--port", str(SERVER_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3) # Wait for startup
    yield process
    print("Stopping test server...")
    process.terminate()
    process.wait()

def test_server_connectivity(api_server):
    """Test that the server is reachable"""
    try:
        response = requests.get(f"{SERVER_URL}/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    except requests.exceptions.ConnectionError:
        pytest.fail("Could not connect to server")

def test_get_transactions(api_server):
    """Test fetching transactions via API"""
    response = requests.get(f"{SERVER_URL}/transactions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_transaction(api_server):
    """Test adding a transaction via API"""
    payload = {
        "date": "2025-01-01",
        "description": "API Test",
        "quantity": 1,
        "price": 10.0,
        "type": "income",
        "supplier": "TestSupplier"
    }
    response = requests.post(f"{SERVER_URL}/transactions", json=payload)
    assert response.status_code == 200
    assert "id" in response.json()
