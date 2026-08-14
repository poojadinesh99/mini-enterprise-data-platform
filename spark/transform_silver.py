"""
Silver layer transformation (PySpark + Delta Lake).

Reads bronze Delta tables, applies cleaning/deduplication/type-normalization,
writes structured Delta tables to the Silver layer with MERGE (upsert)
semantics so re-runs are idempotent.
"""
import logging

from config import BRONZE_PATH, SILVER_PATH, get_spark
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from pyspark.sql.window import Window

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def transform_customers(spark):
    bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/customers_raw")

    w = Window.partitionBy(F.lower(F.col("email"))).orderBy(F.col("_ingested_at").desc())
    silver = (
        bronze.withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .withColumn("customer_email", F.lower(F.col("email")))
        .withColumn("customer_name", F.lower(F.col("name")))
        .filter(F.col("customer_email").rlike(r"^[^@]+@[^@]+\.[^@]+$"))
        .select("customer_email", "customer_name", "_ingested_at")
    )

    path = f"{SILVER_PATH}/customers_clean"
    if DeltaTable.isDeltaTable(spark, path):
        target = DeltaTable.forPath(spark, path)
        (
            target.alias("t")
            .merge(silver.alias("s"), "t.customer_email = s.customer_email")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        silver.write.format("delta").mode("overwrite").save(path)
    log.info("Silver customers_clean upserted (%d rows evaluated)", silver.count())


def transform_orders(spark):
    bronze = spark.read.format("delta").load(f"{BRONZE_PATH}/orders_raw")

    silver = (
        bronze.withColumn("customer_email", F.lower(F.col("customer_email")))
        .withColumn("order_date", F.to_date("order_date"))
        .withColumn("delivery_date", F.to_date("delivery_date"))
        .withColumn("order_amount", F.col("order_amount").cast("double"))
        .filter(F.col("order_amount").isNotNull())
        .filter(F.col("status").isin("DELIVERED", "PENDING", "CANCELLED"))
        .dropDuplicates(["order_id"])
    )

    path = f"{SILVER_PATH}/orders_clean"
    if DeltaTable.isDeltaTable(spark, path):
        target = DeltaTable.forPath(spark, path)
        (
            target.alias("t")
            .merge(silver.alias("s"), "t.order_id = s.order_id")
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        silver.write.format("delta").mode("overwrite").save(path)
    log.info("Silver orders_clean upserted (%d rows evaluated)", silver.count())


def main():
    spark = get_spark()
    try:
        transform_customers(spark)
        transform_orders(spark)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
