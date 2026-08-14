# Deploys the spark/ pipeline (ingest_bronze -> transform_silver ->
# build_gold_star_schema) as a scheduled Databricks Job, so the "local dev"
# scripts in spark/ run unchanged in production against the ADLS Gen2
# containers provisioned in main.tf.

resource "databricks_cluster" "etl_cluster" {
  cluster_name            = "etl-cluster-${var.environment}"
  spark_version           = "15.4.x-scala2.12"
  node_type_id             = "Standard_DS3_v2"
  autotermination_minutes = 20
  num_workers             = 1

  spark_conf = {
    "spark.databricks.delta.preview.enabled" = "true"
  }
}

resource "databricks_job" "etl_pipeline" {
  name = "mini-enterprise-etl-${var.environment}"

  job_cluster {
    job_cluster_key = "etl"
    new_cluster {
      spark_version = "15.4.x-scala2.12"
      node_type_id  = "Standard_DS3_v2"
      num_workers   = 1
    }
  }

  task {
    task_key = "ingest_bronze"
    job_cluster_key = "etl"
    spark_python_task {
      python_file = "/Repos/mini-enterprise-data-platform/spark/ingest_bronze.py"
    }
  }

  task {
    task_key = "transform_silver"
    job_cluster_key = "etl"
    depends_on {
      task_key = "ingest_bronze"
    }
    spark_python_task {
      python_file = "/Repos/mini-enterprise-data-platform/spark/transform_silver.py"
    }
  }

  task {
    task_key = "build_gold_star_schema"
    job_cluster_key = "etl"
    depends_on {
      task_key = "transform_silver"
    }
    spark_python_task {
      python_file = "/Repos/mini-enterprise-data-platform/spark/build_gold_star_schema.py"
    }
  }

  schedule {
    quartz_cron_expression = "0 0 3 * * ?" # daily at 03:00
    timezone_id             = "Europe/Berlin"
  }
}
