import unittest
from unittest.mock import patch, mock_open, MagicMock
from app.csv_processor import (
    extract_file_id,
    read_csv,
    update_database,
    update_existing_product,
    create_new_product,
    process_row,
)
from app.models import Product


class TestCSVProcessor(unittest.TestCase):

    def test_extract_file_id(self):
        url = "https://drive.google.com/file/d/1X9ze_7q1oVjDia4trRnd9ZZkq5P2ymhY/view"
        expected_id = "1X9ze_7q1oVjDia4trRnd9ZZkq5P2ymhY"
        self.assertEqual(extract_file_id(url), expected_id)

    def test_extract_file_id_invalid_url(self):
        url = "https://invalid-url.com"
        with self.assertRaises(ValueError):
            extract_file_id(url)

    @patch(
        "app.csv_processor.open",
        new_callable=mock_open,
        read_data="product_name,photo_url,barcode,price_cents,sku (unique id),producer\nProduct1,http://example.com,123,1000,SKU1,Producer1\n",
    )
    def test_read_csv(self, mock_file):
        data = read_csv("dummy.csv")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["product_name"], "Product1")
        self.assertEqual(data[0]["sku (unique id)"], "SKU1")

    def test_update_existing_product(self):
        product = Product(
            product_name="Old Name",
            photo_url="http://old.com",
            barcode="old",
            price_cents=500,
            sku="SKU1",
            producer="Old Producer",
        )
        row = {
            "product_name": "New Name",
            "photo_url": "http://new.com",
            "barcode": "new",
            "price_cents": "1000",
            "sku (unique id)": "SKU1",
            "producer": "New Producer",
        }
        update_existing_product(product, row)
        self.assertEqual(product.product_name, "New Name")
        self.assertEqual(product.photo_url, "http://new.com")
        self.assertEqual(product.barcode, "new")
        self.assertEqual(product.price_cents, "1000")
        self.assertEqual(product.sku, "SKU1")
        self.assertEqual(product.producer, "New Producer")

    def test_create_new_product(self):
        row = {
            "product_name": "New Product",
            "photo_url": "http://example.com",
            "barcode": "123",
            "price_cents": "1000",
            "sku (unique id)": "SKU2",
            "producer": "New Producer",
        }
        product = create_new_product(row)
        self.assertEqual(product.product_name, "New Product")
        self.assertEqual(product.photo_url, "http://example.com")
        self.assertEqual(product.barcode, "123")
        self.assertEqual(product.price_cents, "1000")
        self.assertEqual(product.sku, "SKU2")
        self.assertEqual(product.producer, "New Producer")

    @patch("app.csv_processor.update_existing_product")
    @patch("app.csv_processor.create_new_product")
    def test_process_row_existing_product(self, mock_create, mock_update):
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = (
            MagicMock()
        )
        row = {"sku (unique id)": "SKU1"}
        process_row(mock_db, row)
        mock_update.assert_called_once()
        mock_create.assert_not_called()

    @patch("app.csv_processor.update_existing_product")
    @patch("app.csv_processor.create_new_product")
    def test_process_row_new_product(self, mock_create, mock_update):
        mock_db = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        row = {"sku (unique id)": "SKU1"}
        process_row(mock_db, row)
        mock_create.assert_called_once()
        mock_update.assert_not_called()
        mock_db.add.assert_called_once()

    @patch("app.csv_processor.process_row")
    @patch("app.csv_processor.SessionLocal")
    def test_update_database(self, mock_session_local, mock_process_row):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        data = [{"sku (unique id)": "SKU1"}, {"sku (unique id)": "SKU2"}]
        update_database(data)
        self.assertEqual(mock_process_row.call_count, 2)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.csv_processor.process_row")
    @patch("app.csv_processor.SessionLocal")
    def test_update_database_exception(self, mock_session_local, mock_process_row):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_process_row.side_effect = Exception("Test exception")
        data = [{"sku (unique id)": "SKU1"}]
        with self.assertRaises(Exception):
            update_database(data)
        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("app.csv_processor.process_row")
    def test_update_database_with_existing_session(self, mock_process_row):
        mock_db = MagicMock()
        data = [{"sku (unique id)": "SKU1"}]
        update_database(data, db=mock_db)
        mock_process_row.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_not_called()


if __name__ == "__main__":
    unittest.main()
