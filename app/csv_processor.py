import csv
import os
import re
from typing import List, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import gdown

from utils.logger import logger
from app.models import Base, Product
from app.database import SessionLocal

engine = create_engine("sqlite:///products.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

GOOGLE_DRIVE_URL = (
    "https://drive.google.com/file/d/1X9ze_7q1oVjDia4trRnd9ZZkq5P2ymhY/view"
)
CSV_FILE_PATH = "catalog.csv"


def extract_file_id(url: str) -> str:
    """Extract the file ID from a Google Drive URL."""
    match = re.search(r"/file/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    raise ValueError("Unable to extract file ID from URL")


def download_csv():
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


def update_database(data: List[Dict[str, str]], db: Session = None):
    if db is None:
        db = SessionLocal()
    try:
        for row in data:
            product = db.query(Product).filter_by(sku=row['sku (unique id)']).first()
            if product:
                # Update existing product
                for key, value in row.items():
                    if key == 'sku (unique id)':
                        setattr(product, 'sku', value)
                    elif key == 'producer':
                        setattr(product, 'producer', value if value else '')
                    else:
                        setattr(product, key.replace(' ', '_'), value)
            else:
                # Create new product
                product_data = {key.replace(' ', '_'): value for key, value in row.items() if key != 'sku (unique id)'}
                product_data['sku'] = row['sku (unique id)']
                product_data['producer'] = row.get('producer', '')  # Set empty string if producer is missing
                product = Product(**product_data)
                db.add(product)
        db.commit()
        logger.info(f"Successfully updated database with {len(data)} products")
    except Exception as e:
        logger.exception(f"Error updating database: {e}")
        db.rollback()
        raise
    finally:
        if db != SessionLocal():
            db.close()

def process_csv():
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
