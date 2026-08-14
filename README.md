# Mini Enterprise Data Platform

![Platform Architecture](docs/platform_architecture.png)

Architecture first.
Code second.

A compact, opinionated starter for building an internal data platform (ingestion, transformation, warehouse, governance, and BI) — runnable locally on Postgres, and deployable to Azure (Databricks + ADLS Gen2 Delta Lake) via Terraform.

Purpose
-------
Provide a minimal, reproducible foundation for collecting, transforming, and serving trusted data to downstream analytics and BI consumers, with two parallel implementations of the same Bronze/Silver/Gold pattern:

- **`ingestion/`** — Python + SQLAlchemy + Postgres. Simple, dependency-light, good for local dev or small workloads.
- **`spark/`** — PySpark + Delta Lake. The production-shaped path: same Bronze/Silver/Gold layering, but as a lakehouse pipeline designed to run as an Azure Databricks Job against ADLS Gen2.

Architecture (high level)
-------------------------
- **Ingestion**: lands raw data in the Bronze layer (`ingestion/` for Postgres, `spark/ingest_bronze.py` for Delta Lake).
- **Transformation**: incrementally cleans, deduplicates, and curates data into structured Silver tables.
- **Gold / warehouse**: dimensional star schema (`dim_customer`, `dim_supplier`, `dim_date`, `fact_orders`) built for downstream BI — see `warehouse/gold_star_schema.sql` (SQL DDL) and `spark/build_gold_star_schema.py` (Delta Lake).
- **BI**: `powerbi/` documents how to connect Power BI to the Gold layer (Power Query M + DAX measures) — either against Delta tables on ADLS Gen2 or the Postgres Gold schema.
- **Infrastructure**: `terraform/` provisions the Azure side — resource group, ADLS Gen2 storage (bronze/silver/gold containers), Azure Databricks workspace + scheduled Job, Postgres Flexible Server, Key Vault, and a Log Analytics workspace for monitoring.
- **CI/CD**: `.github/workflows/ci.yml` lints and tests the Python code, validates the Terraform, and runs the full Spark pipeline end-to-end as a smoke test on every push.
- **Monitoring**: `monitoring/` provides structured JSON logging for each pipeline stage, with an optional Azure Monitor / Application Insights export path and example KQL queries.
- **Governance**: dataset ownership, access-review cadence, DQ checks, and audit logging.

Where to look
-------------
- `ingestion/` — Postgres-based ingestion pipelines (Bronze → Silver), local dev via `docker-compose`-style Postgres.
- `spark/` — PySpark + Delta Lake pipeline (Bronze → Silver → Gold), runnable locally with `delta-spark` or as an Azure Databricks Job.
- `warehouse/` — SQL DDL for the Gold-layer star schema (Postgres/Synapse-compatible reference).
- `powerbi/` — Power BI connection guide (Power Query M, DAX measures, suggested report pages) for the Gold layer.
- `terraform/` — Azure infrastructure as code (storage, Databricks, Postgres, Key Vault, Log Analytics).
- `monitoring/` — structured logging helper + Azure Monitor/Log Analytics integration notes.
- `governance/` — policies and operational guidance (data ownership, GDPR, audits).
- `.github/workflows/` — CI: lint, unit tests, Terraform validation, and a pipeline smoke test.

Running it locally
-------------------
```bash
# Postgres path (ingestion/)
pip install -r ingestion/requirements.txt
python ingestion/ingest_customers.py
python ingestion/transform_customers_silver.py

# PySpark + Delta Lake path (spark/)
pip install -r spark/requirements-spark.txt
cd spark
python ingest_bronze.py
python transform_silver.py
python build_gold_star_schema.py
```

Deploying to Azure
-------------------
```bash
cd terraform
terraform init
terraform plan
terraform apply
```
This provisions the storage, Databricks workspace, and scheduled Job that runs the `spark/` pipeline in production. See `terraform/databricks_job.tf` for the job/task definitions.

Audience & intent
-----------------
This repository is intended for platform engineers, data stewards, and technical stakeholders who maintain or consume organizational data. It is a codebase and an operational reference — not a step‑by‑step tutorial.

Contributing
------------
- Open a feature branch and submit a PR describing the change and the dataset owner(s) affected.
- Major or sensitive changes (PII, retention, cross‑border transfers) must be reviewed by Compliance.

Support & governance
--------------------
Refer to `governance/data_governance_policy.md` for roles, SLAs, access‑review cadence, and GDPR guidance.
