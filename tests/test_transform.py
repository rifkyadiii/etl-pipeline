import unittest
import pandas as pd
import numpy as np
from utils.transform import (
    transform_data,
    convert_to_idr,
    handle_missing_values,
    convert_data_types
)

class TestTransform(unittest.TestCase):
    
    def setUp(self):
        self.raw_df = pd.DataFrame([
            {'Title': 'Jacket A', 'Price': '$10.00', 'Rating': '4.0', 'Colors': '3', 'Size': 'L', 'Gender': 'Male', 'timestamp': '2024-01-01T00:00:00'},
            {'Title': 'Price Unavailable', 'Price': 'Price Unavailable', 'Rating': None, 'Colors': None, 'Size': None, 'Gender': None, 'timestamp': '2024-01-01T00:00:00'},
            {'Title': 'Unknown Product', 'Price': '$15.00', 'Rating': '4.5', 'Colors': '2', 'Size': 'M', 'Gender': 'Female', 'timestamp': '2024-01-01T00:00:00'},
            {'Title': 'Jacket A', 'Price': '$10.00', 'Rating': '4.0', 'Colors': '3', 'Size': 'L', 'Gender': 'Male', 'timestamp': '2024-01-01T00:00:00'}  # duplicate
        ])

    def test_convert_to_idr(self):
        self.assertEqual(convert_to_idr('$10.00'), 160000)
        self.assertEqual(convert_to_idr('$0.00'), 0)
        self.assertIsNone(convert_to_idr('invalid'))
        self.assertIsNone(convert_to_idr(None))

    def test_handle_missing_values(self):
        df = pd.DataFrame([
            {'Rating': None, 'Colors': None, 'Size': None, 'Gender': None}
        ])
        handled = handle_missing_values(df.copy())
        self.assertEqual(handled['Colors'][0], 0)
        self.assertEqual(handled['Size'][0], 'Unknown')
        self.assertEqual(handled['Gender'][0], 'Unknown')

    def test_convert_data_types(self):
        df = pd.DataFrame([
            {'Price': '10000', 'Rating': '4.5', 'Colors': '2 Colors', 'Size': ' XL ', 'Gender': ' Female ', 'timestamp': '2023-10-10T10:00:00'}
        ])
        converted = convert_data_types(df)
        self.assertIsInstance(converted['Price'][0], (int, float, np.integer))
        self.assertIsInstance(converted['Rating'][0], float)
        self.assertIsInstance(converted['Colors'][0], (int, np.integer))
        self.assertEqual(converted['Size'][0], 'XL')
        self.assertEqual(converted['Gender'][0], 'Female')

    def test_transform_data(self):
        transformed = transform_data(self.raw_df)
        self.assertEqual(len(transformed), 1)  # hanya satu baris unik valid
        self.assertEqual(transformed['Price'].iloc[0], 160000)
        self.assertEqual(transformed['Title'].iloc[0], 'Jacket A')

if __name__ == '__main__':
    unittest.main()
