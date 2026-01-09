import requests
from config.config import TABLE_NAME, SERVER_URL

class APIClient:
    BASE_URL = SERVER_URL

    @staticmethod
    def get_all_transactions():
        try:
            response = requests.get(f"{APIClient.BASE_URL}/transactions")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []

    @staticmethod
    def add_transaction(date, desc, qty, price, t_type, supplier=None):
        payload = {
            "date": date,
            "description": desc,
            "quantity": qty,
            "price": price,
            "type": t_type,
            "supplier": supplier
        }
        try:
            response = requests.post(f"{APIClient.BASE_URL}/transactions", json=payload)
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def update_transaction(t_id, date, desc, qty, price, t_type, supplier=None):
        payload = {
            "date": date,
            "description": desc,
            "quantity": qty,
            "price": price,
            "type": t_type,
            "supplier": supplier
        }
        try:
            response = requests.put(f"{APIClient.BASE_URL}/transactions/{t_id}", json=payload)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def delete_transaction(t_id):
        try:
            response = requests.delete(f"{APIClient.BASE_URL}/transactions/{t_id}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e
