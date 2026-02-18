# 1. The Resource Group
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.project_prefix}-dev"
  location = var.location
}

# 2. Azure Data Lake Storage Gen2
resource "azurerm_storage_account" "datalake" {
  name                     = "dls${var.project_prefix}dev123" # Must be globally unique, no hyphens
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  # CRITICAL: This line makes it a Data Lake Gen2
  is_hns_enabled           = true  
}

# 3. Create the Bronze layer folder inside the Data Lake
resource "azurerm_storage_data_lake_gen2_filesystem" "bronze" {
  name               = "bronze"
  storage_account_id = azurerm_storage_account.datalake.id
}

# 4. Azure Key Vault for storing passwords securely
resource "azurerm_key_vault" "kv" {
  name                        = "kv-${var.project_prefix}-dev-123" # Must be globally unique
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  sku_name                    = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    secret_permissions = ["Get", "List", "Set", "Delete", "Purge"]
  }
}

# 5. Azure Data Factory (Our Orchestrator)
resource "azurerm_data_factory" "adf" {
  name                = "adf-${var.project_prefix}-dev-123" # Must be globally unique
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  
  tags = {
    Environment = var.environment
  }
}

# 6. Azure Event Hubs Namespace (The container for Event Hubs)
resource "azurerm_eventhub_namespace" "eh_namespace" {
  name                = "ehns-${var.project_prefix}-dev-123" # Must be globally unique
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "Standard" # Standard allows for better streaming integrations
  capacity            = 1
}

# 7. The actual Event Hub for Clickstream data
resource "azurerm_eventhub" "eh_clickstream" {
  name                = "eh-clickstream"
  namespace_name      = azurerm_eventhub_namespace.eh_namespace.name
  resource_group_name = azurerm_resource_group.rg.name
  partition_count     = 2
  message_retention   = 1 # Keep messages for 1 day
}

# 8. Azure Databricks Workspace
resource "azurerm_databricks_workspace" "dbx" {
  name                = "dbx-${var.project_prefix}-dev-123"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "trial" # Or "standard" if trial isn't available

  tags = {
    Environment = var.environment
  }
}