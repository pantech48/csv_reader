from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Product
from app.database import get_db
from typing import List, Optional
from pydantic import BaseModel

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
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    query = db.query(Product)

    if producer is not None:
        query = query.filter(or_(Product.producer == producer, Product.producer == ''))
    else:
        query = query.filter(Product.producer == '')

    products = query.offset(skip).limit(limit).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    return products
