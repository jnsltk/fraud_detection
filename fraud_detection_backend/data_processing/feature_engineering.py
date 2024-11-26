import pandas as pd
from sklearn.preprocessing import StandardScaler
from sqlalchemy import create_engine
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the values from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Construct the DATABASE_URL
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

# Load data from the database
query = "SELECT * FROM detector_transaction LIMIT 10"
df = pd.read_sql(query, engine)

# Handle missing values
for col in df.select_dtypes(include=[np.number]).columns:
    df[col] = df[col].fillna(df[col].mean())  # Fill missing values for numerical features with mean
for col in df.select_dtypes(include=[object]).columns:
    df[col] = df[col].fillna('Unknown')  # Fill missing values for categorical features with 'Unknown'

# Process timestamp
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['transaction_hour'] = df['timestamp'].dt.hour  # Extract hour from timestamp
df['transaction_dayofweek'] = df['timestamp'].dt.dayofweek  # Extract day of week from timestamp
df['transaction_month'] = df['timestamp'].dt.month  # Extract month from timestamp

# Encode categorical features
categorical_cols = ['merchant_category', 'merchant_type', 'merchant', 'currency', 'country', 'city', 'city_size', 'card_type', 'device', 'channel']
df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)  # One-hot encode categorical features

# Standardize numerical features
scaler = StandardScaler()
numeric_cols = ['amount', 'v_num_transactions', 'v_total_amount', 'v_unique_merchants', 'v_unique_countries', 'v_total_amount', 'v_max_single_amount']
df[numeric_cols] = scaler.fit_transform(df[numeric_cols])  # Apply StandardScaler to numerical columns

# Process high-risk merchants
df['high_risk_merchant'] = df['high_risk_merchant'].astype(int)  # Convert to integer

# Drop unnecessary columns. We can adjust features that need to be dropped
df = df.drop(columns=['transaction_id', 'customer_id', 'timestamp', 'card_number', 'device_fingerprint', 'ip_address'])  # Drop columns not needed for modeling

# Handle target variable
X = df.drop(columns=['is_fraud'])  # Features for the model
y = df['is_fraud']  # Target variable (fraud or not)


# Save the processed data to a CSV file if someone would like to view the precessed data 
# output_file = 'file_path/processed_transactions.csv'
# df.to_csv(output_file, index=False, mode='w')