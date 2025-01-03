'''
    Made by: Henrik Lagrosen
'''

import urllib.request
from currency_converter import CurrencyConverter, ECB_URL
from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np

# ------------------------- CONSTANTS ------------------------ #

EUR_DIR_1 = 'data'
EUR_DIR_2 = 'detector/services/ml_pipeline/data'
EUR_FILE = 'eurofxref-hist.zip'

OTHER = 'other'

# -------------------- SETUP FEATURE FLAGS ------------------- #

load_dotenv()

SKIP_EUR_DOWNLOAD = os.getenv('SKIP_EUR_DOWNLOAD') in ('TRUE', 'True', 'true', '1')

# ---------------------- CURRENCY METHODS ---------------------- #


def has_currency(code: str) -> bool:
    return (code == 'NGN') or (code in c.currencies)


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


# ---------------------- HOUR FUNCTIONS ---------------------- #


def add_hour_trig_cols(df: pd.DataFrame) -> pd.DataFrame:
    ''' Adds sin and cos columns for the transaction hour which are more learnable '''

    df['hour_sin'] = np.sin(2 * np.pi * df['transaction_hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['transaction_hour'] / 24)

    if df['hour_cos'].isnull().values.any() or df['hour_sin'].isnull().values.any():
        raise ValueError('Missing values in hour_sin or hour_cos')


# --------------------------- SETUP -------------------------- #


def _setup_currency_converter():
    data_path = None

    # Gets right path for currency data
    if os.path.exists(EUR_DIR_1):
        data_path = os.path.join(EUR_DIR_1, EUR_FILE)
    elif os.path.exists(EUR_DIR_2):
        data_path = os.path.join(EUR_DIR_2, EUR_FILE)
    else:
        raise FileNotFoundError('Could not find currency data folder')

    if SKIP_EUR_DOWNLOAD:
        print('Note - Skipping download of currency data (using previously downloaded data)')
    else:
        urllib.request.urlretrieve(ECB_URL, data_path)

    if not os.path.exists(data_path):
        cur_path = os.path.abspath(os.getcwd())

        raise FileNotFoundError(f'Could not download/find currency data. DEBUG: current path is {cur_path}')

    return CurrencyConverter(data_path, fallback_on_missing_rate=True, fallback_on_wrong_date=True)


c = _setup_currency_converter()
