from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from db import transactions as db_ops
from services.utils import TransactionUtils
from config.config import TABLE_NAME

import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic Models for Validation
class TransactionCreate(BaseModel):
    date: str
    description: str
    quantity: int
    price: float
    type: str
    supplier: Optional[str] = ""

class TransactionUpdate(BaseModel):
    date: str
    description: str
    quantity: int
    price: float
    type: str
    supplier: Optional[str] = ""

@router.get("/transactions")
def get_transactions():
    """Get all transactions"""
    try:
        data = db_ops.read_transactions(table=TABLE_NAME)
        return data
    except Exception as e:
        logger.error(f"Error getting transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transactions")
def add_transaction(item: TransactionCreate):
    """Add a new transaction"""
    try:
        # Map Pydantic model to DB function args
        new_id = db_ops.write_transaction(
            transaction_date=item.date,
            description=item.description,
            quantity=item.quantity,
            price=item.price,
            transaction_type=item.type,
            supplier=item.supplier,
            table=TABLE_NAME
        )
        return {"id": new_id, "message": "Transaction added"}
    except ValueError as ve:
         raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error adding transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/transactions/{t_id}")
def update_transaction(t_id: int, item: TransactionUpdate):
    """Update an existing transaction"""
    try:
        db_ops.update_transaction(
            transaction_id=t_id,
            transaction_date=item.date,
            description=item.description,
            quantity=item.quantity,
            price=item.price,
            transaction_type=item.type,
            supplier=item.supplier,
            table=TABLE_NAME
        )
        return {"message": "Transaction updated"}
    except Exception as e:
        logger.error(f"Error updating transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/transactions/{t_id}")
def delete_transaction(t_id: int):
    """Delete a transaction"""
    try:
        db_ops.delete_transaction(transaction_id=t_id, table=TABLE_NAME)
        return {"message": "Transaction deleted"}
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
def get_summary():
    """Get calculated summary stats"""
    try:
        # Reuse existing logic: Read all -> Calculate in Python
        # In a larger app, this calculation should move to SQL aggregation
        data = db_ops.read_transactions(table=TABLE_NAME)
        summary = TransactionUtils.calculate_summary(data)
        return summary
    except Exception as e:
        logger.error(f"Error getting summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- Materials Routes ---
from db import materials as material_ops
from config.config import MATERIALS_TABLE

class MaterialCreate(BaseModel):
    name: str
    category: str
    stock_quantity: Optional[float] = 0.0
    unit_cost: float
    unit_type: str

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    stock_quantity: Optional[float] = None
    unit_cost: Optional[float] = None
    unit_type: Optional[str] = None

@router.get("/materials")
def get_materials():
    try:
        return material_ops.get_materials(table=MATERIALS_TABLE)
    except Exception as e:
        logger.error(f"Error getting materials: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/materials")
def add_material(item: MaterialCreate):
    try:
        new_id = material_ops.add_material(
            name=item.name,
            category=item.category,
            stock_quantity=item.stock_quantity,
            unit_cost=item.unit_cost,
            unit_type=item.unit_type,
            table=MATERIALS_TABLE
        )
        return {"id": new_id, "message": "Material added"}
    except Exception as e:
        logger.error(f"Error adding material: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/materials/{m_id}")
def update_material(m_id: int, item: MaterialUpdate):
    try:
        material_ops.update_material(
            material_id=m_id,
            name=item.name,
            category=item.category,
            stock_quantity=item.stock_quantity,
            unit_cost=item.unit_cost,
            unit_type=item.unit_type,
            table=MATERIALS_TABLE
        )
        return {"message": "Material updated"}
    except Exception as e:
        logger.error(f"Error updating material: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/materials/{m_id}")
def delete_material(m_id: int):
    try:
        material_ops.delete_material(m_id, table=MATERIALS_TABLE)
        return {"message": "Material deleted"}
    except Exception as e:
        logger.error(f"Error deleting material: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# --- Product Routes ---
from db import products as product_ops
from config.config import PRODUCTS_TABLE_NAME
import base64

class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    upc: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = 0
    weight_g: Optional[float] = 0.0
    length_cm: Optional[float] = 0.0
    width_cm: Optional[float] = 0.0
    height_cm: Optional[float] = 0.0
    wax_type: Optional[str] = None
    wax_weight_g: Optional[float] = 0.0
    fragrance_weight_g: Optional[float] = 0.0
    wick_type: Optional[str] = None
    container_type: Optional[str] = None
    container_details: Optional[str] = None
    box_price: Optional[float] = 0.0
    wrap_price: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0
    image: Optional[str] = None # Base64 string

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    upc: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = None
    weight_g: Optional[float] = None
    length_cm: Optional[float] = None
    width_cm: Optional[float] = None
    height_cm: Optional[float] = None
    wax_type: Optional[str] = None
    wax_weight_g: Optional[float] = None
    fragrance_weight_g: Optional[float] = None
    wick_type: Optional[str] = None
    container_type: Optional[str] = None
    container_details: Optional[str] = None
    box_price: Optional[float] = None
    wrap_price: Optional[float] = None
    total_cost: Optional[float] = None
    image: Optional[str] = None

@router.get("/products")
def get_products():
    try:
        products = product_ops.get_products(table=PRODUCTS_TABLE_NAME)
        # Convert BLOB bytes to Base64 string for JSON response
        for p in products:
            if p.get('image'):
                if isinstance(p['image'], bytes):
                    p['image'] = base64.b64encode(p['image']).decode('utf-8')
        return products
    except Exception as e:
        logger.error(f"Error getting products: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products")
def add_product(item: ProductCreate):
    try:
        data = item.model_dump()
        # Decode Base64 image to bytes
        if data.get('image'):
            try:
                data['image'] = base64.b64decode(data['image'])
            except Exception:
                 data['image'] = None # Handle bad base64
        
        product_ops.create_product(data, table=PRODUCTS_TABLE_NAME)
        return {"message": "Product added"}
    except Exception as e:
        logger.error(f"Error adding product: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{p_id}")
def update_product(p_id: int, item: ProductUpdate):
    try:
        data = item.model_dump(exclude_unset=True)
        if data.get('image'):
             try:
                data['image'] = base64.b64decode(data['image'])
             except Exception:
                 data['image'] = None

        product_ops.update_product(p_id, data, table=PRODUCTS_TABLE_NAME)
        return {"message": "Product updated"}
    except Exception as e:
        logger.error(f"Error updating product: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/{p_id}")
def delete_product(p_id: int):
    try:
        product_ops.delete_product(p_id, table=PRODUCTS_TABLE_NAME)
        return {"message": "Product deleted"}
    except Exception as e:
        logger.error(f"Error deleting product: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
