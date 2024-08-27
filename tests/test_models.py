import unittest
from app.models import Product


class TestModels(unittest.TestCase):

    def test_product_model(self):
        product = Product(
            product_name="Test Product",
            photo_url="http://example.com",
            barcode="123456",
            price_cents=1000,
            sku="TEST-SKU",
            producer="Test Producer",
        )

        self.assertEqual(product.product_name, "Test Product")
        self.assertEqual(product.photo_url, "http://example.com")
        self.assertEqual(product.barcode, "123456")
        self.assertEqual(product.price_cents, 1000)
        self.assertEqual(product.sku, "TEST-SKU")
        self.assertEqual(product.producer, "Test Producer")


if __name__ == "__main__":
    unittest.main()
