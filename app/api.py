"""
This module contains functions to process CSV files, including downloading,
reading, and updating the database with the CSV data.
"""

from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Product
from app.database import get_db
from typing import List, Optional
from pydantic import BaseModel
import config

app = FastAPI()


class ProductOut(BaseModel):
    product_name: str
    photo_url: str
    barcode: str
    price_cents: int
    sku: str
    producer: Optional[str]

    class Config:
        from_attributes = True


@app.get("/products/", response_model=List[ProductOut])
def get_products(
    producer: Optional[str] = None,
    skip: int = Query(config.DEFAULT_SKIP, ge=0),
    limit: int = Query(config.DEFAULT_LIMIT, ge=1, le=config.MAX_LIMIT),
    db: Session = Depends(get_db),
):
    """Get a list of products based on the producer."""
    query = db.query(Product)

    if producer is not None:
        query = query.filter(or_(Product.producer == producer, Product.producer == ""))
    else:
        query = query.filter(Product.producer == "")

    products = query.offset(skip).limit(limit).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products
