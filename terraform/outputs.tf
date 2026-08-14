output "resource_group_name" {
  value = azurerm_resource_group.this.name
}

output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.this.workspace_url
}

output "datalake_storage_account" {
  value = azurerm_storage_account.datalake.name
}

output "postgres_server_fqdn" {
  value = azurerm_postgresql_flexible_server.this.fqdn
}

output "log_analytics_workspace_id" {
  value = azurerm_log_analytics_workspace.this.workspace_id
}
