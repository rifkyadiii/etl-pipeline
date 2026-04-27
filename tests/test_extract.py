import unittest
from unittest.mock import patch, Mock
from bs4 import BeautifulSoup
from utils.extract import scrape_product, scrape_main

class TestScraper(unittest.TestCase):

    def test_scrape_product_valid(self):
        html = '''
        <div class="collection-card">
            <div style="position: relative;">
                <img src="https://picsum.photos/280/350?random=1" class="collection-image" alt="Cool Jacket">
            </div>
            <div class="product-details">
                <h3 class="product-title">Cool Jacket</h3>
                <div class="price-container"><span class="price">$59.99</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ 4.5 / 5</p>
                <p style="font-size: 14px; color: #777;">5 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: M</p>
                <p style="font-size: 14px; color: #777;">Gender: Unisex</p>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        product_card = soup.select_one('.collection-card')
        result = scrape_product(product_card)

        self.assertIsNotNone(result)
        self.assertEqual(result['Title'], 'Cool Jacket')
        self.assertEqual(result['Price'], '$59.99')
        self.assertEqual(result['Rating'], '4.5')
        self.assertEqual(result['Colors'], '5')
        self.assertEqual(result['Size'], 'M')
        self.assertEqual(result['Gender'], 'Unisex')

    def test_scrape_product_invalid_rating(self):
        html = '''
        <div class="collection-card">
            <div class="product-details">
                <h3 class="product-title">Invalid Product</h3>
                <div class="price-container"><span class="price">$29.99</span></div>
                <p style="font-size: 14px; color: #777;">Rating: ⭐ Invalid Rating / 5</p>
                <p style="font-size: 14px; color: #777;">2 Colors</p>
                <p style="font-size: 14px; color: #777;">Size: S</p>
                <p style="font-size: 14px; color: #777;">Gender: Women</p>
            </div>
        </div>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        product_card = soup.select_one('.collection-card')
        result = scrape_product(product_card)

        self.assertIsNotNone(result)
        self.assertIsNone(result['Rating'])

    @patch('utils.extract.requests.get')
    def test_scrape_main_with_mock(self, mock_get):
        mock_html = '''
        <div class="collection-grid" id="collectionList">
            <div class="collection-card">
                <div class="product-details">
                    <h3 class="product-title">Test Shirt</h3>
                    <div class="price-container"><span class="price">$19.99</span></div>
                    <p style="font-size: 14px; color: #777;">Rating: ⭐ 3.5 / 5</p>
                    <p style="font-size: 14px; color: #777;">2 Colors</p>
                    <p style="font-size: 14px; color: #777;">Size: S</p>
                    <p style="font-size: 14px; color: #777;">Gender: Male</p>
                </div>
            </div>
        </div>
        '''
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mock_html.encode('utf-8')
        mock_get.return_value = mock_response

        with patch('utils.extract.BASE_URL', 'https://mock-url.dev'):
            df = scrape_main()

        self.assertEqual(len(df), 50)
        self.assertIn('Title', df.columns)
        self.assertIn('Price', df.columns)
        self.assertIn('Rating', df.columns)

if __name__ == '__main__':
    unittest.main()