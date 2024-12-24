from django.test import TestCase
import pandas as pd
from detector.services.ml_pipeline._feature_transformer import transform_single, transform_df, _one_hot_encode


class TransformSingleTests(TestCase):

    def test_valid_normal_input(self):
        pass

    def test_null_input(self):
        pass

    def test_null_col_data(self):
        pass

    def test_missing_col_data_entry_for_categorical(self):
        pass

    def test_missing_col_data_entry_for_numerical(self):
        pass

    def test_missing_input_value(self):
        pass

    def test_extra_col_data_entry_for_categorical(self):
        pass

    def test_extra_col_data_entry_for_numerical(self):
        pass


class TransformDFTests(TestCase):

    def test_valid_normal_input(self):
        pass

    def test_null_col_data(self):
        pass

    def test_null_df(self):
        pass

    def test_missing_col_data_entry_for_categorical(self):
        pass

    def test_missing_col_data_entry_for_numerical(self):
        pass

    def test_extra_col_data_entry_for_categorical(self):
        pass

    def test_extra_col_data_entry_for_numerical(self):
        pass

    def test_missing_df_value(self):
        pass


class OneHotEncodeTests(TestCase):

    # ------------------------ SHOULD PASS ----------------------- #

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
