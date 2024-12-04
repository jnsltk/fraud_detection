import pandas as pd
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text

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
    ''' Randomly sample data from the database '''

    engine = create_engine(DATABASE_URL)

    query = text('''
        SELECT setseed(0.37);
        SELECT * FROM detector_transaction ORDER BY RANDOM() LIMIT :sample_size;
    ''')

    with engine.connect() as connection:
        df = pd.read_sql(query, connection, params={'sample_size': sample_size})

    return df


def get_unique(column: str, const_valid_list: list) -> list:
    ''' 
        NOTE - The list should contain all possible values for the column parameter. 
            It is used to limit possible inputs against SQL injection.
    '''

    # Input validation
    if column not in const_valid_list:
        raise ValueError(f'Invalid column name {column}')

    # Setup connection and query
    engine = create_engine(DATABASE_URL)
    query = f'''
        SELECT DISTINCT {column} FROM detector_transaction;
    '''

    # Execute query
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    # Return the list of unique values
    return df[column].tolist()


def get_all() -> pd.DataFrame:
    engine = create_engine(DATABASE_URL)

    query = text('''
        SELECT * FROM detector_transaction;
    ''')

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df


# ---------------------------- RUN --------------------------- #

if __name__ == '__main__':
    data = load_data()
    print(data.head())
