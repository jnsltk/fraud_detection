import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine

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


def load_data(sample_size: int = 20000) -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)

    # Sample data from the database
    query = f'''
        SELECT setseed(0.37);
        SELECT * FROM detector_transaction ORDER BY RANDOM() LIMIT {sample_size};
    '''
    df = pd.read_sql(query, engine)

    engine.dispose()
    return df


def get_unique(column: str) -> list:
    engine = create_engine(DATABASE_URL)

    # Load data from the database
    query = f'''
        SELECT DISTINCT {column} FROM detector_transaction;
    '''
    df = pd.read_sql(query, engine)

    engine.dispose()
    return df[column].tolist()


def get_all() -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)

    # Load data from the database
    query = f'''
        SELECT * FROM detector_transaction;
    '''
    df = pd.read_sql(query, engine)

    engine.dispose()
    return df


# ---------------------------- RUN --------------------------- #

if __name__ == '__main__':
    # print(get_stats('amount'))
    load_data()
