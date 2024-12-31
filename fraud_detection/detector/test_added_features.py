from currency_converter import ECB_URL
from django.test import TestCase
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from detector.services.ml_pipeline.added_features import has_currency, row_to_eur, add_hour_trig_cols, _setup_currency_converter

class AddedFeaturesTests(TestCase):
    @patch("detector.services.ml_pipeline.added_features.c.currencies", new_callable=set)
    def test_has_currency_true(self, mock_currencies):
        """Test has_currency returns True for valid currencies."""
        mock_currencies.update({"USD", "EUR"})
        self.assertTrue(has_currency("USD"))
        self.assertTrue(has_currency("EUR"))
        self.assertTrue(has_currency("NGN"))

    @patch("detector.services.ml_pipeline.added_features.c.currencies", new_callable=set)
    def test_has_currency_false(self, mock_currencies):
        """Test has_currency returns False for invalid currencies."""
        mock_currencies.update({"USD", "EUR"})
        self.assertFalse(has_currency("ABC"))

    @patch("detector.services.ml_pipeline.added_features.c.convert")
    def test_row_to_eur_ngn(self, mock_convert):
        """Test row_to_eur for NGN currency."""
        row = [1000, None, "NGN"]
        result = row_to_eur(row, euro_mean=None)
        self.assertEqual(result, 1000 * 0.00057)

    @patch("detector.services.ml_pipeline.added_features.c.convert")
    def test_row_to_eur_other(self, mock_convert):
        """Test row_to_eur for OTHER currency."""
        row = [500, None, "other"]
        result = row_to_eur(row, euro_mean=None)
        self.assertEqual(result, 500)

    @patch("detector.services.ml_pipeline.added_features.c.currencies", new_callable=set)
    def test_row_to_eur_unknown_currency(self, mock_currencies):
        """Test row_to_eur for unknown currency, falling back to euro_mean."""
        mock_currencies.update({"USD", "EUR"})
        row = [1000, None, "ABC"]
        euro_mean = 42.5
        result = row_to_eur(row, euro_mean=euro_mean)
        self.assertEqual(result, euro_mean)

    @patch("detector.services.ml_pipeline.added_features.c.convert")
    def test_row_to_eur_conversion(self, mock_convert):
        """Test row_to_eur for valid conversion."""
        mock_convert.return_value = 42.0
        row = [1000, "2024-12-01", "USD"]
        result = row_to_eur(row, euro_mean=None)
        self.assertEqual(result, 42.0)
        mock_convert.assert_called_once_with(1000, "USD", date="2024-12-01")

    def test_add_hour_trig_cols(self):
        """Test add_hour_trig_cols adds correct columns."""
        df = pd.DataFrame({"transaction_hour": [0, 6, 12, 18]})
        add_hour_trig_cols(df)

        # Ensure columns were added
        self.assertIn("hour_sin", df.columns)
        self.assertIn("hour_cos", df.columns)

        expected_sin = [0.0, 1.0, 0.0, -1.0]
        expected_cos = [1.0, 0.0, -1.0, 0.0]

        # Assert almost equal to account for floating-point precision
        np.testing.assert_almost_equal(df["hour_sin"].values, expected_sin, decimal=7)
        np.testing.assert_almost_equal(df["hour_cos"].values, expected_cos, decimal=7)

    def test_add_hour_trig_cols_missing_values(self):
        """Test add_hour_trig_cols raises ValueError for missing values."""
        df = pd.DataFrame({"transaction_hour": [None, 6, 12, 18]})
        with self.assertRaises(ValueError):
            add_hour_trig_cols(df)

    @patch("detector.services.ml_pipeline.added_features.urllib.request.urlretrieve")
    @patch("detector.services.ml_pipeline.added_features.os.path.exists")
    @patch("detector.services.ml_pipeline.added_features.CurrencyConverter")
    def test_setup_currency_converter_download(self, mock_currency_converter, mock_exists, mock_urlretrieve):
        """Test _setup_currency_converter with download."""

        # Mock directory existence for EUR_DIR_1
        def side_effect_exists(path):
            # Directory exists, but file doesn't initially
            if path == "data":
                return True  # Simulates the presence of EUR_DIR_1
            if path == "data/eurofxref-hist.zip":
                return False  # Simulates that the file does not exist initially
            return False

        mock_exists.side_effect = side_effect_exists

        # Simulate a successful file download
        def side_effect_urlretrieve(url, filepath):
            # After download, the file should now "exist"
            mock_exists.side_effect = lambda path: path in ["data", "data/eurofxref-hist.zip"]

        mock_urlretrieve.side_effect = side_effect_urlretrieve

        # Call the function
        _setup_currency_converter()

        # Assertions
        mock_urlretrieve.assert_called_once_with(ECB_URL, "data/eurofxref-hist.zip")
        mock_currency_converter.assert_called_once_with(
            "data/eurofxref-hist.zip",
            fallback_on_missing_rate=True,
            fallback_on_wrong_date=True,
        )

    @patch("detector.services.ml_pipeline.added_features.urllib.request.urlretrieve")
    @patch("detector.services.ml_pipeline.added_features.os.path.exists")
    def test_setup_currency_converter_file_not_found(self, mock_exists, mock_urlretrieve):
        """Test _setup_currency_converter raises FileNotFoundError."""
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            _setup_currency_converter()