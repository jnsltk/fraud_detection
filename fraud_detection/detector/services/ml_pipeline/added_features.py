import urllib.request
from currency_converter import CurrencyConverter, ECB_URL
from dotenv import load_dotenv
import os

# ------------------------- CONSTANTS ------------------------ #

EUR_PATH_1 = 'data/eurofxref-hist.zip'
EUR_PATH_2 = 'detector/services/ml_pipeline/data/eurofxref-hist.csv'

OTHER = 'other'

# -------------------- SETUP FEATURE FLAGS ------------------- #

load_dotenv()

SKIP_EUR_DOWNLOAD = os.getenv('SKIP_EUR_DOWNLOAD') in ('TRUE', 'True', 'true', '1')

# ---------------------- PUBLIC METHODS ---------------------- #


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


# --------------------------- SETUP -------------------------- #


def _setup_currency_converter():
    data_path = None

    if os.path.exists(EUR_PATH_1):
        data_path = EUR_PATH_1
    elif os.path.exists(EUR_PATH_2):
        data_path = EUR_PATH_2

    if data_path is None:
        raise FileNotFoundError('Could not find currency data')

    if SKIP_EUR_DOWNLOAD:
        print('Note - Skipping download of currency data')
    else:
        urllib.request.urlretrieve(ECB_URL, data_path)

    if not os.path.exists(data_path):
        cur_path = os.path.abspath(os.getcwd())

        raise FileNotFoundError(f'Could not download/find currency data. Current path is {cur_path}')

    return CurrencyConverter(data_path, fallback_on_missing_rate=True, fallback_on_wrong_date=True)


c = _setup_currency_converter()
