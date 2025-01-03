'''
    Made by: Yingchao Ji
'''

import psycopg2
import csv
from psycopg2 import extras
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

def import_csv_to_postgres(csv_file, db_params, table_name):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
    # Open the CSV file
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip the header row of the CSV file
        
        # Create the INSERT SQL statement
        insert_query = f"INSERT INTO {table_name} ({', '.join(header)}) VALUES %s ON CONFLICT (transaction_id) DO NOTHING;"
        
        # Prepare the data to insert
        data_to_insert = [tuple(row) for row in reader]
        
        # Use psycopg2.extras.execute_values to efficiently insert data in bulk
        extras.execute_values(cursor, insert_query, data_to_insert)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Data has been successfully imported from {csv_file} into the {table_name} table.")

# Read database connection parameters from environment variables
db_params = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': os.getenv('DB_PORT')
}

# CSV file path and target table name
file_path = 'file_path'
table_name = 'transactions.transaction_details'

# Perform data import
import_csv_to_postgres(file_path, db_params, table_name)
