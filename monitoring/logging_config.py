"""
Structured JSON logging for the pipeline, designed to ship to Azure Monitor /
Log Analytics via the OpenCensus Azure Monitor exporter when
APPLICATIONINSIGHTS_CONNECTION_STRING is set (e.g. as an Azure Databricks
cluster env var, wired to the Log Analytics workspace from
terraform/main.tf). Falls back to plain console JSON logging locally/in CI.
"""
import json
import logging
import os
import sys
import time


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pipeline_stage": getattr(record, "pipeline_stage", None),
            "run_id": os.getenv("RUN_ID"),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def get_pipeline_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # avoid duplicate handlers on repeated calls

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    conn_str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if conn_str:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler

            azure_handler = AzureLogHandler(connection_string=conn_str)
            logger.addHandler(azure_handler)
        except ImportError:
            logger.warning(
                "APPLICATIONINSIGHTS_CONNECTION_STRING set but opencensus-ext-azure "
                "is not installed — add it to spark/requirements-spark.txt to enable "
                "Azure Monitor export."
            )
    return logger


def log_stage_duration(logger: logging.Logger, stage: str):
    """Context manager that logs start/end + duration of a pipeline stage,
    tagged with `pipeline_stage` so it's filterable in Log Analytics/KQL."""

    class _Timer:
        def __enter__(self):
            self.start = time.time()
            logger.info(f"Starting stage: {stage}", extra={"pipeline_stage": stage})
            return self

        def __exit__(self, exc_type, exc, tb):
            duration = round(time.time() - self.start, 2)
            if exc_type:
                logger.error(
                    f"Stage {stage} failed after {duration}s: {exc}",
                    extra={"pipeline_stage": stage},
                )
            else:
                logger.info(
                    f"Completed stage: {stage} in {duration}s",
                    extra={"pipeline_stage": stage},
                )

    return _Timer()
