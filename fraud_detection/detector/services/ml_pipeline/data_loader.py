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

# ------------------------ MAIN METHOD ----------------------- #


def load_data() -> pd.DataFrame:
    # Construct the DATABASE_URL
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(DATABASE_URL)

    # Load data from the database
    query = "SELECT * FROM detector_transaction"
    df = pd.read_sql(query, engine)

    return df


# ---------------------------- RUN --------------------------- #

if __name__ == '__main__':
    load_data()
