locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${local.name_prefix}"
  location = var.location
  tags     = var.tags
}

# ---------------------------------------------------------------------------
# Storage: ADLS Gen2 account backing the Bronze/Silver/Gold Delta Lake layers
# ---------------------------------------------------------------------------
resource "azurerm_storage_account" "datalake" {
  name                     = replace("st${local.name_prefix}", "-", "")
  resource_group_name      = azurerm_resource_group.this.name
  location                 = azurerm_resource_group.this.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"
  is_hns_enabled           = true # required for ADLS Gen2 / Delta Lake
  min_tls_version          = "TLS1_2"
  tags                     = var.tags
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_name  = azurerm_storage_account.datalake.name
  container_access_type = "private"
}

# ---------------------------------------------------------------------------
# Azure Databricks workspace running the PySpark/Delta Lake pipeline (spark/)
# ---------------------------------------------------------------------------
resource "azurerm_databricks_workspace" "this" {
  name                = "dbw-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = var.databricks_sku
  tags                = var.tags
}

# ---------------------------------------------------------------------------
# Postgres Flexible Server: parity with local docker-compose Postgres used
# by ingestion/ (kept for workloads that still need a relational store,
# e.g. governance metadata / operational tables outside the lakehouse).
# ---------------------------------------------------------------------------
resource "azurerm_postgresql_flexible_server" "this" {
  name                   = "psql-${local.name_prefix}"
  resource_group_name    = azurerm_resource_group.this.name
  location               = azurerm_resource_group.this.location
  version                = "15"
  administrator_login    = var.postgres_admin_login
  administrator_password = var.postgres_admin_password
  storage_mb             = 32768
  sku_name               = "B_Standard_B1ms"
  zone                   = "1"
  tags                   = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "platform_db" {
  name      = "platform_db"
  server_id = azurerm_postgresql_flexible_server.this.id
  collation = "en_US.utf8"
  charset   = "utf8"
}

# ---------------------------------------------------------------------------
# Key Vault: secrets for DB credentials, storage keys, service principals
# ---------------------------------------------------------------------------
resource "azurerm_key_vault" "this" {
  name                       = "kv-${substr(local.name_prefix, 0, 15)}"
  resource_group_name        = azurerm_resource_group.this.name
  location                   = azurerm_resource_group.this.location
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  tags                       = var.tags
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgres-admin-password"
  value        = var.postgres_admin_password
  key_vault_id = azurerm_key_vault.this.id
}

# ---------------------------------------------------------------------------
# Log Analytics workspace: backs the monitoring/ Azure Monitor integration
# ---------------------------------------------------------------------------
resource "azurerm_log_analytics_workspace" "this" {
  name                = "log-${local.name_prefix}"
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_monitor_diagnostic_setting" "storage_diag" {
  name                       = "diag-datalake"
  target_resource_id         = azurerm_storage_account.datalake.id
  log_analytics_workspace_id = azurerm_log_analytics_workspace.this.id

  enabled_log {
    category = "StorageWrite"
  }

  metric {
    category = "Transaction"
    enabled  = true
  }
}
