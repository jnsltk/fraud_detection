import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import numpy as np
from datetime import datetime
from dataclasses import dataclass
import added_features

# ========================== CLASSES ========================= #


@dataclass
class TransformSingleResult:
    df: pd.DataFrame
    euros: float
    hour_sin: float
    hour_cos: float


@dataclass
class TransformDfResult:
    df: pd.DataFrame
    categories: dict[str, list]
    stats: dict[str, dict[str, float]]


# =========================== CONSTANTS ========================== #

UNKNOWN = 'unknown'
UNKNOWN_IN_TRAINING_PERCENTAGE = 0.1

USED_FEATURES = [
    'merchant_category', 'amount', 'currency', 'country', 'card_type', 'card_present', 'device', 'channel',
    'distance_from_home', 'transaction_hour', 'weekend_transaction', 'euros', 'hour_sin', 'hour_cos'
]

CAT_COLS = ['merchant_category', 'currency', 'country', 'card_type', 'device', 'channel']
NUM_COLS = ['amount', 'transaction_hour', 'euros', 'hour_sin', 'hour_cos']
BOOL_COLS = ['card_present', 'distance_from_home', 'weekend_transaction']

STANDARDISED_COLS = ['amount', 'transaction_hour', 'euros']

# ======================== PUBLIC METHODS ======================= #


def transform_single(input: dict, col_data: dict[str, any]) -> TransformSingleResult:
    ''' Throws ValueError if the input is invalid '''

    df = pd.DataFrame([input])

    # Adds euros column
    amount_cols = [input['amount'], datetime.now(), input['currency']]
    euro = added_features.row_to_eur(amount_cols, euro_mean=col_data['euros']['mean'])
    df['euros'] = [euro]

    # Adds hour trig columns
    added_features.add_hour_trig_cols(df)
    hour_sin = df['hour_sin'].values[0]
    hour_cos = df['hour_cos'].values[0]

    # Selects feature subset & Sorts columns
    df = df[USED_FEATURES].copy()

    # Handles missing numerical values
    if df.select_dtypes(include=[np.number]).isnull().values.any():
        raise ValueError('Missing values in numerical columns')

    # One-hot encodes categorical features
    for col in CAT_COLS:
        df = _one_hot_encode(df, col, col_data[col])

    # Standardises numerical features
    for col in STANDARDISED_COLS:
        df[col] = (df[col] - col_data[col]['mean']) / col_data[col]['std']

    # Returns the transformed dataframe
    return TransformSingleResult(df, euros=euro, hour_cos=hour_cos, hour_sin=hour_sin)


# Note - col_data will be passed if model is already trained, and the function is used for SHAP
def transform_df(df: pd.DataFrame, col_data: dict[str:any] = None) -> TransformDfResult:

    # Adds euros column, inspired by ChatGPT
    df['euros'] = [
        added_features.row_to_eur(row, euro_mean=None)
        for row in df[['amount', 'timestamp', 'currency']].itertuples(index=False)
    ]

    # Adds hour trig columns
    added_features.add_hour_trig_cols(df)

    # Selects feature subset & sorts columns
    df = df[USED_FEATURES + ['is_fraud']].copy()

    # Fills missing values for numerical features with mean
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].mean())

    # One-hot encodes categorical features
    unknowns_amt = int(UNKNOWN_IN_TRAINING_PERCENTAGE * len(df))
    categories = {}
    for col in CAT_COLS:

        # Sets some values to unknown to learn to handle unknown values
        unknowns_idxs = np.random.choice(df.index, unknowns_amt, replace=False)
        df.loc[unknowns_idxs, col] = UNKNOWN

        if col_data is None:
            categories[col] = sorted(df[col].unique())
        else:
            categories[col] = col_data[col]

        # One-hot encodes column
        df = _one_hot_encode(df, col, categories[col])

    # Standardises numerical features
    stats = {}
    for col in STANDARDISED_COLS:
        # Note - Uses pre-calculated, more accurate stats for mean and std if available
        stats[col] = {'mean': df[col].mean(), 'std': df[col].std()} if col_data is None else col_data[col]

        df[col] = (df[col] - stats[col]['mean']) / stats[col]['std']

    # Move is_fraud to the last column
    df['is_fraud'] = df.pop('is_fraud')

    # Returns the result of the transformation
    return TransformDfResult(df, categories, stats)


# ====================== PRIVATE METHODS ====================== #


def _one_hot_encode(df: pd.DataFrame, col: str, categories: list) -> pd.DataFrame:

    # Creates and fits encoder with the categories
    encoder = OneHotEncoder(categories=[categories], handle_unknown='ignore')
    encoder.fit(df[[col]])

    # Encodes the column
    encoded = encoder.transform(df[[col]])
    columns = [f'{col}={cat}' for cat in categories]
    encoded_df = pd.DataFrame(encoded.toarray(), columns=columns)

    # Replaces original column with encoded columns
    df = pd.concat([df, encoded_df], axis=1)
    df.drop(columns=[col], inplace=True)

    # Returns the transformed dataframe
    return df


# ============================ TESTS =========================== #

if set(USED_FEATURES) != set(CAT_COLS + NUM_COLS + BOOL_COLS):
    raise ValueError('USED_FEATURES does not match the feature columns')

if not set(STANDARDISED_COLS) <= set(NUM_COLS):
    raise ValueError('STANDARDISED_COLS must be a subset of NUM_COLS')

# =========================== START - (for testing) ========================== #

if __name__ == '__main__':
    # Load the data
    input_file = 'data/transactions.csv'
    df = pd.read_csv(input_file)

    # Transform the data
    df = transform_df(df)

    # Save the processed data to a CSV file if someone would like to view the precessed data
    output_file = 'data/processed_transactions.csv'
    df.to_csv(output_file, index=False, mode='w')
