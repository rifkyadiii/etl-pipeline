import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from pathlib import Path
from utils import load

class TestLoadModule(unittest.TestCase):
    def setUp(self):
        # Dummy DataFrame
        self.df = pd.DataFrame({
            'Title': ['Product A', 'Product B'],
            'Price': [320000.0, 480000.0],
            'Rating': [4.5, 3.7],
            'Colors': [3, 2],
            'Size': ['M', 'L'],
            'Gender': ['Men', 'Women'],
            'timestamp': ['2024-01-01 12:00:00', '2024-01-02 13:00:00']
        })

    @patch("utils.load.os.makedirs")
    @patch("utils.load.pd.DataFrame.to_csv")
    def test_load_to_csv_success(self, mock_to_csv, mock_makedirs):
        mock_to_csv.return_value = None
        result = load.load_to_csv(self.df)
        self.assertTrue(result)

    @patch("utils.load.create_engine")
    def test_load_to_postgres_success(self, mock_create_engine):
        mock_engine = MagicMock()
        mock_conn = mock_engine.connect.return_value.__enter__.return_value
        mock_create_engine.return_value = mock_engine

        result = load.load_to_postgres(self.df)
        self.assertTrue(result)

    @patch("utils.load.Path.exists", return_value=True)
    @patch("utils.load.gspread.authorize")
    @patch("utils.load.Credentials.from_service_account_file")
    def test_load_to_gsheets_success(self, mock_creds, mock_authorize, mock_exists):
        mock_gc = MagicMock()
        mock_ws = MagicMock()
        mock_authorize.return_value = mock_gc
        mock_gc.open_by_key.return_value.worksheet.return_value = mock_ws
        mock_ws.update.return_value = None

        result = load.load_to_gsheets(self.df)
        self.assertTrue(result)

    @patch("utils.load.load_to_csv", return_value=True)
    @patch("utils.load.load_to_postgres", return_value=True)
    @patch("utils.load.Path.exists", return_value=False)
    def test_load_data_csv_postgres_only(self, mock_exists, mock_postgres, mock_csv):
        result = load.load_data(self.df)
        self.assertTrue(result)

    @patch("utils.load.load_to_csv", return_value=False)
    @patch("utils.load.load_to_postgres", return_value=True)
    def test_load_data_csv_fail(self, mock_postgres, mock_csv):
        result = load.load_data(self.df)
        self.assertFalse(result)

    def test_prepare_dataframe_for_export(self):
        df_export = load.prepare_dataframe_for_export(self.df)
        self.assertEqual(df_export['timestamp'].dtype, object)

if __name__ == '__main__':
    unittest.main()
