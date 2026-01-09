from fastapi.testclient import TestClient
from server.routes import router
from fastapi import FastAPI
from unittest.mock import patch, MagicMock
from db import materials
from config.config import MATERIALS_TABLE

app = FastAPI()
app.include_router(router)
client = TestClient(app)

def test_get_materials():
    mock_data = [{'id': 1, 'name': 'Wax 464', 'category': 'wax', 'unit_cost': 0.01, 'unit_type': 'g'}]
    with patch('db.materials.get_materials', return_value=mock_data) as mock_get:
        response = client.get("/materials")
        assert response.status_code == 200
        assert response.json() == mock_data
        mock_get.assert_called_with(table=MATERIALS_TABLE)

def test_add_material():
    item = {"name": "Test Wick", "category": "wick", "unit_cost": 0.10, "unit_type": "unit"}
    with patch('db.materials.add_material', return_value=123) as mock_add:
        response = client.post("/materials", json=item)
        assert response.status_code == 200
        assert response.json() == {"id": 123, "message": "Material added"}
        
        mock_add.assert_called_with(
            name="Test Wick",
            category="wick",
            stock_quantity=0.0,
            unit_cost=0.10,
            unit_type="unit",
            table=MATERIALS_TABLE
        )

def test_update_material():
    item = {"unit_cost": 0.15}
    with patch('db.materials.update_material') as mock_update:
        response = client.put("/materials/1", json=item)
        assert response.status_code == 200
        assert response.json() == {"message": "Material updated"}
        
        # Check that update called with correct args
        mock_update.assert_called()
        args = mock_update.call_args[1]
        assert args['material_id'] == 1
        assert args['unit_cost'] == 0.15
        assert args['table'] == MATERIALS_TABLE

def test_delete_material():
    with patch('db.materials.delete_material') as mock_delete:
        response = client.delete("/materials/1")
        assert response.status_code == 200
        assert response.json() == {"message": "Material deleted"}
        mock_delete.assert_called_with(1, table=MATERIALS_TABLE)
