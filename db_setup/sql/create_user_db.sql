CREATE USER fraud_db_user WITH PASSWORD 'SECRET_PASSWORD'; -- Actual password removed for security reasons

CREATE DATABASE fraud_db;

GRANT ALL PRIVILEGES ON DATABASE fraud_db TO fraud_db_user;

ALTER DATABASE fraud_db OWNER TO fraud_db_user;

