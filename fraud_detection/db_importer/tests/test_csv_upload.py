import os
from unittest.mock import patch
from django.test import TestCase
from db_importer.services.csv_handler import process_csv
from fraud_detection import settings


class ImportCSVToDBUnitTest(TestCase):
    def setUp(self):
        # Path to CSV files 
        self.valid_csv_path = os.path.join(settings.BASE_DIR, 'db_importer', 'tests', 'fixtures', 'test_valid_file.csv')
        self.invalid_csv_path = os.path.join(settings.BASE_DIR, 'db_importer', 'tests', 'fixtures', 'test_invalid_file.csv')

    @patch('db_importer.services.csv_handler.validate_csv_data')  # Mock the validate_csv_data function
    @patch('db_importer.services.csv_handler.Transaction.objects.bulk_create')  # Mock database interaction
    def test_valid_csv_pipeline(self, mock_bulk_create, mock_validate_csv_data):
        # Simulate a successful process_csv result
        mock_validate_csv_data.return_value = {"status": "success", "message": "File processed successfully!"}
        
        # Mock bulk_create to prevent actual database insertion
        mock_bulk_create.return_value = None

        # Open the file in binary mode and pass it directly to process_csv
        with open(self.valid_csv_path, 'rb') as file:
            result = process_csv(file)

        # Assert the view redirects to the success page
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "File processed successfully!")
        mock_validate_csv_data.assert_called_once_with("/tmp/uploaded_file.csv")

        # Verify bulk_create was called
        self.assertTrue(mock_bulk_create.called)
        print("Database Insertion Mock Call Arguments:", mock_bulk_create.call_args_list)

    @patch('db_importer.services.csv_handler.Transaction.objects.bulk_create')  # Mock bulk_create
    @patch('db_importer.services.csv_handler.validate_csv_data')  # Mock validate_csv_data
    def test_process_csv_invalid_file(self, mock_validate_csv_data, mock_bulk_create):
        # Mock validation to return an error
        mock_validate_csv_data.return_value = {
            "status": "error",
            "message": "Validation failed due to invalid data."
        }

        # Open the file in binary mode and pass it directly to process_csv
        with open(self.invalid_csv_path, 'rb') as file:
            result = process_csv(file)

        # Assertions
        self.assertEqual(result["status"], "error")
        self.assertIn("Validation failed", result["message"])

        # Verify validate_csv_data was called with the correct arguments
        mock_validate_csv_data.assert_called_once_with("/tmp/uploaded_file.csv")

        # Verify bulk_create was not called
        mock_bulk_create.assert_not_called()