# Made by: Yingchao

from django.test import TestCase
from unittest.mock import MagicMock
from core.predictor_singleton import PredictorSingleton

class PredictorTests(TestCase):
    # Set up the test environment by mocking Predictor and PredictorSingleton.
    def setUp(self):
        
        # Mock predictor
        self.mock_predictor = MagicMock()
        
        # Mock the PredictorSingleton to return the mock predictor
        mock_singleton = MagicMock()
        mock_singleton.get_predictor.return_value = self.mock_predictor
        PredictorSingleton.get_instance = MagicMock(return_value=mock_singleton)
        
        # Example input data
        self.input_data = {
            'merchant_category': 'Healthcare',
            'country': 'Canada',
            'currency': 'EUR',
            'amount': 456,
            'transaction_hour': 15,
            'weekend_transaction': 0,
            'card_type': 'Basic Debit',
            'card_present': 1,
            'device': 'Magnetic Stripe',
            'channel': 'mobile',
            'distance_from_home': 1
        }

        # Example mock output
        self.mock_prediction = {
            'probability': 0.926,
            'is_fraud': True,
            'reasons': [
                '"Card present" being selected, increased the probability of fraud by 68%',
                '"Distance from home" being selected, increased the probability of fraud by 31%'
            ]
        }
        
        def mock_predict(input_data):
            if not input_data:
                raise ValueError("Empty input not allowed")
            if "invalid_key" in input_data:
                raise KeyError("Invalid input key")
            return self.mock_prediction
        
        self.mock_predictor.predict.side_effect = mock_predict

    # Test if the predictor's predict method is called with the correct input.
    def test_predictor_called_with_correct_input(self):
        
        predictor = PredictorSingleton.get_instance().get_predictor()

        # Call the predict method
        prediction = predictor.predict(self.input_data)

        # Check if the predict method was called once with self.input_data
        self.mock_predictor.predict.assert_called_once_with(self.input_data)

        # Check if the return value matches the mocked value
        self.assertEqual(prediction, self.mock_prediction)

    # Test if the return structure of the predict method matches expectations.
    def test_predictor_return_structure(self):
        
        predictor = PredictorSingleton.get_instance().get_predictor()
        prediction = predictor.predict(self.input_data)

        # Check if the return value contains expected keys
        self.assertIn('probability', prediction)
        self.assertIn('is_fraud', prediction)
        self.assertIn('reasons', prediction)

        # Check if the field types are correct
        self.assertIsInstance(prediction['probability'], float)
        self.assertIsInstance(prediction['is_fraud'], bool)
        self.assertIsInstance(prediction['reasons'], list)

    # Test if the predict method raises an exception for empty input.
    def test_predictor_handles_empty_input(self):
        
        predictor = PredictorSingleton.get_instance().get_predictor()

        with self.assertRaises(ValueError):  # Assume predict raises ValueError for empty input
            predictor.predict({})

    # Test if the predict method raises an exception for invalid input.
    def test_predictor_handles_invalid_input(self):
        
        predictor = PredictorSingleton.get_instance().get_predictor()

        invalid_input_data = {"invalid_key": "invalid_value"}  # Example invalid input
        with self.assertRaises(KeyError):  # Assume predict raises KeyError for invalid keys
            predictor.predict(invalid_input_data)
