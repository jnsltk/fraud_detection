<!---
Made by:  Janos
---->

# Database setup

The database is running on the VPS inside a docker container, which is using the official PostgreSQL image.
The database is exposed on port 5432 and is accessible from the VPS's IP address.

## How the database was setup

The database was setup using the following command:

```bash
docker run --name financial_fraud_db -e POSTGRES_PASSWORD=SUPER_SECRET_PASSWD -d -p 5432:5432 postgres
```

The database is accessible at the following address: `79.139.60.91:5432`

## User, database, and schema setup

The sql scripts that were used to create the user, database, and schema are located in the `sql` directory. The scripts are named `create_user_db.sql` 
and `create_schema.sql`.

To create the user and database, run the following command:

```bash
psql -U postgres -f sql/create_user_db.sql
```
> NOTE: The password in the script has been removed, so before running the script, make sure to replace the password with the correct one.

(DEPRECATED) After that run the following command to create the schema:

> ⚠️ This step is no longer needed, as the database is managed by the Django ORM.

```bash
psql -U fraud_db_user -d fraud_db -f create_schema.sql
```

In case you're trying to connect to the database from a remote machine, make sure to add the `--host` flag to the `psql` command, like so:

```bash
psql --host=HOST_IP -U postgres -f sql/create_user_db.sql
```

and 

```bash
psql --host=HOST_IP -U fraud_db_user -d fraud_db -f create_schema.sql
```
