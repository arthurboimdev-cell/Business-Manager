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
    product_id: Optional[int] = None

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
            product_id=item.product_id,
            table=TABLE_NAME
        )
        
        # Link to Inventory: Deduct Stock
        if item.product_id:
             # If income (sale), deduct stock. 
             # logic: quantity sold = deduction
             # If expense (restock?), maybe add? Default assumption: Income = Sale.
             # User Request: "When adding a 'Income' transaction... Deduct Stock"
             if item.type.lower() == 'income':
                 product_ops.update_stock(item.product_id, -item.quantity, table=PRODUCTS_TABLE_NAME)
                 
                 # FEATURE: Material Deduction
                 # Fetch product details to know what to deduct
                 product = product_ops.get_product(item.product_id, table=PRODUCTS_TABLE_NAME)
                 if product:
                     # 1. Wax
                     if product.get('wax_type') and product.get('wax_weight_g'):
                         total_wax = float(product['wax_weight_g']) * item.quantity
                         material_ops.deduct_stock_by_name(product['wax_type'], total_wax, table=MATERIALS_TABLE)
                         
                     # 2. Wick
                     if product.get('wick_type'):
                         total_wick = 1.0 * item.quantity # Assuming 1 wick per unit
                         material_ops.deduct_stock_by_name(product['wick_type'], total_wick, table=MATERIALS_TABLE)
                         
                     # 3. Container
                     if product.get('container_type'):
                         total_container = 1.0 * item.quantity 
                         material_ops.deduct_stock_by_name(product['container_type'], total_container, table=MATERIALS_TABLE)
                         
                     # 4. Fragrance (Optional, if we had connection. Schema implies fragrance_weight_g exists but no Type field yet)
                     pass

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
    title: str
    sku: Optional[str] = None
    upc: Optional[str] = None
    description: Optional[str] = None
    stock_quantity: Optional[int] = 0
    weight_g: Optional[float] = 0.0
    length_cm: Optional[float] = 0.0
    width_cm: Optional[float] = 0.0
    height_cm: Optional[float] = 0.0
    wax_type: Optional[str] = None
    wax_rate: Optional[float] = 0.0
    fragrance_type: Optional[str] = None
    fragrance_weight_g: Optional[float] = 0.0
    fragrance_rate: Optional[float] = 0.0
    wick_type: Optional[str] = None
    wick_rate: Optional[float] = 0.0
    wick_quantity: Optional[int] = 1
    container_type: Optional[str] = None
    container_rate: Optional[float] = 0.0
    container_quantity: Optional[int] = 1
    container_details: Optional[str] = None
    box_type: Optional[str] = None
    box_price: Optional[float] = 0.0
    box_quantity: Optional[int] = 1
    wrap_price: Optional[float] = 0.0
    business_card_cost: Optional[float] = 0.0
    labor_time: Optional[int] = 0
    labor_rate: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0
    selling_price: Optional[float] = 0.0
    amazon_data: Optional[dict] = None
    etsy_data: Optional[dict] = None
    common_data: Optional[dict] = None
    image: Optional[str] = None # Base64 string

class ProductUpdate(BaseModel):
    title: Optional[str] = None
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
    wax_rate: Optional[float] = None
    fragrance_type: Optional[str] = None
    fragrance_weight_g: Optional[float] = None
    fragrance_rate: Optional[float] = None
    wick_type: Optional[str] = None
    wick_rate: Optional[float] = None
    wick_quantity: Optional[int] = None
    container_type: Optional[str] = None
    container_rate: Optional[float] = None
    container_quantity: Optional[int] = None
    container_details: Optional[str] = None
    box_type: Optional[str] = None
    box_price: Optional[float] = None
    box_quantity: Optional[int] = None
    wrap_price: Optional[float] = None
    business_card_cost: Optional[float] = None
    labor_time: Optional[int] = None
    labor_rate: Optional[float] = None
    total_cost: Optional[float] = None
    selling_price: Optional[float] = None
    amazon_data: Optional[dict] = None
    etsy_data: Optional[dict] = None
    common_data: Optional[dict] = None
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
            # JSON fields are likely returned as strings/dicts depending on DB driver
            # MySQL connector might return string or dict if using JSON column
            # Ensure they are proper JSON
            import json
            for key in ['amazon_data', 'etsy_data', 'common_data']:
                if p.get(key) and isinstance(p[key], str):
                    try:
                        p[key] = json.loads(p[key])
                    except: pass
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
        
        new_id = product_ops.create_product(data, table=PRODUCTS_TABLE_NAME)
        return {"id": new_id, "message": "Product added"}
    except Exception as e:
        logger.error(f"Error adding product: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/products/{p_id}")
def update_product(p_id: int, item: ProductUpdate):
    try:
        data = item.model_dump(exclude_unset=True)
        print(f"DEBUG: update_product received keys: {data.keys()}")
        if data.get('image'):
             print(f"DEBUG: update_product has image data length: {len(data['image'])}")
             try:
                data['image'] = base64.b64decode(data['image'])
                print(f"DEBUG: decoded image length: {len(data['image'])}")
             except Exception as e:
                 print(f"DEBUG: Image decode failed: {e}")
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

# --- Product Images Routes ---
class ImageCreate(BaseModel):
    product_id: int
    image_data: str # Base64
    display_order: Optional[int] = 0

@router.get("/products/{p_id}/images")
def get_product_images(p_id: int):
    try:
        images = product_ops.get_product_images(p_id)
        # Convert BLOB to Base64
        for img in images:
            if img.get('image_data'):
                img['image_data'] = base64.b64encode(img['image_data']).decode('utf-8')
        return images
    except Exception as e:
        logger.error(f"Error getting images: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/products/{p_id}/images")
def add_product_image(p_id: int, item: ImageCreate):
    try:
        data = base64.b64decode(item.image_data)
        new_id = product_ops.add_product_image(p_id, data, item.display_order)
        return {"id": new_id, "message": "Image added"}
    except Exception as e:
        logger.error(f"Error adding image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/products/images/{img_id}")
def delete_product_image(img_id: int):
    try:
         product_ops.delete_product_image(img_id)
         return {"message": "Image deleted"}
    except Exception as e:
        logger.error(f"Error deleting image: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
