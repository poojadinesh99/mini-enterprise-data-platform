variable "project_name" {
  description = "Short name used as prefix for all resources."
  type        = string
  default     = "mini-ent-data"
}

variable "environment" {
  description = "Deployment environment (dev/test/prod)."
  type        = string
  default     = "dev"
}

variable "location" {
  description = "Azure region."
  type        = string
  default     = "germanywestcentral"
}

variable "postgres_admin_login" {
  description = "Admin username for the Postgres Flexible Server (local-dev-parity DB)."
  type        = string
  default     = "platform_admin"
}

variable "postgres_admin_password" {
  description = "Admin password for the Postgres Flexible Server. Pass via TF_VAR or CI secret, never commit."
  type        = string
  sensitive   = true
}

variable "databricks_sku" {
  description = "Databricks workspace pricing tier."
  type        = string
  default     = "standard"
}

variable "tags" {
  description = "Common resource tags."
  type        = map(string)
  default = {
    project    = "mini-enterprise-data-platform"
    managed_by = "terraform"
  }
}
