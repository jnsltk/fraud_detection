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
UNKNOWN_IN_TRAINING_PERCENTAGE = 0.1

USED_FEATURES = [
    'merchant_category',
    'amount',
    'currency',
    'country',
    'card_type',
    'card_present',
    'device',
    'channel',
    'distance_from_home',
    'transaction_hour',
    'weekend_transaction',
]

CAT_COLS = ['merchant_category', 'currency', 'country', 'card_type', 'device', 'channel']

NUM_COLS = ['amount', 'euros']

# =========================== SETUP EURO ========================== #

load_dotenv()

SKIP_EUR_DOWNLOAD = os.getenv('SKIP_EUR_DOWNLOAD') in ('TRUE', 'True', 'true', '1')

# sets up currency converter with recent data
if SKIP_EUR_DOWNLOAD:
    print('Skipping download of currency data')
else:
    urllib.request.urlretrieve(ECB_URL, 'data/eurofxref-hist.zip')

if not os.path.exists('data/eurofxref-hist.zip'):
    raise FileNotFoundError(
        'Could not download/find currency data, likely run from wrong PWD. Please run from the ml_pipeline directory')

c = CurrencyConverter('data/eurofxref-hist.zip', fallback_on_missing_rate=True, fallback_on_wrong_date=True)

# ====================== HELPER METHODS ====================== #


def _one_hot_encode(df: pd.DataFrame, col: str) -> pd.DataFrame:

    # loads all categories from the database, and adds unknown
    categories = data_loader.get_unique(col) + [UNKNOWN]
    encoder = OneHotEncoder(categories=[categories], drop='first', handle_unknown='infrequent_if_exist')

    encoder.fit(df[[col]])
    encoded = encoder.transform(df[[col]])
    encoded_df = pd.DataFrame(encoded.toarray(), columns=[f'{col}_{cat}' for cat in categories[1:]])
    df = pd.concat([df, encoded_df], axis=1)

    df.drop(columns=[col], inplace=True)
    return df


# ======================== PUBLIC METHODS ======================= #


def row_to_eur(row):
    ''' Takes row of [amount, timestamp, currency] and returns the amount in EUR '''

    if row[2] == 'NGN':  # note - the ECB does not have NGN for some reason
        return row[0] * 0.00057
    else:
        return c.convert(row[0], row[2], date=row[1])


# TODO - add end date
def transform_single(input: dict, stats: list[Stat]) -> pd.DataFrame:

    # ---------------- CREATE EURO CONVERSION DATA --------------- #

    timestamp = datetime.now()
    amount_cols = np.array([input['amount'], timestamp, input['currency']])  # used for euros conversion

    # ----------------- SELECT SUBSET OF COLUMNS ----------------- #

    df = pd.DataFrame([input])[USED_FEATURES].copy()

    # ------------------------ ADD COLUMNS ----------------------- #

    df['euros'] = np.array(row_to_eur(amount_cols))

    # ---------------------- MISSING VALUES ---------------------- #

    if df.select_dtypes(include=[np.number]).isnull().values.any():
        raise ValueError('Missing values in numerical columns')

    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna(UNKNOWN)  # Fill missing values for categorical features with 'unknown'

    # ---------------- ENCODE CATEGORICAL FEATURES --------------- #

    for col in CAT_COLS:
        df = _one_hot_encode(df, col)

    # ------------------- STANDARDISE FEATURES ------------------- #

    for col in NUM_COLS:
        df[col] = (df[col] - stats[col].mean) / stats[col].std

    return df


# TODO - add end date
def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    amount_cols = np.array(df[['amount', 'timestamp', 'currency']])  # used for euros conversion

    # ----------------- SELECT SUBSET OF COLUMNS ----------------- #

    df = df[USED_FEATURES + ['is_fraud']].copy()

    # ------------------------ ADD COLUMNS ----------------------- #

    df['euros'] = np.array([row_to_eur(row) for row in amount_cols])

    # ---------------------- MISSING VALUES ---------------------- #

    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].mean())  # Fill missing values for numerical features with mean

    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna(UNKNOWN)  # Fill missing values for categorical features with 'unknown'

    # ---------------- ENCODE CATEGORICAL FEATURES --------------- #

    unknowns_amt = int(UNKNOWN_IN_TRAINING_PERCENTAGE * len(df))

    for col in CAT_COLS:
        # sets some values to unknown to learn to handle unknown values
        unknowns_idxs = np.random.choice(df.index, unknowns_amt, replace=False)
        df.loc[unknowns_idxs, col] = UNKNOWN

        df = _one_hot_encode(df, col)

    # ------------------- STANDARDISE FEATURES ------------------- #

    df[NUM_COLS] = StandardScaler().fit_transform(df[NUM_COLS])

    # ----------------- OTHER ------------------- #

    df['is_fraud'] = df.pop('is_fraud')  # Move is_fraud to the last column

    return df


# ============================ RUN =========================== #

if __name__ == '__main__':
    # Load the data
    input_file = 'data/transactions.csv'
    df = pd.read_csv(input_file)

    # Transform the data
    df = transform_df(df)

    # Save the processed data to a CSV file if someone would like to view the precessed data
    output_file = 'data/processed_transactions.csv'
    df.to_csv(output_file, index=False, mode='w')
