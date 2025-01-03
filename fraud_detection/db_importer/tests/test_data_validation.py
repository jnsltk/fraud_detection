'''
    Made by: Shiyao Xin
'''

import json
import subprocess
from unittest.mock import patch
from django.test import TestCase
from db_importer.services.csv_handler import validate_csv_data


class DataValidationTest(TestCase):
    @patch('db_importer.services.csv_handler.subprocess.run')
    @patch('db_importer.services.csv_handler.os.path.isfile', return_value=True)  # Mock file existence check
    def test_validate_valid_csv(self, mock_isfile, mock_subprocess_run):
        # Mock subprocess.run for a successful validation
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["python", "validate_data.py", "/tmp/test_valid.csv"],
            returncode=0,
            stdout=json.dumps({
                "status": "success",
                "message": "Validation succeeded!"
            }),
            stderr=""
        )

        # Call validate_csv_data with the temporary file path
        result = validate_csv_data("/tmp/test_valid.csv")
        
        # Assert validation succeeded
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["message"], "Validation succeeded!")


    @patch('db_importer.services.csv_handler.subprocess.run')
    @patch('db_importer.services.csv_handler.os.path.isfile', return_value=True)  # Mock file existence check
    def test_validate_invalid_csv(self, mock_isfile, mock_subprocess_run):
        # Mock subprocess.run for a failed validation
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["python", "validate_data.py", "/tmp/test_invalid.csv"],
            returncode=1,
            stdout=json.dumps({
                "status": "error",
                "message": "Validation failed.",
                "failures": [
                    {
                        "expectation": "expect_column_values_to_be_of_type",
                        "column": "merchant_type",
                        "unexpected_count": None,
                        "unexpected_percent": None,
                        "partial_unexpected_list": None
                    }
                ]
            }),
            stderr=""
        )

        # Call validate_csv_data with the temporary file path
        result = validate_csv_data("/tmp/test_invalid.csv")
        
        # Assert validation failed
        self.assertEqual(result["status"], "error")
        self.assertIn("Validation failed.", result["message"])
        self.assertIn("failures", result["message"])


    @patch('db_importer.services.csv_handler.subprocess.run')
    @patch('db_importer.services.csv_handler.os.path.isfile', return_value=True)  # Mock file existence check
    def test_invalid_json_output(self, mock_isfile, mock_subprocess_run):
        # Mock subprocess.run with invalid JSON output
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["python", "validate_data.py", "test.csv"],
            returncode=0,
            stdout="Invalid JSON",
            stderr=""
        )

        # Call validate_csv_data and expect JSONDecodeError handling
        result = validate_csv_data("test.csv")

        self.assertEqual(result["status"], "error")
        self.assertIn("Validation script returned invalid or empty output.", result["message"])