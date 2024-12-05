import pandas as pd
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import os
from currency_converter import CurrencyConverter, ECB_URL
import urllib.request  # for obtaining currency data
from dotenv import load_dotenv
from datetime import datetime
from dataclasses import dataclass

# ========================== CLASSES ========================= #


@dataclass
class TransformSingleResult:
    df: pd.DataFrame
    euros: float


@dataclass
class TransformDfResult:
    df: pd.DataFrame
    categories: dict[str, list]
    stats: dict[str, dict[str, float]]


# =========================== CONSTANTS ========================== #

UNKNOWN = 'unknown'
OTHER = 'other'
UNKNOWN_IN_TRAINING_PERCENTAGE = 0.1

USED_FEATURES = [
    'merchant_category', 'amount', 'currency', 'country', 'card_type', 'card_present', 'device', 'channel',
    'distance_from_home', 'transaction_hour', 'weekend_transaction', 'euros'
]

CAT_COLS = ['merchant_category', 'currency', 'country', 'card_type', 'device', 'channel']
NUM_COLS = ['amount', 'transaction_hour', 'euros']
BOOL_COLS = ['card_present', 'distance_from_home', 'weekend_transaction']

# =========================== SETUP ENV FLAGS ========================== #

load_dotenv()

SKIP_EUR_DOWNLOAD = os.getenv('SKIP_EUR_DOWNLOAD') in ('TRUE', 'True', 'true', '1')

# ======================== PUBLIC METHODS ======================= #


# Note - This should ideally happen during data collection,
# but is done here due to technical debt
def row_to_eur(row, euro_mean: float | None) -> float:
    ''' Takes row of [amount, timestamp, currency] and returns the amount in EUR '''

    # Note - The user is instructed to convert to EUR if the currency is not in the list
    if row[2] == OTHER:
        return row[0]

    # Note - The ecb does not have ngn for some reason
    if row[2] == 'NGN':
        return row[0] * 0.00057

    # Defaults to euro_mean if the currency is not in the list
    elif not row[2] in c.currencies:
        return euro_mean

    # Converts the amount to euros
    else:
        return c.convert(row[0], row[2], date=row[1])


def transform_single(input: dict, col_data: dict[str, any]) -> TransformSingleResult:
    ''' Throws ValueError if the input is invalid '''

    df = pd.DataFrame([input])

    # Adds euros column
    amount_cols = [input['amount'], datetime.now(), input['currency']]
    euro = row_to_eur(amount_cols, euro_mean=col_data['euros']['mean'])
    df['euros'] = [euro]

    # Selects feature subset & Sorts columns
    df = df[USED_FEATURES].copy()

    # Handles missing numerical values
    if df.select_dtypes(include=[np.number]).isnull().values.any():
        raise ValueError('Missing values in numerical columns')

    # One-hot encodes categorical features
    for col in CAT_COLS:
        df = _one_hot_encode(df, col, col_data[col])

    # Standardises numerical features
    for col in NUM_COLS:
        df[col] = (df[col] - col_data[col]['mean']) / col_data[col]['std']

    # Returns the transformed dataframe
    return TransformSingleResult(df, euros=euro)


# Note - col_data will be passed if model is already trained, and the function is used for SHAP
def transform_df(df: pd.DataFrame, col_data: dict[str:any] = None) -> TransformDfResult:

    # Adds euros column, inspired by ChatGPT
    df['euros'] = [
        row_to_eur(row, euro_mean=None) for row in df[['amount', 'timestamp', 'currency']].itertuples(index=False)
    ]

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
    for col in NUM_COLS:
        # Note - ses pre-calculated, more accurate stats for mean and std if available
        stats[col] = {'mean': df[col].mean(), 'std': df[col].std()} if col_data is None else col_data[col]

        df[col] = (df[col] - stats[col]['mean']) / stats[col]['std']

    # Move is_fraud to the last column
    df['is_fraud'] = df.pop('is_fraud')

    # Returns the result of the transformation
    return TransformDfResult(df, categories, stats)


# ====================== PRIVATE METHODS ====================== #


def _setup_currency_converter():
    if SKIP_EUR_DOWNLOAD:
        print('Note - Skipping download of currency data')
    else:
        urllib.request.urlretrieve(ECB_URL, 'data/eurofxref-hist.zip')

    if not os.path.exists('data/eurofxref-hist.zip'):
        raise FileNotFoundError(
            'Could not download/find currency data, likely run from wrong PWD. Please run from the ml_pipeline directory'
        )

    return CurrencyConverter('data/eurofxref-hist.zip', fallback_on_missing_rate=True, fallback_on_wrong_date=True)


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


# ============================ OTHER =========================== #

c = _setup_currency_converter()

if set(USED_FEATURES) != set(CAT_COLS + NUM_COLS + BOOL_COLS):
    raise ValueError('USED_FEATURES does not match the feature columns')

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
