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
