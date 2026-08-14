terraform {
  required_version = ">= 1.7.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.51"
    }
  }

  backend "azurerm" {
    # Configure via `terraform init -backend-config=...` (remote state).
    # resource_group_name, storage_account_name, container_name, key
  }
}

provider "azurerm" {
  features {}
}

# Authenticates against the Databricks workspace created below.
provider "databricks" {
  host = azurerm_databricks_workspace.this.workspace_url
}
