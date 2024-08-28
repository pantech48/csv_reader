"""
This module contains functions to process CSV files, including downloading,
reading, and updating the database with the CSV data.
"""

import csv
import os
import re
from typing import List, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import gdown

from utils.logger import logger
from app.models import Base, Product
from app.database import SessionLocal
from config import GOOGLE_DRIVE_URL, CSV_FILE_PATH, DATABASE_URL


engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


def extract_file_id(url: str) -> str:
    """
    Extract the file ID from a Google Drive URL.

    Args:
        url (str): The Google Drive URL.

    Returns:
        str: The extracted file ID.

    Raises:
        ValueError: If the file ID cannot be extracted from the URL.
    """
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Unable to extract file ID from URL")


def download_csv() -> None:
    """
    Download the CSV file from Google Drive using the predefined URL.

    Raises:
        Exception: If there is an error during the download process.
    """
    try:
        logger.info(f"Downloading CSV file from Google Drive")
        file_id = extract_file_id(GOOGLE_DRIVE_URL)
        output = CSV_FILE_PATH
        gdown.download(f"https://drive.google.com/uc?id={file_id}", output, quiet=False)
        logger.info(f"Successfully downloaded CSV file to {CSV_FILE_PATH}")
    except Exception as e:
        logger.exception(f"Error downloading CSV file: {e}")
        raise


def read_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Read a CSV file and return its contents as a list of dictionaries.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        List[Dict[str, str]]: A list of dictionaries representing the rows in the CSV file.
    """
    try:
        logger.info(f"Reading CSV file: {file_path}")
        with open(file_path, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
        logger.info(f"Successfully read {len(data)} rows from {file_path}")
        return data
    except Exception as e:
        logger.exception(f"Error reading CSV file {file_path}: {e}")
        return []


def update_existing_product(product: Product, row: Dict[str, str]) -> None:
    """
    Update an existing product with new data.

    Args:
        product (Product): The existing product to update.
        row (Dict[str, str]): A dictionary containing the new product data.

    Returns:
        None
    """
    for key, value in row.items():
        if key == "sku (unique id)":
            setattr(product, "sku", value)
        elif key == "producer":
            setattr(product, "producer", value if value else "")
        else:
            setattr(product, key.replace(" ", "_"), value)


def create_new_product(row: Dict[str, str]) -> Product:
    """
    Create a new product from row data.

    Args:
        row (Dict[str, str]): A dictionary containing the product data.

    Returns:
        Product: A new Product instance.
    """
    product_data = {
        key.replace(" ", "_"): value
        for key, value in row.items()
        if key != "sku (unique id)"
    }
    product_data["sku"] = row["sku (unique id)"]
    product_data["producer"] = row.get("producer", "")
    return Product(**product_data)


def process_row(db: Session, row: Dict[str, str]) -> None:
    """
    Process a single row of data.

    Args:
        db (Session): The database session.
        row (Dict[str, str]): A dictionary containing the product data.

    Returns:
        None
    """
    product = db.query(Product).filter_by(sku=row["sku (unique id)"]).first()
    if product:
        update_existing_product(product, row)
    else:
        new_product = create_new_product(row)
        db.add(new_product)


def update_database(data: List[Dict[str, str]], db: Session = None) -> None:
    """
    Update the database with the provided data.

    Args:
        data (List[Dict[str, str]]): A list of dictionaries representing the data to be updated.
        db (Session, optional): The database session. Defaults to None.

    Returns:
        None

    Raises:
        Exception: If there is an error during the database update process.
    """
    if db is None:
        db = SessionLocal()
        should_close_db = True
    else:
        should_close_db = False

    try:
        for row in data:
            process_row(db, row)
        db.commit()
        logger.info(f"Successfully updated database with {len(data)} products")
    except Exception as e:
        logger.exception(f"Error updating database: {e}")
        db.rollback()
        raise
    finally:
        if should_close_db:
            db.close()


def process_csv() -> None:
    """
    Process the CSV file by downloading it, reading its contents, and updating the database.

    Raises:
        Exception: If there is an error during the CSV processing.
    """
    try:
        download_csv()
        data = read_csv(CSV_FILE_PATH)
        if data:
            update_database(data)
        else:
            logger.warning("No data was read from the CSV file.")
    except Exception as e:
        logger.exception(f"Error processing CSV: {e}")
    finally:
        # Clean up the downloaded file
        if os.path.exists(CSV_FILE_PATH):
            os.remove(CSV_FILE_PATH)
            logger.info(f"Removed temporary CSV file: {CSV_FILE_PATH}")
