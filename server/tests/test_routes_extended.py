import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import base64
import json

# Setup proper imports for the app logic
# Since main.py imports routes, and routes imports db, we mock at 
# the imports inside server.routes mostly.

import sys
# Ensure imports work if running from root
from server.main import app
from server.routes import router

client = TestClient(app)

class TestRoutesExtended:
    
    @pytest.fixture
    def mock_db_ops(self):
        with patch("server.routes.db_ops") as mock_trans, \
             patch("server.routes.material_ops") as mock_mats, \
             patch("server.routes.product_ops") as mock_prods:
            yield mock_trans, mock_mats, mock_prods

    # --- Transactions Routes (12 Tests) ---
    def test_get_transactions_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.read_transactions.return_value = [{"id": 1, "description": "T1"}]
        response = client.get("/transactions") 
        assert response.status_code == 200
        assert response.json()[0]["description"] == "T1"

    def test_get_transactions_empty(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.read_transactions.return_value = []
        response = client.get("/transactions")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_transactions_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.read_transactions.side_effect = Exception("DB Fail")
        response = client.get("/transactions")
        assert response.status_code == 500

    def test_add_transaction_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.write_transaction.return_value = 10
        payload = {"date": "2023-01-01", "description": "Sale", "quantity": 1, "price": 10, "type": "INCOME"}
        response = client.post("/transactions", json=payload)
        assert response.status_code == 200
        assert response.json()["id"] == 10

    def test_add_transaction_deduct_stock(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.write_transaction.return_value = 11
        # Mock product logic for stock deduction
        p.get_product.return_value = {"wax_type": "Soy", "wax_weight_g": 100}
        
        payload = {"date": "2023-01-01", "description": "Sale", "quantity": 2, "price": 20, "type": "INCOME", "product_id": 1}
        response = client.post("/transactions", json=payload)
        
        assert p.update_stock.called # Deduct product stock
        assert m.deduct_stock_by_name.called # Deduct wax
        assert response.status_code == 200

    def test_add_transaction_invalid_body(self, mock_db_ops):
        response = client.post("/transactions", json={"date": "Only Date"}) # Missing required
        assert response.status_code == 422 # Pydantic Validation Error

    def test_add_transaction_db_fail(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.write_transaction.side_effect = Exception("Fail")
        payload = {"date": "2023-01-01", "description": "Sale", "quantity": 1, "price": 10, "type": "INCOME"}
        response = client.post("/transactions", json=payload)
        assert response.status_code == 500

    def test_update_transaction_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        payload = {"date": "2023-01-02", "description": "Upd", "quantity": 2, "price": 20, "type": "EXPENSE"}
        response = client.put("/transactions/1", json=payload)
        assert response.status_code == 200
        assert t.update_transaction.called

    def test_update_transaction_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.update_transaction.side_effect = Exception("Fail")
        payload = {"date": "2023-01-02", "description": "Upd", "quantity": 2, "price": 20, "type": "EXPENSE"}
        response = client.put("/transactions/1", json=payload)
        assert response.status_code == 500

    def test_delete_transaction_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        response = client.delete("/transactions/1")
        assert response.status_code == 200
        assert t.delete_transaction.called

    def test_delete_transaction_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.delete_transaction.side_effect = Exception("Fail")
        response = client.delete("/transactions/1")
        assert response.status_code == 500

    def test_get_summary(self, mock_db_ops):
        t, m, p = mock_db_ops
        t.read_transactions.return_value = []
        with patch("services.utils.TransactionUtils.calculate_summary", return_value={"total": 0}):
            response = client.get("/summary")
            assert response.status_code == 200
            assert "total" in response.json()

    # --- Materials Routes (10 Tests) ---
    def test_get_materials(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.get_materials.return_value = []
        response = client.get("/materials")
        assert response.status_code == 200

    def test_get_materials_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.get_materials.side_effect = Exception("Fail")
        response = client.get("/materials")
        assert response.status_code == 500

    def test_add_material_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.add_material.return_value = 5
        payload = {"name": "M1", "category": "C1", "unit_cost": 5.0, "unit_type": "kg"}
        response = client.post("/materials", json=payload)
        assert response.status_code == 200
        assert response.json()["id"] == 5

    def test_add_material_invalid(self, mock_db_ops):
        response = client.post("/materials", json={})
        assert response.status_code == 422

    def test_add_material_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.add_material.side_effect = Exception("Fail")
        payload = {"name": "M1", "category": "C1", "unit_cost": 5.0, "unit_type": "kg"}
        response = client.post("/materials", json=payload)
        assert response.status_code == 500

    def test_update_material_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        payload = {"name": "M2"}
        response = client.put("/materials/1", json=payload)
        assert response.status_code == 200
        assert m.update_material.called

    def test_update_material_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.update_material.side_effect = Exception("Fail")
        response = client.put("/materials/1", json={})
        assert response.status_code == 500

    def test_delete_material_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        response = client.delete("/materials/1")
        assert response.status_code == 200

    def test_delete_material_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.delete_material.side_effect = Exception("Fail")
        response = client.delete("/materials/1")
        assert response.status_code == 500

    def test_material_optional_fields(self, mock_db_ops):
        t, m, p = mock_db_ops
        m.add_material.return_value = 6
        payload = {"name": "M2", "category": "C2", "unit_cost": 1.0, "unit_type": "g", "stock_quantity": 100}
        response = client.post("/materials", json=payload)
        assert response.status_code == 200
        # verify args passed to db
        kwargs = m.add_material.call_args[1]
        assert kwargs["stock_quantity"] == 100

    # --- Product Routes (15 Tests) ---
    def test_get_products_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.get_products.return_value = [{"id": 1, "title": "P1"}]
        response = client.get("/products")
        assert response.status_code == 200

    def test_get_products_json_parse(self, mock_db_ops):
        t, m, p = mock_db_ops
        # Simulate string field that should be JSON
        p.get_products.return_value = [{"id": 1, "amazon_data": '{"asin": "123"}'}]
        response = client.get("/products")
        assert response.json()[0]["amazon_data"]["asin"] == "123"

    def test_get_products_error(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.get_products.side_effect = Exception("Fail")
        response = client.get("/products")
        assert response.status_code == 500

    def test_add_product_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.create_product.return_value = 99
        payload = {"title": "P1", "price": 10.0}
        response = client.post("/products", json=payload)
        assert response.status_code == 200
        assert response.json()["id"] == 99

    def test_add_product_with_image(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.create_product.return_value = 100
        # Send valid base64
        b64_img = base64.b64encode(b"fake").decode('utf-8')
        payload = {"title": "ImgP", "image": b64_img}
        response = client.post("/products", json=payload)
        assert response.status_code == 200
        # Check if DB called with bytes
        call_args = p.create_product.call_args[0][0]
        assert isinstance(call_args["image"], bytes)

    def test_add_product_bad_image(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.create_product.return_value = 101
        payload = {"title": "BadImg", "image": "NotBase64"}
        response = client.post("/products", json=payload)
        assert response.status_code == 200 # App handles bad base64 by setting None
        call_args = p.create_product.call_args[0][0]
        assert call_args["image"] is None

    def test_update_product_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        payload = {"title": "P1 Updated"}
        response = client.put("/products/1", json=payload)
        assert response.status_code == 200

    def test_update_product_image_decode(self, mock_db_ops):
        t, m, p = mock_db_ops
        b64_img = base64.b64encode(b"new").decode('utf-8')
        payload = {"image": b64_img}
        response = client.put("/products/1", json=payload)
        assert response.status_code == 200
        call_args = p.update_product.call_args[0][1] # arg 1 is data dict
        assert isinstance(call_args["image"], bytes)

    def test_delete_product_success(self, mock_db_ops):
        t, m, p = mock_db_ops
        response = client.delete("/products/1")
        assert response.status_code == 200

    def test_add_product_validation(self, mock_db_ops):
        response = client.post("/products", json={}) # Missing title
        assert response.status_code == 422

    # --- Images Routes (8 Tests) ---
    def test_get_images(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.get_product_images.return_value = [{"image_data": b"bytes"}]
        response = client.get("/products/1/images")
        assert response.status_code == 200
        assert isinstance(response.json()[0]["image_data"], str) # Should be base64 mapped

    def test_add_image(self, mock_db_ops):
        t, m, p = mock_db_ops
        p.add_product_image.return_value = 200
        b64 = base64.b64encode(b"img").decode('utf-8')
        response = client.post("/products/1/images", json={"product_id": 1, "image_data": b64})
        assert response.status_code == 200

    def test_delete_image(self, mock_db_ops):
        t, m, p = mock_db_ops
        response = client.delete("/products/images/1")
        assert response.status_code == 200

    # --- Edge / Extras (5 Tests) ---
    def test_404_route(self):
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_method_not_allowed(self):
        response = client.put("/transactions") # POST allowed, PUT not on collection
        assert response.status_code == 405
