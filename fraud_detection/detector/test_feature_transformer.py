from django.test import TestCase
import pandas as pd
from detector.services.ml_pipeline._feature_transformer import transform_single, transform_df, _one_hot_encode
from datetime import datetime

col_data = {
    "euros": {
        "std": 926.890265767884,
        "mean": 606.3402683218625
    },
    "amount": {
        "std": 259435.16796209908,
        "mean": 75496.7242845
    },
    "device": [
        "Android App", "Chip Reader", "Chrome", "Edge", "Firefox", "Magnetic Stripe", "NFC Payment", "Safari",
        "iOS App", "unknown"
    ],
    "channel": ["mobile", "pos", "unknown", "web"],
    "country": [
        "Australia", "Brazil", "Canada", "France", "Germany", "Japan", "Mexico", "Nigeria", "Russia", "Singapore", "UK",
        "USA", "unknown"
    ],
    "currency": ["AUD", "BRL", "CAD", "EUR", "GBP", "JPY", "MXN", "NGN", "RUB", "SGD", "USD", "unknown"],
    "card_type": ["Basic Credit", "Basic Debit", "Gold Credit", "Platinum Credit", "Premium Debit", "unknown"],
    "transaction_hour": {
        "std": 0.9492128529746034,
        "mean": 1.0751
    },
    "merchant_category":
    ["Education", "Entertainment", "Gas", "Grocery", "Healthcare", "Restaurant", "Retail", "Travel", "unknown"]
}


