import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to allow importing if needed, or just load .env directly
BASE_DIR = Path(__file__).parent.parent
ENV_PATH = BASE_DIR / "config" / "local.env"

load_dotenv(ENV_PATH)

API_KEY = os.getenv("ETSY_API_KEY")
SHOP_NAME = "AurumCandles" # Default assumption

if not API_KEY:
    print("Error: ETSY_API_KEY not found in config/local.env")
    sys.exit(1)

def fetch_shop_id(shop_name):
    url = "https://openapi.etsy.com/v3/application/shops"
    params = {
        "shop_name": shop_name,
        "limit": 1
    }
    headers = {
        "x-api-key": API_KEY.strip()
    }
    
    print(f"Fetching Shop ID for '{shop_name}'...")
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            results = data.get('results', [])
            
            if count > 0 and results:
                shop = results[0]
                shop_id = shop.get('shop_id')
                print(f"\nSUCCESS! Found Shop: {shop.get('shop_name')}")
                print(f"Shop ID: {shop_id}")
                return shop_id
            else:
                print(f"\nNo shop found with name '{shop_name}'.")
                return None
        else:
            print(f"\nFailed to fetch shop. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def check_api_key():
    url = "https://openapi.etsy.com/v3/application/openapi-ping"
    headers = {
        "x-api-key": API_KEY.strip()
    }
    print("Checking API Key validity with ping...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("API Key is VALID.")
            return True
        else:
            print(f"API Key check failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Ping failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        SHOP_NAME = sys.argv[1]
    
    if check_api_key():
        fetch_shop_id(SHOP_NAME)

