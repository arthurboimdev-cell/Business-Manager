
import pytest
from fastapi.testclient import TestClient
from server.main import app
from db.init_db import init_db
from config.config import PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA
from db.db_connection import get_db_connection
import base64

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Setup
    conn = get_db_connection()
    cursor = conn.cursor()
    # Drop in correct order (child first)
    cursor.execute("DROP TABLE IF EXISTS product_images")
    cursor.execute(f"DROP TABLE IF EXISTS {PRODUCTS_TABLE_NAME}")
    conn.commit()
    cursor.close()
    conn.close()

    # Setup
    # Init Tables
    from config.config import PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA
    init_db(PRODUCTS_TABLE_NAME, PRODUCTS_SCHEMA)
    init_db(PRODUCT_IMAGES_TABLE, PRODUCT_IMAGES_SCHEMA)
    
    yield
    
    # Teardown
    # conn = get_db_connection()
    # cursor = conn.cursor()
    # cursor.execute(f"TRUNCATE TABLE {PRODUCTS_TABLE_NAME}")
    # conn.commit()
    # cursor.close()
    # conn.close()

def test_add_product():
    product_data = {
        "title": "Test Candle",
        "sku": "SKU-123",
        "upc": "UPC-456",
        "description": "A test candle",
        "weight_g": 100.0,
        "length_cm": 10.0,
        "width_cm": 10.0,
        "height_cm": 10.0,
        "wax_type": "Soy",
        "wax_weight_g": 80.0,
        "wick_type": "Cotton",
        "container_type": "Glass",
        "container_details": "Clear",
        "box_price": 1.5,
        "wrap_price": 0.5,
        "business_card_cost": 0.10,
        "image": None
    }
    
    response = client.post("/products", json=product_data)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["message"] == "Product added"

def test_get_products():
    response = client.get("/products")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    assert products[0]["title"] == "Test Candle"
    assert products[0]["sku"] == "SKU-123"
    assert products[0]["upc"] == "UPC-456"

def test_add_product_with_image():
    # Create a dummy small image bytes
    # Valid 1x1 GIF bytes
    dummy_bytes = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    b64_str = base64.b64encode(dummy_bytes).decode('utf-8')
    
    product_data = {
        "title": "Image Candle",
        "image": b64_str
    }
    
    response = client.post("/products", json=product_data)
    assert response.status_code == 200
    
    # Verify retrieval
    response = client.get("/products")
    products = response.json()
    # Find the image candle
    found = next((p for p in products if p["title"] == "Image Candle"), None)
    assert found is not None
    assert found["image"] == b64_str

def test_delete_product():
    # First get all to find an ID
    response = client.get("/products")
    products = response.json()
    assert len(products) > 0
    p_id = products[0]["id"]
    
    response = client.delete(f"/products/{p_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Product deleted"}
    
    # Verify it's gone
    response = client.get("/products")
    new_products = response.json()
    assert len(new_products) == len(products) - 1
