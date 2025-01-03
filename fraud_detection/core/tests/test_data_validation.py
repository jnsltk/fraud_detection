'''
    Made by: Shiyao Xin
'''

import json
import subprocess
from unittest.mock import patch
from django.test import TestCase
import io
import pandas as pd

class InputDataValidationTest(TestCase):
    @patch('core.views.subprocess.run')
    def test_valid_input_data(self, mock_subprocess_run):
        # Mock subprocess.run for successful validation
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["python", "validate_data.py"],
            returncode=0,
            stdout=json.dumps({"status": "success", "message": "Validation succeeded!"}),
            stderr=""
        )

        # Sample valid input data
        input_data = {
            'merchant_category': 'Grocery',
            'country': 'Germany',
            'currency': 'EUR',
            'amount': 1000,
            'transaction_hour': 14,
            'weekend_transaction': False,
            'card_type': 'Basic Credit',
            'card_present': True,
            'device': 'Chip Reader',
            'channel': 'pos',
            'distance_from_home': False,
        }
        df = pd.DataFrame([input_data])
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Call validation logic
        csv_data = csv_buffer.getvalue()
        result = subprocess.run(
            ["python", "validate_data.py"],
            input=csv_data,
            capture_output=True,
            text=True,
        )

        # Assert validation passed
        self.assertEqual(result.returncode, 0)
        self.assertIn("Validation succeeded!", result.stdout)


    @patch('core.views.subprocess.run')
    def test_invalid_input_data(self, mock_subprocess_run):
        # Mock subprocess.run for failed validation
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["python", "validate_data.py"],
            returncode=1,
            stdout=json.dumps({
                "status": "error",
                "message": "Validation failed.",
                "failures": [
                    {
                        "expectation": "expect_column_values_to_be_between",
                        "column": "amount",
                        "unexpected_count": 1,
                        "unexpected_percent": 100,
                        "sample_unexpected": [-100.0]
                    }
                ]
            }),
            stderr=""
        )

        # Sample invalid input data
        input_data = {
            'merchant_category': 'Grocery',
            'country': 'Germany',
            'currency': 'EUR',
            'amount': -100,  # Invalid amount
            'transaction_hour': 12,
            'weekend_transaction': False,
            'card_type': 'Basic Credit',
            'card_present': True,
            'device': 'Chip Reader',
            'channel': 'pos',
            'distance_from_home': False,
        }
        df = pd.DataFrame([input_data])
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Call validation logic
        csv_data = csv_buffer.getvalue()
        result = subprocess.run(
            ["python", "validate_data.py"],
            input=csv_data,
            capture_output=True,
            text=True,
        )

        # Assert validation failed
        self.assertEqual(result.returncode, 1)
        self.assertIn("Validation failed.", result.stdout)
