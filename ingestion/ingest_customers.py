"""
Enterprise-style Bronze ingestion script for customers.
Creates bronze.customers_raw and inserts raw rows.
"""

from sqlalchemy import text
import os
import csv

from db import engine

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "customers.csv")

SAMPLE_ROWS = [
    {"name": "Alice Example", "email": "alice@example.com"},
    {"name": "Bob Example", "email": "bob@example.com"},
]


def read_csv(path: str):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append({
                "name": r.get("name"),
                "email": r.get("email"),
            })
    return rows


def main():
    rows = read_csv(DATA_FILE) or SAMPLE_ROWS

    with engine.begin() as conn:

        # Ensure bronze schema exists
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS bronze"))


        # Create raw table in bronze layer
        conn.execute(text(
            """
            CREATE TABLE IF NOT EXISTS bronze.customers_raw (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT UNIQUE,
                ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            """
        ))

        conn.execute(text("TRUNCATE TABLE bronze.customers_raw"))

        # Insert rows one-by-one so we can reliably observe RETURNING values
        inserted_count = 0
        insert_stmt = text(
            """
            INSERT INTO bronze.customers_raw (name, email)
            VALUES (:name, :email)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
            """
        )

        for r in rows:
            res = conn.execute(insert_stmt, r)
            if res.fetchone() is not None:
                inserted_count += 1
    print(f"Inserted {inserted_count} new row(s) into bronze.customers_raw")

    


if __name__ == "__main__":
    main()
