-- Made by Janos

-- Create schema
CREATE SCHEMA IF NOT EXISTS transactions;

-- Create table
CREATE TABLE IF NOT EXISTS transactions.transaction_details (
    transaction_id VARCHAR(20) PRIMARY KEY, 
    customer_id VARCHAR(20) NOT NULL,
    card_number VARCHAR(20) NOT NULL, 
    timestamp TIMESTAMP NOT NULL,
    merchant_category VARCHAR(50),
    merchant_type VARCHAR(50),
    merchant VARCHAR(100),
    amount NUMERIC(15, 2), 
    currency CHAR(3), 
    country VARCHAR(50),
    city VARCHAR(100),
    city_size VARCHAR(20),
    card_type VARCHAR(50),
    card_present BOOLEAN,
    device VARCHAR(50),
    channel VARCHAR(20),
    device_fingerprint VARCHAR(100),
    ip_address INET, 
    distance_from_home BOOLEAN,
    high_risk_merchant BOOLEAN,
    transaction_hour SMALLINT CHECK(transaction_hour BETWEEN 0 AND 23),
    weekend_transaction BOOLEAN,
    velocity_last_hour JSONB, 
    is_fraud BOOLEAN
);

