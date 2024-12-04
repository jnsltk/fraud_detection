import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import numpy as np
import os
from currency_converter import CurrencyConverter, ECB_URL
import urllib.request  # for obtaining currency data
from dotenv import load_dotenv
import data_loader
from datetime import datetime
from dataclasses import dataclass

# ========================== CLASSES ========================= #


@dataclass
class Stat:
    mean: float
    std: float


# =========================== CONSTANTS ========================== #

UNKNOWN = 'unknown'
OTHER = 'other'
UNKNOWN_IN_TRAINING_PERCENTAGE = 0.1

USED_FEATURES = [
    'merchant_category', 'amount', 'currency', 'country', 'card_type', 'card_present', 'device', 'channel',
    'distance_from_home', 'transaction_hour', 'weekend_transaction', 'euros'
]

CAT_COLS = ['merchant_category', 'currency', 'country', 'card_type', 'device', 'channel']
NUM_COLS = ['amount', 'euros']

# =========================== SETUP ENV FLAGS ========================== #

load_dotenv()

SKIP_EUR_DOWNLOAD = os.getenv('SKIP_EUR_DOWNLOAD') in ('TRUE', 'True', 'true', '1')

# ======================== PUBLIC METHODS ======================= #


def row_to_eur(row, euro_mean: float | None) -> float:
    ''' Takes row of [amount, timestamp, currency] and returns the amount in EUR '''

    # note - the user is instructed to convert to EUR if the currency is not in the list
    if row[2] == OTHER:
        return row[0]

    # note - the ECB does not have NGN for some reason
    if row[2] == 'NGN':
        return row[0] * 0.00057

    # Defaults to euro_mean if the currency is not in the list
    elif not row[2] in c.currencies:
        return euro_mean

    # Converts the amount to euros
    else:
        return c.convert(row[0], row[2], date=row[1])


# TODO - add end date
def transform_single(input: dict, stats: list[Stat], categories_dict: dict[list]) -> pd.DataFrame:
    df = pd.DataFrame([input])

    # Adds euros column
    timestamp = datetime.now()
    amount_cols = np.array([input['amount'], timestamp, input['currency']])  # used for euros conversion
    df['euros'] = np.array(row_to_eur(amount_cols, stats['euros'].mean))

    # Selects feature subset & sorts columns
    df = df[USED_FEATURES].copy()

    # Handles missing numerical values
    if df.select_dtypes(include=[np.number]).isnull().values.any():
        raise ValueError('Missing values in numerical columns')

    # Fills missing categorical values with UNKNOWN
    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna(UNKNOWN)

    # One-hot encodes categorical features
    for col in CAT_COLS:
        if df[col].values[0] not in categories_dict[col]:
            df[col].values[0] = UNKNOWN

        df = _one_hot_encode(df, col, categories_dict[col])

    # Standardises numerical features
    for col in NUM_COLS:
        df[col] = (df[col] - stats[col].mean) / stats[col].std

    # Returns the transformed dataframe
    return df


# TODO - add end date
def transform_df(df: pd.DataFrame) -> pd.DataFrame:

    # Adds euros column
    amount_cols = np.array(df[['amount', 'timestamp', 'currency']])  # used for euros conversion
    df['euros'] = np.array([row_to_eur(row, None) for row in amount_cols])

    # Selects feature subset & sorts columns
    df = df[USED_FEATURES + ['is_fraud']].copy()

    # Fills missing values for numerical features with mean
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].mean())

    # Fill missing values for categorical features with UNKNOWN
    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna(UNKNOWN)

    # One-hot encodes categorical features
    unknowns_amt = int(UNKNOWN_IN_TRAINING_PERCENTAGE * len(df))
    for col in CAT_COLS:

        # Sets some values to unknown to learn to handle unknown values
        unknowns_idxs = np.random.choice(df.index, unknowns_amt, replace=False)
        df.loc[unknowns_idxs, col] = UNKNOWN

        # Loads all unique categories from the database, and adds unknown
        categories = data_loader.get_unique(col, CAT_COLS) + [UNKNOWN]

        # One-hot encodes column
        df = _one_hot_encode(df, col, categories)

    # Standardises numerical features
    df[NUM_COLS] = StandardScaler().fit_transform(df[NUM_COLS])

    # Move is_fraud to the last column
    df['is_fraud'] = df.pop('is_fraud')

    # Returns the transformed dataframe
    return df


# ====================== PRIVATE METHODS ====================== #


def _setup_currency_converter():
    if SKIP_EUR_DOWNLOAD:
        print('Skipping download of currency data')
    else:
        urllib.request.urlretrieve(ECB_URL, 'data/eurofxref-hist.zip')

    if not os.path.exists('data/eurofxref-hist.zip'):
        raise FileNotFoundError(
            'Could not download/find currency data, likely run from wrong PWD. Please run from the ml_pipeline directory'
        )

    return CurrencyConverter('data/eurofxref-hist.zip', fallback_on_missing_rate=True, fallback_on_wrong_date=True)


def _one_hot_encode(df: pd.DataFrame, col: str, categories: list) -> pd.DataFrame:

    # Creates and fits encoder with the categories
    encoder = OneHotEncoder(categories=[categories], handle_unknown='error')
    encoder.fit(df[[col]])

    # Encodes the column
    encoded = encoder.transform(df[[col]])
    columns = [f'{col}_{cat}' for cat in categories]
    encoded_df = pd.DataFrame(encoded.toarray(), columns=columns)

    # Replaces original column with encoded columns
    df = pd.concat([df, encoded_df], axis=1)
    df.drop(columns=[col], inplace=True)

    # Returns the transformed dataframe
    return df


# ============================ OTHER =========================== #

c = _setup_currency_converter()

if __name__ == '__main__':
    # Load the data
    input_file = 'data/transactions.csv'
    df = pd.read_csv(input_file)

    # Transform the data
    df = transform_df(df)

    # Save the processed data to a CSV file if someone would like to view the precessed data
    output_file = 'data/processed_transactions.csv'
    df.to_csv(output_file, index=False, mode='w')
