import sys
print(f"Python version: {sys.version}")
print(f"sys.path in test_integration.py: {sys.path}")

import app
print(f"csv_reader module location: {app.__file__}")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Product
from app.csv_processor import update_database
from app.api import app, get_db
from fastapi.testclient import TestClient


@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield engine

    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def client(test_db):
    return TestClient(app)


def test_csv_processing_and_api(test_db, client):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    db = SessionLocal()

    # Test data
    test_data = [
        {
            "product_name": "Test Product",
            "photo_url": "http://example.com/test.jpg",
            "barcode": "123456789",
            "price_cents": "1999",
            "sku (unique id)": "TEST-SKU-001",
            "producer": "Test Producer",
        }
    ]

    # Process the test data
    update_database(test_data, db)

    # Test the API
    response = client.get("/products/Test Producer")
    assert response.status_code == 200

    products = response.json()
    assert len(products) == 1
    assert products[0]["product_name"] == "Test Product"
    assert products[0]["sku"] == "TEST-SKU-001"

    db.close()


def test_pagination(test_db, client):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    db = SessionLocal()

    # Add multiple products
    test_data = [
        {
            "product_name": f"Product {i}",
            "photo_url": f"http://example.com/product{i}.jpg",
            "barcode": f"12345{i}",
            "price_cents": str(1000 + i),
            "sku (unique id)": f"SKU-00{i}",
            "producer": "Pagination Producer",
        }
        for i in range(15)  # Create 15 products
    ]

    update_database(test_data, db)

    # Test first page (default 10 items)
    response = client.get("/products/Pagination Producer")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 10

    # Test second page
    response = client.get("/products/Pagination Producer?skip=10&limit=10")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 5  # Should return the remaining 5 products

    db.close()

def test_nonexistent_producer(test_db, client):
    response = client.get("/products/Nonexistent Producer")
    assert response.status_code == 404
