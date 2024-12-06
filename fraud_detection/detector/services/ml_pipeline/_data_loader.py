import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text
from datetime import datetime

# ---------------- LOAD ENVIRONMENT VARIABLES ---------------- #

# Load environment variables from the .env file
load_dotenv()

# Get the values from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# ------------------------ METHODS ----------------------- #


# Note - Uses sqlalchemy for database connection so that can be run independently from Django
def load_data(sample_size: int = 20000, start: datetime = None, end: datetime = None) -> pd.DataFrame:
    ''' Randomly sample data from the database, throws ValueError if no data found '''

    engine = create_engine(DATABASE_URL)

    query = text('''
        SELECT setseed(0.42);

        SELECT * 
        FROM detector_transaction 
        WHERE (:start IS NULL OR version_date >= :start)
            AND (:end IS NULL OR version_date < :end)
        ORDER BY RANDOM()
        LIMIT :sample_size;
    ''')

    with engine.connect() as connection:
        df = pd.read_sql(query, connection, params={'sample_size': sample_size, 'start': start, 'end': end})

    if df.empty:
        raise ValueError('No data found')

    return df


# ---------------------------- RUN - (for testing) --------------------------- #

if __name__ == '__main__':
    data = load_data(999999, start=datetime(2024, 11, 3), end=datetime(2024, 12, 4))

    print(f'max: {data['version_date'].max()}\nmin: {data['version_date'].min(axis=0)}\n')
    print(data.head())
