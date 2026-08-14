"""
Bronze layer ingestion (PySpark + Delta Lake).

Mirrors the existing ingestion/ingest_customers.py (Postgres) pattern, but
lands raw data as Delta tables instead — this is the path used when the
platform runs on Azure Databricks against ADLS Gen2 rather than local Postgres.

Run locally:
    python spark/ingest_bronze.py

On Databricks: schedule this as a Job task (see terraform/databricks_job.tf
for the job/cluster definition), with DELTA_ROOT pointing at the ADLS mount.
"""
import logging
import os

from config import BRONZE_PATH, get_spark
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    StringType,
    StructField,
    StructType,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

CUSTOMERS_CSV = os.path.join(DATA_DIR, "..", "ingestion", "data", "customers.csv")
ORDERS_CSV = os.path.join(DATA_DIR, "orders_sample.csv")

ORDERS_SCHEMA = StructType(
    [
        StructField("order_id", StringType(), False),
        StructField("customer_email", StringType(), False),
        StructField("supplier_name", StringType(), True),
        StructField("product_category", StringType(), True),
        StructField("order_amount", DoubleType(), True),
        StructField("order_date", StringType(), True),
        StructField("delivery_date", StringType(), True),
        StructField("status", StringType(), True),
    ]
)


def ingest_customers(spark):
    df = (
        spark.read.option("header", True)
        .csv(CUSTOMERS_CSV)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.lit("customers.csv"))
    )
    path = os.path.join(BRONZE_PATH, "customers_raw")
    df.write.format("delta").mode("overwrite").save(path)
    log.info("Wrote %d customer rows to bronze Delta table at %s", df.count(), path)


def ingest_orders(spark):
    df = (
        spark.read.option("header", True)
        .schema(ORDERS_SCHEMA)
        .csv(ORDERS_CSV)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.lit("orders_sample.csv"))
    )
    path = os.path.join(BRONZE_PATH, "orders_raw")
    df.write.format("delta").mode("overwrite").save(path)
    log.info("Wrote %d order rows to bronze Delta table at %s", df.count(), path)


def main():
    spark = get_spark()
    try:
        ingest_customers(spark)
        ingest_orders(spark)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
