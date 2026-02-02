
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from client.api_client import APIClient

def fetch_list():
    print("Fetching product list...")
    try:
        products = APIClient.get_products()
        if not products:
            print("No products found (or empty list returned).")
        else:
            print(f"Found {len(products)} products:")
            print(json.dumps(products, indent=2))
        return True
    except Exception as e:
        print(f"Error fetching products: {e}")
        return False

if __name__ == "__main__":
    fetch_list()
