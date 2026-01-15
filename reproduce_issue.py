import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from db.products import create_product, delete_product
from db.db_connection import get_db_connection

def test_valid_product_creation():
    print("Testing VALID product creation...")
    
    # Valid data matching schema and form logic
    product_data = {
        "title": "Final Verification Product",
        "description": "Output of fixed logic",
        "stock_quantity": 5,
        "weight_g": 200.5,
        "length_cm": 10.0,
        "width_cm": 10.0,
        "height_cm": 10.0,
        "wax_type": "Soy", 
        "wax_weight_g": 150.0,
        "fragrance_type": "Lavender", # The new field
        "container_type": "Glass Jar",
        "selling_price": 25.00,
        "labor_time": 10,
        "labor_rate": 15.00,
        "common_data": {"test": "json"},
        "wax_rate": 0.05, # Valid float, not empty string
    }
    
    new_id = None
    try:
        new_id = create_product(product_data)
        print(f"Result ID: {new_id}")
        
        if new_id:
            print("SUCCESS: Product created successfully.")
            # Verify data integrity
            conn = get_db_connection()
            c = conn.cursor(dictionary=True)
            c.execute(f"SELECT * FROM products_test WHERE id ={new_id}") # Default to test table in dev
            row = c.fetchone()
            print(f"Verified DB Row Fragrance Type: {row.get('fragrance_type')}")
            c.close()
            conn.close()
            
            # Cleanup
            delete_product(new_id)
            print("Cleanup: Product newly created deleted.")
            
        else:
            print("FAILURE: No ID returned.")
            
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    test_valid_product_creation()
