
import sys
import requests
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.config import SERVER_URL

def check_connection():
    print(f"Checking connection to {SERVER_URL}...")
    try:
        response = requests.get(SERVER_URL)
        if response.status_code == 200:
            print("Successfully connected to API!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"Connected, but received status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("Connection failed: Server is likely not running.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    if check_connection():
        sys.exit(0)
    else:
        sys.exit(1)
