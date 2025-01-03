# Made by Janos

from django.test import TestCase
from unittest.mock import patch, MagicMock
from datetime import datetime
import pandas as pd
from sqlalchemy.exc import SQLAlchemyError
from detector.services.ml_pipeline._data_loader import load_data


class LoadDataTests(TestCase):
    @patch("detector.services.ml_pipeline._data_loader.create_engine")
    @patch("detector.services.ml_pipeline._data_loader.pd.read_sql")
    def test_load_data_success(self, mock_read_sql, mock_create_engine):
        """Test that load_data returns a DataFrame when data is found."""
        # Mock the database engine and read_sql
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Mock the data returned by the database
        mock_data = pd.DataFrame({
            "id": [1, 2],
            "version_date": [datetime(2024, 10, 1), datetime(2024, 10, 2)],
        })
        mock_read_sql.return_value = mock_data

        # Call the function
        result = load_data(sample_size=2, start=datetime(2024, 10, 1), end=datetime(2024, 12, 4))

        # Assertions
        self.assertFalse(result.empty)
        self.assertEqual(len(result), 2)
        mock_create_engine.assert_called_once()
        mock_read_sql.assert_called_once()

    @patch("detector.services.ml_pipeline._data_loader.create_engine")
    @patch("detector.services.ml_pipeline._data_loader.pd.read_sql")
    def test_load_data_no_data(self, mock_read_sql, mock_create_engine):
        """Test that load_data raises ValueError when no data is found."""
        # Mock the database engine and read_sql
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        # Mock an empty DataFrame returned by the database
        mock_read_sql.return_value = pd.DataFrame()

        # Call the function and expect a ValueError
        with self.assertRaises(ValueError):
            load_data(sample_size=2, start=datetime(2024, 10, 1), end=datetime(2024, 12, 4))

        mock_create_engine.assert_called_once()
        mock_read_sql.assert_called_once()

    @patch("detector.services.ml_pipeline._data_loader.create_engine")
    @patch("detector.services.ml_pipeline._data_loader.pd.read_sql")
    def test_load_data_db_error(self, mock_read_sql, mock_create_engine):
        """Test that load_data handles database errors gracefully."""
        # Mock the database engine and simulate a database error
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine
        mock_read_sql.side_effect = SQLAlchemyError("Database error")

        # Call the function and expect a SQLAlchemyError
        with self.assertRaises(SQLAlchemyError):
            load_data(sample_size=2, start=datetime(2024, 10, 1), end=datetime(2024, 12, 4))

        mock_create_engine.assert_called_once()