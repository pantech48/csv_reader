from fastapi import FastAPI, Query, HTTPException
from sqlalchemy.orm import Session
from .models import Product
from .csv_processor import engine
from typing import List
from pydantic import BaseModel

app = FastAPI()


class ProductOut(BaseModel):
    product_name: str
    photo_url: str
    barcode: str
    price_cents: int
    sku: str
    producer: str

    class Config:
        orm_mode = True


@app.get("/products/{producer}", response_model=List[ProductOut])
def get_products_by_producer(
    producer: str, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1, le=100)
):
    session = Session(bind=engine)
    try:
        products = (
            session.query(Product)
            .filter(Product.producer == producer)
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not products:
            raise HTTPException(
                status_code=404, detail="No products found for this producer"
            )
        return products
    finally:
        session.close()