class TransformSingleTests(TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

        self.input = {
            'merchant_category': 'Restaurant',
            'currency': 'EUR',
            'country': 'SE',
            'card_type': 'credit',
            'device': 'mobile',
            'channel': 'online',
            'amount': 50.75,
            'transaction_hour': 14.0,
            'euros': 50.75,
            'hour_sin': 0.866,
            'hour_cos': 0.5,
            'card_present': False,
            'distance_from_home': True,
            'weekend_transaction': False
        }

    # ------------------------ SHOULD WORK ----------------------- #

    def test_valid_normal_input(self):
        result = transform_single(self.input, col_data)
        self.assertTrue(result.df.map(lambda x: isinstance(x, (bool, float))).all().all())
        self.assertEqual(len(result.df.columns), 62)

    def test_unknown_categorical(self):
        input_cpy = self.input.copy()
        input_cpy['device'] = 'some_category_not_in_col_data'

        result = transform_single(input_cpy, col_data)

        self.assertTrue(result.df.map(lambda x: isinstance(x, (bool, float))).all().all())
        self.assertEqual(len(result.df.columns), 62)

        for col in result.df.columns:
            if col.startswith('device='):
                self.assertEqual(result.df[col].values[0], 0.0)

    # ------------------- SHOULD FAIL CORRECTLY ------------------ #

    def test_null_input(self):
        with self.assertRaises(TypeError):
            transform_single(None, col_data)

    def test_null_col_data(self):
        with self.assertRaises(TypeError):
            transform_single(self.input, None)

    def test_missing_col_data_entry_for_categorical(self):
        col_data_cpy = col_data.copy()
        col_data_cpy.pop('device')

        with self.assertRaises(KeyError):
            transform_single(self.input, col_data_cpy)

    def test_missing_col_data_entry_for_numerical(self):
        col_data_cpy = col_data.copy()
        col_data_cpy.pop('transaction_hour')

        with self.assertRaises(KeyError):
            transform_single(self.input, col_data_cpy)

    def test_missing_input_value(self):
        input_cpy = self.input.copy()
        input_cpy.pop('amount')

        with self.assertRaises(KeyError):
            transform_single(input_cpy, col_data)


class TransformDfTests(TestCase):

    def __init__(self, methodName="runTest"):
        super().__init__(methodName)

        self.df = pd.DataFrame({
            'merchant_category': ['Restaurant', 'Retail', 'Retail', 'Restaurant', 'Restaurant'],
            'currency': ['EUR', 'USD', 'USD', 'EUR', 'EUR'],
            'country': ['SE', 'US', 'US', 'SE', 'SE'],
            'card_type': ['credit', 'debit', 'debit', 'credit', 'credit'],
            'device': ['mobile', 'web', 'mobile', 'mobile', 'web'],
            'channel': ['online', 'online', 'pos', 'online', 'online'],
            'amount': [50.75, 100.0, 150.0, 200.0, 250.0],
            'transaction_hour': [14.0, 15.0, 16.0, 17.0, 18.0],
            'euros': [50.75, 100.0, 150.0, 200.0, 250.0],
            'hour_sin': [0.866, 0.5, 0.0, -0.5, -0.866],
            'hour_cos': [0.5, 0.866, 1.0, 0.866, 0.5],
            'card_present': [False, True, False, True, False],
            'distance_from_home': [True, False, True, False, True],
            'weekend_transaction': [False, False, False, False, True],
            'timestamp': [datetime.now(),
                          datetime.now(),
                          datetime.now(),
                          datetime.now(),
                          datetime.now()],
            'is_fraud': [False, False, False, False, True]
        })

    # ------------------------ SHOULD WORK ----------------------- #

    def test_with_col_data(self):
        result = transform_df(self.df, col_data)
        self.assertTrue(result.df.map(lambda x: isinstance(x, (bool, float))).all().all())
        self.assertEqual(len(result.df.columns), 63)

    def test_null_col_data(self):
        ''' Valid case, col_data will be calculated when not provided '''
        result = transform_df(self.df, None)
        self.assertTrue(result.df.map(lambda x: isinstance(x, (bool, float))).all().all())
        self.assertEqual(len(result.df.columns), 21)

    # ------------------- SHOULD FAIL CORRECTLY ------------------ #

    def test_null_df(self):
        with self.assertRaises(TypeError):
            transform_df(None, col_data)

    def test_missing_col_data_entry_for_categorical(self):
        col_data_cpy = col_data.copy()
        col_data_cpy.pop('device')

        with self.assertRaises(KeyError):
            transform_df(self.df, col_data_cpy)

    def test_missing_col_data_entry_for_numerical(self):
        col_data_cpy = col_data.copy()
        col_data_cpy.pop('transaction_hour')

        with self.assertRaises(KeyError):
            transform_df(self.df, col_data_cpy)

    def test_missing_df_col(self):
        df_cpy = self.df.copy()
        df_cpy.pop('merchant_category')

        with self.assertRaises(KeyError):
            transform_df(df_cpy, col_data)


class OneHotEncodeTests(TestCase):

    # ------------------------ SHOULD WORK ----------------------- #

    def test_valid_normal_input(self):
        df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['Rock', 'Paper', 'Scissors'], 'col3': ['1', '2', '3']})
        col = 'col2'
        categories = ['Rock', 'Paper', 'Scissors']
        expected = pd.DataFrame({
            'col1': ['a', 'b', 'c'],
            'col3': ['1', '2', '3'],
            'col2=Rock': [1.0, 0.0, 0.0],
            'col2=Paper': [0.0, 1.0, 0.0],
            'col2=Scissors': [0.0, 0.0, 1.0],
        })

        result = _one_hot_encode(df, col, categories)
        self.assertTrue(result.equals(expected))

    def test_categories_with_special_chars(self):
        df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['Rock', 'Paper', 'Scissors'], 'col3': ['1', '2', '3']})
        col = 'col2'
        categories = [
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero.',
            '',
            'DQ*bFY!Lz2efko@afAd'  # NOTE - my facebook password
        ]

        result = _one_hot_encode(df, col, categories)
        self.assertEqual(len(result.columns), 5)
        transformed_rows = result.iloc[:, -3:]

        # Checks that the transformed rows are all 0 or 1
        self.assertTrue(transformed_rows.isin([0, 1]).all().all())

    # --------------------- SHOULD FAIL CORRECTLY -------------------- #

    def test_col_not_in_df(self):
        df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['Rock', 'Paper', 'Scissors'], 'col3': ['1', '2', '3']})
        col = 'col_not_in_df'
        categories = ['Rock', 'Paper', 'Scissors']

        with self.assertRaises(KeyError):
            _one_hot_encode(df, col, categories)

    def test_null_col(self):
        df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['Rock', 'Paper', 'Scissors'], 'col3': ['1', '2', '3']})
        col = None
        categories = ['Rock', 'Paper', 'Scissors']

        with self.assertRaises((KeyError, ValueError)):  # NOTE - Both errors make sense
            _one_hot_encode(df, col, categories)

    def test_empty_categories(self):
        df = pd.DataFrame({'col1': ['a', 'b', 'c'], 'col2': ['Rock', 'Paper', 'Scissors'], 'col3': ['1', '2', '3']})
        col = None
        categories = []

        with self.assertRaises((ValueError, KeyError)):  # NOTE - Both errors make sense
            _one_hot_encode(df, col, categories)
