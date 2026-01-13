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
    def add_transaction(date, desc, qty, price, t_type, supplier=None, product_id=None):
        payload = {
            "date": date,
            "description": desc,
            "quantity": qty,
            "price": price,
            "type": t_type,
            "supplier": supplier,
            "product_id": product_id
        }
        try:
            response = requests.post(f"{APIClient.BASE_URL}/transactions", json=payload)
            response.raise_for_status()
            return response.json().get("id")
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def update_transaction(t_id, date, desc, qty, price, t_type, supplier=None, product_id=None):
        payload = {
            "date": date,
            "description": desc,
            "quantity": qty,
            "price": price,
            "type": t_type,
            "supplier": supplier,
            "product_id": product_id
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

    # --- Product Methods ---
    @staticmethod
    def get_products():
        try:
            response = requests.get(f"{APIClient.BASE_URL}/products")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []

    @staticmethod
    def add_product(product_data):
        import base64
        # Handle Byte Image -> Base64 String
        if product_data.get('image') and isinstance(product_data['image'], bytes):
            product_data['image'] = base64.b64encode(product_data['image']).decode('utf-8')
            
        try:
            response = requests.post(f"{APIClient.BASE_URL}/products", json=product_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def update_product(p_id, product_data):
        import base64
        # Handle Byte Image -> Base64 String
        if product_data.get('image') and isinstance(product_data['image'], bytes):
            product_data['image'] = base64.b64encode(product_data['image']).decode('utf-8')

        try:
            response = requests.put(f"{APIClient.BASE_URL}/products/{p_id}", json=product_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def delete_product(p_id):
        try:
            response = requests.delete(f"{APIClient.BASE_URL}/products/{p_id}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    # --- Materials Methods ---
    @staticmethod
    def get_materials():
        try:
            response = requests.get(f"{APIClient.BASE_URL}/materials")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []

    @staticmethod
    def add_material(data):
        try:
            response = requests.post(f"{APIClient.BASE_URL}/materials", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def update_material(m_id, data):
        try:
            response = requests.put(f"{APIClient.BASE_URL}/materials/{m_id}", json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def delete_material(m_id):
        try:
            response = requests.delete(f"{APIClient.BASE_URL}/materials/{m_id}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e
            raise e

    # --- Image Methods ---
    @staticmethod
    def get_product_images(p_id):
        try:
            response = requests.get(f"{APIClient.BASE_URL}/products/{p_id}/images")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []

    @staticmethod
    def add_product_image(p_id, image_bytes):
        import base64
        # Convert bytes to base64 string
        if isinstance(image_bytes, bytes):
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        else:
            image_b64 = image_bytes # Assume it's already b64 or fail server-side
            
        payload = {
            "product_id": p_id,
            "image_data": image_b64,
            "display_order": 0
        }
        try:
            response = requests.post(f"{APIClient.BASE_URL}/products/{p_id}/images", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e

    @staticmethod
    def delete_product_image(img_id):
        try:
            response = requests.delete(f"{APIClient.BASE_URL}/products/images/{img_id}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            raise e
