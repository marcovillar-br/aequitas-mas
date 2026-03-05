# ==============================================================================
# AEQUITAS-MAS: Infrastructure Variables
# Defines regional settings and environment-specific capacities for FinOps.
# ==============================================================================

# 1. Deployment Region
# Injected via TF_VAR_AQM_REGION in the GitHub Actions workflow.
variable "AQM_REGION" {
  description = "The target AWS region for all project resources"
  type        = string
  default     = "us-east-1"
}

# 2. OpenSearch Capacity Units (OCUs)
# Controls the maximum scale and cost of the Vector Store per environment.
# dev/hom: Minimal footprint to save costs.
# prod: Higher capacity for real-world traffic.
variable "AQM_OS_CAPACITY" {
  description = "Maximum capacity (Indexing/Search) for OpenSearch Serverless collections"
  type        = map(number)
  default = {
    dev  = 2 # Minimum allowed (1 Indexing + 1 Search OCU)
    hom  = 2 # Mirror of dev for testing parity
    prod = 4 # Increased capacity for production reliability
  }
}

# 3. DynamoDB Project Settings
# Centralizes naming conventions for the LangGraph persistence layer.
variable "AQM_DYNAMO_TABLE_NAME" {
  description = "Base name for the LangGraph checkpoints table"
  type        = string
  default     = "AQM_Checkpoints"
}

variable "AQM_DYNAMO_BILLING" {
  description = "Billing mode for DynamoDB tables (FinOps: PAY_PER_REQUEST for MAS)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "AQM_ENABLE_DELETION_PROTECTION" {
  description = "Logic to prevent accidental deletion of tables per environment"
  type        = map(bool)
  default = {
    dev  = false
    hom  = true
    prod = true
  }
}