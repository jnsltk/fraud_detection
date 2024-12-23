from django.test import TestCase


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

    def test_valid_normal_input(self):
        pass

    def test_empty_df(self):
        pass

    def test_col_not_in_df(self):
        pass

    def test_null_col(self):
        pass

    def test_empty_categories(self):
        pass
