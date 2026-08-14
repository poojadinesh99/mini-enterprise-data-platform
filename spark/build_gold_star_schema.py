"""
Gold layer: dimensional (star schema) model built from Silver Delta tables,
designed to be consumed directly by Power BI (Import or DirectLake mode
against Delta tables on ADLS Gen2 / OneLake).

Produces:
    dim_customer      -- customer dimension
    dim_supplier       -- supplier dimension
    dim_date          -- date dimension
    fact_orders       -- order fact table (grain: 1 row per order)
"""
import logging

from config import GOLD_PATH, SILVER_PATH, get_spark
from pyspark.sql import functions as F

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def build_dim_customer(spark):
    silver = spark.read.format("delta").load(f"{SILVER_PATH}/customers_clean")
    dim = silver.select(
        F.monotonically_increasing_id().alias("customer_key"),
        "customer_email",
        "customer_name",
    )
    dim.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/dim_customer")
    log.info("Built dim_customer (%d rows)", dim.count())
    return dim


def build_dim_supplier(spark):
    silver = spark.read.format("delta").load(f"{SILVER_PATH}/orders_clean")
    dim = (
        silver.select("supplier_name")
        .distinct()
        .withColumn("supplier_key", F.monotonically_increasing_id())
        .select("supplier_key", "supplier_name")
    )
    dim.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/dim_supplier")
    log.info("Built dim_supplier (%d rows)", dim.count())
    return dim


def build_dim_date(spark):
    orders = spark.read.format("delta").load(f"{SILVER_PATH}/orders_clean")
    dates = (
        orders.select(F.col("order_date").alias("date"))
        .union(orders.select(F.col("delivery_date").alias("date")))
        .where(F.col("date").isNotNull())
        .distinct()
    )
    dim = dates.select(
        F.date_format("date", "yyyyMMdd").cast("int").alias("date_key"),
        "date",
        F.year("date").alias("year"),
        F.month("date").alias("month"),
        F.dayofmonth("date").alias("day"),
        F.date_format("date", "EEEE").alias("weekday_name"),
    )
    dim.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/dim_date")
    log.info("Built dim_date (%d rows)", dim.count())
    return dim


def build_fact_orders(spark, dim_customer, dim_supplier):
    orders = spark.read.format("delta").load(f"{SILVER_PATH}/orders_clean")

    fact = (
        orders.join(dim_customer, on="customer_email", how="left")
        .join(dim_supplier, on="supplier_name", how="left")
        .select(
            "order_id",
            "customer_key",
            "supplier_key",
            F.date_format("order_date", "yyyyMMdd").cast("int").alias("order_date_key"),
            F.date_format("delivery_date", "yyyyMMdd").cast("int").alias("delivery_date_key"),
            "product_category",
            "order_amount",
            "status",
            F.when(
                F.col("delivery_date").isNotNull() & F.col("order_date").isNotNull(),
                F.datediff("delivery_date", "order_date"),
            ).alias("fulfillment_days"),
        )
    )
    fact.write.format("delta").mode("overwrite").save(f"{GOLD_PATH}/fact_orders")
    log.info("Built fact_orders (%d rows)", fact.count())
    return fact


def main():
    spark = get_spark()
    try:
        dim_customer = build_dim_customer(spark)
        dim_supplier = build_dim_supplier(spark)
        build_dim_date(spark)
        build_fact_orders(spark, dim_customer, dim_supplier)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
