-- Gold layer star schema — SQL DDL reference (Synapse Serverless / Postgres
-- compatible). This mirrors the Delta tables produced by
-- spark/build_gold_star_schema.py, and is what Power BI's semantic model
-- is built on top of (see powerbi/README.md).
--
-- Grain of fact_orders: one row per order.

CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE gold.dim_customer (
    customer_key    BIGINT PRIMARY KEY,
    customer_email  TEXT NOT NULL UNIQUE,
    customer_name   TEXT NOT NULL
);

CREATE TABLE gold.dim_supplier (
    supplier_key    BIGINT PRIMARY KEY,
    supplier_name   TEXT NOT NULL UNIQUE
);

CREATE TABLE gold.dim_date (
    date_key        INT PRIMARY KEY,      -- yyyyMMdd
    date            DATE NOT NULL,
    year            INT NOT NULL,
    month           INT NOT NULL,
    day             INT NOT NULL,
    weekday_name    TEXT NOT NULL
);

CREATE TABLE gold.fact_orders (
    order_id            TEXT PRIMARY KEY,
    customer_key        BIGINT REFERENCES gold.dim_customer(customer_key),
    supplier_key        BIGINT REFERENCES gold.dim_supplier(supplier_key),
    order_date_key       INT REFERENCES gold.dim_date(date_key),
    delivery_date_key    INT REFERENCES gold.dim_date(date_key),
    product_category     TEXT,
    order_amount          NUMERIC(12, 2) NOT NULL,
    status                TEXT NOT NULL,
    fulfillment_days      INT
);

CREATE INDEX idx_fact_orders_customer ON gold.fact_orders (customer_key);
CREATE INDEX idx_fact_orders_supplier ON gold.fact_orders (supplier_key);
CREATE INDEX idx_fact_orders_order_date ON gold.fact_orders (order_date_key);
