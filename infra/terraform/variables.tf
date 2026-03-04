# Standard AWS region for the Aequitas-MAS ecosystem
variable "AQM_REGION" {
  description = "Default AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# Proportional capacity for OpenSearch Serverless (OCUs)
variable "AQM_OS_CAPACITY" {
  description = "Maximum capacity for OpenSearch Serverless collections"
  type        = map(number)
  default = {
    dev  = 2 # Minimum (1 Indexing, 1 Search)
    hom  = 2
    prod = 4 # Increased scale for production workloads
  }
}

# Data protection flags based on environment criticality
variable "AQM_ENABLE_DELETION_PROTECTION" {
  description = "Controls resource deletion protection"
  type        = map(bool)
  default = {
    dev  = false
    hom  = false
    prod = true # Protection enabled only for production
  }
}