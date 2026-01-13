import pytest
from unittest.mock import MagicMock, patch
from services.shipping_service import ChitChatsProvider

@pytest.fixture
def mock_requests_post():
    with patch('requests.post') as mock:
        yield mock

def test_chitchats_provider_initialization():
    provider = ChitChatsProvider()
    assert provider.base_url == "https://chitchats.com/api/v1"

def test_get_rates_missing_credentials():
    provider = ChitChatsProvider()
    provider.client_id = ""
    provider.access_token = ""
    
    recipient = {}
    package = {}
    
    rates = provider.get_rates(recipient, package)
    assert len(rates) == 1
    assert "error" in rates[0]
    assert "Missing Chit Chats credentials" in rates[0]["error"]

def test_get_rates_success(mock_requests_post):
    provider = ChitChatsProvider()
    provider.client_id = "test_client"
    provider.access_token = "test_token"
    
    # Mock API Response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "shipment": {
            "id": "shipment_123",
            "rates": [
                {
                    "postage_carrier": "USPS",
                    "postage_description": "First Class",
                    "postage_label_price": "5.50",
                    "estimated_delivery_date": "2023-10-25"
                },
                {
                    "postage_carrier": "FedEx",
                    "postage_description": "Ground",
                    "postage_label_price": "12.00",
                    "estimated_delivery_date": "2023-10-23"
                }
            ]
        }
    }
    mock_requests_post.return_value = mock_response
    
    recipient = {
        "name": "John Doe",
        "address_1": "123 Main St",
        "city": "New York",
        "province_code": "NY",
        "postal_code": "10001",
        "country_code": "US"
    }
    
    package = {
        "weight": 500,
        "size_x": 10,
        "size_y": 10,
        "size_z": 10,
        "description": "Candle",
        "value": 20
    }
    
    rates = provider.get_rates(recipient, package)
    
    assert len(rates) == 2
    assert rates[0]['postage_carrier'] == "USPS"
    assert rates[0]['postage_label_price'] == "5.50"
    
    # Verify API Call payload
    mock_requests_post.assert_called_once()
    args, kwargs = mock_requests_post.call_args
    assert kwargs['headers']['Authorization'] == "test_token"
    payload = kwargs['json']
    assert payload['postage_type'] == 'unknown'
    assert payload['weight'] == 500

def test_get_rates_api_failure(mock_requests_post):
    provider = ChitChatsProvider()
    provider.client_id = "test_client"
    provider.access_token = "test_token"
    
    # Mock API Failure
    mock_response = MagicMock()
    import requests
    mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("API Error")
    mock_requests_post.return_value = mock_response
    
    rates = provider.get_rates({}, {})
    
    assert len(rates) == 1
    assert "error" in rates[0]
    assert "API Request Failed" in rates[0]["error"]
