# DynamoDB table for LangGraph cyclic state persistence
resource "aws_dynamodb_table" "AQM_CHECKPOINTS" {
  # Naming follows technical acronym and workspace context
  name           = "AQM_Checkpoints_${terraform.workspace}"
  billing_mode   = "PAY_PER_REQUEST" 
  hash_key       = "thread_id"
  range_key      = "checkpoint_id"

  attribute {
    name = "thread_id"
    type = "S"
  }

  attribute {
    name = "checkpoint_id"
    type = "S"
  }

  # Right-sizing: Deletion protection is proportional to the environment
  deletion_protection_enabled = var.AQM_ENABLE_DELETION_PROTECTION[terraform.workspace]

  # Merge global tags with component-specific metadata
  tags = merge(local.common_tags, {
    Component = "Persistence"
  })
}