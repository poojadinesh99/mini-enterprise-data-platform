# Monitoring — Azure Monitor / Log Analytics

`logging_config.py` provides structured JSON logging for every pipeline
stage (Bronze ingest, Silver transform, Gold build). When
`APPLICATIONINSIGHTS_CONNECTION_STRING` is set — e.g. as a Databricks
cluster environment variable pointing at the `azurerm_log_analytics_workspace`
from `terraform/main.tf` — logs are shipped to Azure Monitor via the
OpenCensus exporter; otherwise it just prints structured JSON to stdout
(picked up by the CI job logs / Databricks driver logs either way).

## Usage in a pipeline script

```python
from monitoring.logging_config import get_pipeline_logger, log_stage_duration

logger = get_pipeline_logger(__name__)

with log_stage_duration(logger, "ingest_bronze"):
    ingest_customers(spark)
    ingest_orders(spark)
```

## Example KQL queries (Log Analytics)

Pipeline stage failures in the last 24h:

```kql
AppTraces
| where TimeGenerated > ago(24h)
| where Properties.pipeline_stage != ""
| where SeverityLevel >= 3
| project TimeGenerated, Message, Properties.pipeline_stage
| order by TimeGenerated desc
```

Average stage duration trend:

```kql
AppTraces
| where Message startswith "Completed stage"
| extend duration_s = extract(@"in ([\d.]+)s", 1, Message, typeof(real))
| summarize avg(duration_s) by bin(TimeGenerated, 1h), tostring(Properties.pipeline_stage)
```

## What this does *not* cover

This is log-based monitoring, not full observability — there's no metrics
dashboard or alerting rule provisioned in Terraform yet. If the role needs
alerting (e.g. "page on 3 consecutive pipeline failures"), the next step
would be an `azurerm_monitor_scheduled_query_rules_alert_v2` resource
wired to the KQL query above — not included here since it wasn't part of
the original scope.
