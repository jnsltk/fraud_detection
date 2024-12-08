'''
    NOTE - The bulk of the data validations is performed db_importer app, meaning the loaded data from the database is already clean.
        These simple tests simply tests the results of the transformer and loader.
'''


def test(df):
    ''' Throws if any test fails '''

    # throws if is_fraud column is not last
    if df.columns[-1] != 'is_fraud':
        raise Exception(f'Invalid label-column: {df.columns[-1]}')

    # throws if unhandled null-values
    sum_of_nulls = df.isnull().sum().sum()
    if sum_of_nulls > 0:
        raise Exception(f'{sum_of_nulls} unhandled null-values')
