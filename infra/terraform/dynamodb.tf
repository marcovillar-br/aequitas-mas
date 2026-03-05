# DynamoDB table for LangGraph cyclic state persistence
resource "aws_dynamodb_table" "AQM_CHECKPOINTS" {
  # Dynamic naming based on workspace (e.g., AQM_Checkpoints_dev)
  name           = "AQM_Checkpoints_${terraform.workspace}"
  billing_mode   = "PAY_PER_REQUEST" # FinOps: Pay only for what is used
  hash_key       = "thread_id"
  range_key      = "checkpoint_id"

  # Core attributes for state management
  attribute {
    name = "thread_id"
    type = "S"
  }

  attribute {
    name = "checkpoint_id"
    type = "S"
  }

  # Environment-based protection (Right-sizing)
  # FIX: Using lookup() to prevent errors in non-standard workspaces (e.g., feature branches)
  deletion_protection_enabled = lookup(var.AQM_ENABLE_DELETION_PROTECTION, terraform.workspace, false)

  # Mandatory tags for compliance and audit (ETD v5, Section 5.1)
  tags = merge(local.common_tags, {
    Component = "Persistence"
  })
}