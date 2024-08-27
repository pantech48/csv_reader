from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    product_name = Column(String)
    photo_url = Column(String)
    barcode = Column(String)
    price_cents = Column(Integer)
    sku = Column(String, unique=True)
    producer = Column(String)
