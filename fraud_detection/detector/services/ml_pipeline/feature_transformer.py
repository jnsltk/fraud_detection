import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np
import os
from currency_converter import CurrencyConverter, ECB_URL
import urllib.request  # for obtaining currency data
from dotenv import load_dotenv

# =========================== SETUP ========================== #

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


def to_eur(row):
    ''' Takes row of [amount, timestamp, currency] and returns the amount in EUR '''

    if row[2] == 'NGN':  # note - the ECB does not have NGN for some reason
        return row[0] * 0.00057
    else:
        return c.convert(row[0], row[2], date=row[1])


# ======================== MAIN METHOD ======================= #


def transform(df) -> pd.DataFrame:
    amount_cols = np.array(df[['amount', 'timestamp', 'currency']])  # used for euros conversion

    # ----------------- SELECT SUBSET OF COLUMNS ----------------- #

    df = df[[
        'merchant_category', 'amount', 'currency', 'card_present', 'device', 'channel', 'distance_from_home',
        'transaction_hour', 'weekend_transaction', 'is_fraud'
    ]].copy()

    # ------------------------ ADD COLUMNS ----------------------- #

    euros = np.array([to_eur(row) for row in amount_cols])
    df['euros'] = euros

    # ---------------------- MISSING VALUES ---------------------- #

    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].mean())  # Fill missing values for numerical features with mean

    for col in df.select_dtypes(include=[object]).columns:
        df[col] = df[col].fillna('Unknown')  # Fill missing values for categorical features with 'Unknown'

    # ---------------- ENCODE CATEGORICAL FEATURES --------------- #

    cat_cols = np.array([
        'merchant_category', 'merchant_type', 'merchant', 'currency', 'country', 'city', 'city_size', 'card_type',
        'device', 'channel'
    ])
    chosen_cat_cols = np.intersect1d(cat_cols, np.array(df.columns))

    # One-hot encode categorical features
    df = pd.get_dummies(df, columns=chosen_cat_cols, drop_first=True, prefix=chosen_cat_cols)

    # ------------------- STANDARDISE FEATURES ------------------- #

    scaler = StandardScaler()
    numeric_cols = [
        'amount', 'v_num_transactions', 'v_total_amount', 'v_unique_merchants', 'v_unique_countries', 'v_total_amount',
        'v_max_single_amount', 'euros'
    ]
    chosen_numeric_cols = np.intersect1d(numeric_cols, np.array(df.columns))

    # Apply StandardScaler to numerical columns
    df[chosen_numeric_cols] = scaler.fit_transform(df[chosen_numeric_cols])

    # -------------------- CONVERT DATA TYPES -------------------- #

    # Process high-risk merchants
    #df['high_risk_merchant'] = df['high_risk_merchant'].astype(int)  # Convert to integer

    # Convert the binary feature to Boolean type
    binary_cols = [col for col in df.columns if df[col].nunique() == 2 and sorted(df[col].unique()) == [0, 1]]
    df[binary_cols] = df[binary_cols].astype(bool)

    # ----------------- OTHER ------------------- #

    df['is_fraud'] = df.pop('is_fraud')  # Move is_fraud to the last column

    # print(df.columns)

    return df


# ============================ RUN =========================== #

if __name__ == '__main__':
    # Load the data
    input_file = 'data/transactions.csv'
    df = pd.read_csv(input_file)

    # Transform the data
    df = transform(df)

    # Save the processed data to a CSV file if someone would like to view the precessed data
    output_file = 'data/processed_transactions.csv'
    df.to_csv(output_file, index=False, mode='w')

# TODO!
enabled_features = [
    'merchant_category', 'merchant_type', 'country', 'currency', 'city_size', 'amount', 'distance_from_home',
    'transaction_hour', 'weekend_transaction', 'high_risk_merchant', 'card_type'
]
