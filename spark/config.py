"""
Spark session + Delta Lake configuration.

Local dev: writes Delta tables to ./data/delta (or $DELTA_ROOT).
Databricks / Azure: set DELTA_ROOT to an ADLS Gen2 path, e.g.
    abfss://gold@<storage_account>.dfs.core.windows.net/enterprise-platform
and this module works unchanged when deployed as a Databricks Job
(cluster already has delta-spark preinstalled via the Databricks Runtime).
"""
import os

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

DELTA_ROOT = os.getenv("DELTA_ROOT", os.path.join(os.path.dirname(__file__), "..", "data", "delta"))

BRONZE_PATH = os.path.join(DELTA_ROOT, "bronze")
SILVER_PATH = os.path.join(DELTA_ROOT, "silver")
GOLD_PATH = os.path.join(DELTA_ROOT, "gold")


def get_spark(app_name: str = "mini-enterprise-data-platform") -> SparkSession:
    """
    Returns a SparkSession configured for Delta Lake.

    On Databricks, SparkSession is already provided by the runtime and
    already has Delta configured — this builder pattern is only needed
    for local/dev execution (e.g. running via `spark-submit` or pytest).
    """
    builder = (
        SparkSession.builder.appName(app_name)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .master(os.getenv("SPARK_MASTER", "local[*]"))
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()
