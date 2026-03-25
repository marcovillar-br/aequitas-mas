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

# 4. OpenSearch Index Routing (ADR 006 — Shared Collection, Separate Indices)
# Defines logical routing per bounded context in the shared collection.
variable "opensearch_index" {
  description = "OpenSearch index names per agent domain for the shared aequitas-vector-store collection"
  type        = map(string)
  default = {
    fisher = "fisher-index"
    macro  = "macro-index"
    audit  = "aequitas-decision-path"
  }

  validation {
    condition = (
      can(var.opensearch_index.fisher) &&
      can(var.opensearch_index.macro) &&
      can(var.opensearch_index.audit) &&
      trimspace(var.opensearch_index.fisher) != "" &&
      trimspace(var.opensearch_index.macro) != "" &&
      trimspace(var.opensearch_index.audit) != "" &&
      var.opensearch_index.fisher != var.opensearch_index.macro &&
      var.opensearch_index.fisher != var.opensearch_index.audit &&
      var.opensearch_index.macro != var.opensearch_index.audit
    )
    error_message = "opensearch_index must define non-empty and distinct values for keys 'fisher', 'macro', and 'audit'."
  }
}

# 5. Optional developer SSO principal for OpenSearch write tests in dev.
# Keep empty by default; when provided, it is applied only in workspace `dev`.
variable "developer_sso_arn" {
  description = "Optional IAM role/user ARN for developer SSO access in dev workspace (OpenSearch data policy)"
  type        = string
  default     = ""

  validation {
    condition = (
      trimspace(var.developer_sso_arn) == "" ||
      can(regex("^arn:aws:iam::[0-9]{12}:(role|user)/.+$", trimspace(var.developer_sso_arn)))
    )
    error_message = "developer_sso_arn must be empty or a valid IAM role/user ARN (arn:aws:iam::<account-id>:role/... or :user/...)."
  }
}
