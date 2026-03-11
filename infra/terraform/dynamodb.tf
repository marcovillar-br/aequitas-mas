resource "aws_dynamodb_table" "AQM_CHECKPOINTS" {
  name         = "AQM_Checkpoints_${terraform.workspace}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "thread_id"
  range_key    = "checkpoint_id"

  attribute {
    name = "thread_id"
    type = "S"
  }

  attribute {
    name = "checkpoint_id"
    type = "S"
  }

  deletion_protection_enabled = lookup(var.AQM_ENABLE_DELETION_PROTECTION, terraform.workspace, false)

  tags = {
    Environment = terraform.workspace
    Project     = "Aequitas"
    Service     = "MAS"
    Component   = "Persistence"
    ManagedBy   = "Terraform"
    Owner       = "Marco Villar"
    CostCenter  = "TA-UFG-AI"
  }
}