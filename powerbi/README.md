# Power BI — Gold Layer Semantic Model

**Honest scope note:** this repo cannot ship a `.pbix` file — building one
requires Power BI Desktop (Windows GUI app), which isn't available in this
environment. What's provided here is everything you need to build the
report yourself in ~15 minutes: the Power Query (M) source connections and
the DAX measures, wired to the exact Gold Delta tables produced by
`spark/build_gold_star_schema.py` / `warehouse/gold_star_schema.sql`.

## 1. Connect Power BI to the Gold layer

**Option A — Delta tables on ADLS Gen2 (matches the Databricks deployment):**

```m
let
    Source = AzureStorage.DataLake("https://<storage_account>.dfs.core.windows.net/gold"),
    fact_orders = Delta.Table(Source{[Name="fact_orders"]}[Content]),
    dim_customer = Delta.Table(Source{[Name="dim_customer"]}[Content]),
    dim_supplier = Delta.Table(Source{[Name="dim_supplier"]}[Content]),
    dim_date = Delta.Table(Source{[Name="dim_date"]}[Content])
in
    fact_orders
```

**Option B — Postgres (local dev / `warehouse/gold_star_schema.sql`):**

```m
let
    Source = PostgreSQL.Database("localhost", "platform_db"),
    gold_schema = Source{[Schema="gold"]}[Data],
    fact_orders = gold_schema{[Name="fact_orders"]}[Data]
in
    fact_orders
```

## 2. Model relationships (star schema)

| From                          | To                     | Cardinality |
|--------------------------------|------------------------|-------------|
| fact_orders[customer_key]      | dim_customer[customer_key] | many-to-one |
| fact_orders[supplier_key]      | dim_supplier[supplier_key] | many-to-one |
| fact_orders[order_date_key]    | dim_date[date_key]     | many-to-one |
| fact_orders[delivery_date_key] | dim_date[date_key]     | many-to-one (inactive; activate with `USERELATIONSHIP` where needed) |

Mark `dim_date` as a Date Table in Power BI (Modeling → Mark as Date Table).

## 3. Core DAX measures

```dax
Total Order Value =
SUM ( fact_orders[order_amount] )

Delivered Order Value =
CALCULATE (
    [Total Order Value],
    fact_orders[status] = "DELIVERED"
)

Order Count =
COUNTROWS ( fact_orders )

Avg Fulfillment Days =
AVERAGE ( fact_orders[fulfillment_days] )

Cancellation Rate =
DIVIDE (
    CALCULATE ( [Order Count], fact_orders[status] = "CANCELLED" ),
    [Order Count]
)

Order Value MTD =
TOTALMTD ( [Total Order Value], dim_date[date] )

Order Value by Delivery Date =
CALCULATE (
    [Total Order Value],
    USERELATIONSHIP ( fact_orders[delivery_date_key], dim_date[date_key] )
)
```

## 4. Suggested report pages

1. **Overview** — Total Order Value, Order Count, Cancellation Rate cards; Order Value by month (dim_date).
2. **Suppliers** — Order Value by dim_supplier[supplier_name], Avg Fulfillment Days by supplier.
3. **Customers** — Top customers by Total Order Value (dim_customer).
