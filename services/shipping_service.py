import abc
import requests
import json
from typing import Dict, Any, List, Optional
from config.config import CHIT_CHATS_CLIENT_ID, CHIT_CHATS_ACCESS_TOKEN, CHIT_CHATS_API_URL

class ShippingProvider(abc.ABC):
    @abc.abstractmethod
    def get_rates(self, recipient: Dict[str, Any], package: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get shipping rates for a package.
        
        :param recipient: Dict containing 'name', 'address_1', 'city', 'province_code', 'postal_code', 'country_code'
        :param package: Dict containing 'weight' (g), 'size_x', 'size_y', 'size_z' (cm), 'description', 'value'
        :return: List of rate dictionaries
        """
        pass

class ChitChatsProvider(ShippingProvider):
    def __init__(self):
        self.client_id = CHIT_CHATS_CLIENT_ID
        self.access_token = CHIT_CHATS_ACCESS_TOKEN
        self.base_url = CHIT_CHATS_API_URL

    def get_rates(self, recipient: Dict[str, Any], package: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.client_id or not self.access_token:
            return [{"error": "Missing Chit Chats credentials. Please configure client_id and access_token."}]
            
        url = f"{self.base_url}/clients/{self.client_id}/shipments"
        
        # Construct payload required by Chit Chats API
        # Postage type 'unknown' is required to get rates
        payload = {
            "name": recipient.get("name"),
            "address_1": recipient.get("address_1"),
            "city": recipient.get("city"),
            "province_code": recipient.get("province_code"),
            "postal_code": recipient.get("postal_code"),
            "country_code": recipient.get("country_code"),
            "package_type": "parcel", # Defaulting to parcel
            "size_unit": "cm",
            "size_x": package.get("size_x", 0),
            "size_y": package.get("size_y", 0),
            "size_z": package.get("size_z", 0),
            "weight_unit": "g",
            "weight": package.get("weight", 0),
            "value_currency": "usd", # Configurable? Defaulting to USD for compatibility
            "value": package.get("value", 0),
            "description": package.get("description", "Merchandise"),
            "ship_date": "today",
            "postage_type": "unknown",
            "line_items": [
                {
                    "quantity": 1,
                    "description": package.get("description", "Merchandise"),
                    "value_amount": package.get("value", 0),
                    "currency_code": "USD",
                    "origin_country": "CA",
                    "hs_tariff_code": "3406000000"
                }
            ] 
        }

        headers = {
            "Authorization": self.access_token,
            "Content-Type": "application/json"
        }
        
        try:
            # We assume creates a shipment to get rates? usually 'unknown' postage type returns rates in response
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Parse rates from response
            # Response usually contains 'shipment': { 'rates': [...] } if created with unknown postage
            shipment = data.get("shipment", {})
            rates = shipment.get("rates", [])
            
            return rates
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request Failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse Body: {e.response.text}"
            return [{"error": error_msg}]
