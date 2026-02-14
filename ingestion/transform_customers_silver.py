"""
Silver layer transformation for customers.

Reads from bronze.customers_raw
Creates structured silver.customers_clean dimension table.
"""

from sqlalchemy import text
from db import engine


def main():
    with engine.begin() as conn:
    # Ensure silver schema exists
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver"))

        # Create silver table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS silver.customers_clean (
                customer_key SERIAL PRIMARY KEY,
                customer_id INT,
                customer_name TEXT NOT NULL,
                customer_email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Insert cleaned + deduplicated data
        conn.execute(text("""
            INSERT INTO silver.customers_clean (customer_id, customer_name, customer_email)
            SELECT
                id,
                LOWER(name),
                LOWER(email)
            FROM (
                SELECT *,
                    ROW_NUMBER() OVER (PARTITION BY email ORDER BY ingestion_timestamp DESC) as rn
                FROM bronze.customers_raw
            ) t
            WHERE rn = 1
            ON CONFLICT (customer_email) DO NOTHING
        """))
            
            
        print("Silver transformation completed successfully.")


if __name__ == "__main__":
    main()
