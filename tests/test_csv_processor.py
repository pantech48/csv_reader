import unittest
from unittest.mock import patch, mock_open, MagicMock
from csv_reader.csv_processor import extract_file_id, read_csv, update_database
from csv_reader.models import Product

class TestCSVProcessor(unittest.TestCase):

    def test_extract_file_id(self):
        url = "https://drive.google.com/file/d/1X9ze_7q1oVjDia4trRnd9ZZkq5P2ymhY/view"
        expected_id = "1X9ze_7q1oVjDia4trRnd9ZZkq5P2ymhY"
        self.assertEqual(extract_file_id(url), expected_id)

    def test_extract_file_id_invalid_url(self):
        url = "https://invalid-url.com"
        with self.assertRaises(ValueError):
            extract_file_id(url)

    @patch('csv_reader.csv_processor.open', new_callable=mock_open, read_data='product_name,photo_url,barcode,price_cents,sku (unique id),producer\nProduct1,http://example.com,123,1000,SKU1,Producer1\n')
    def test_read_csv(self, mock_file):
        data = read_csv('dummy.csv')
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['product_name'], 'Product1')
        self.assertEqual(data[0]['sku (unique id)'], 'SKU1')

    @patch('csv_reader.csv_processor.Session')
    def test_update_database(self, mock_session):
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock the query result to return None, simulating a new product
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = None

        data = [
            {
                'product_name': 'Product1',
                'photo_url': 'http://example.com',
                'barcode': '123',
                'price_cents': '1000',
                'sku (unique id)': 'SKU1',
                'producer': 'Producer1'
            }
        ]

        update_database(data)

        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(sku='SKU1')
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()

    @patch('csv_reader.csv_processor.Session')
    def test_update_existing_product(self, mock_session):
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        # Mock the query result to return an existing product
        existing_product = Product(
            product_name='Old Name',
            photo_url='http://old.com',
            barcode='old',
            price_cents=500,
            sku='SKU1',
            producer='Old Producer'
        )
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = existing_product

        data = [
            {
                'product_name': 'New Name',
                'photo_url': 'http://new.com',
                'barcode': 'new',
                'price_cents': '1000',
                'sku (unique id)': 'SKU1',
                'producer': 'New Producer'
            }
        ]

        update_database(data)

        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(sku='SKU1')
        mock_session_instance.add.assert_not_called()  # Should not be called for existing products
        mock_session_instance.commit.assert_called_once()

        # Check that the existing product was updated
        self.assertEqual(existing_product.product_name, 'New Name')
        self.assertEqual(existing_product.photo_url, 'http://new.com')
        self.assertEqual(existing_product.barcode, 'new')
        self.assertEqual(existing_product.price_cents, 1000)
        self.assertEqual(existing_product.producer, 'New Producer')

if __name__ == '__main__':
    unittest.main()