# ==============================================================================
# AQUISTAS-MAS: OpenSearch Serverless Configuration (Fisher Agent)
# This file manages the Vector Store infrastructure for Graph-RAG capabilities.
# ==============================================================================

# 1. Capacity Control (FinOps)
# Sets the maximum OCUs allowed for this account to prevent unexpected costs.
resource "aws_opensearchserverless_account_settings" "AQM_CAPACITY_CONTROL" {
  maximum_indexing_capacity = var.AQM_OS_CAPACITY[terraform.workspace]
  maximum_search_capacity   = var.AQM_OS_CAPACITY[terraform.workspace]
}

# 2. Security Policy: Encryption
# Defines the KMS encryption settings for the collection.
resource "aws_opensearchserverless_security_policy" "AQM_FISHER_ENCRYPTION_POLICY" {
  name        = "aqm-fisher-enc-${terraform.workspace}"
  type        = "encryption"
  description = "Encryption policy for Fisher Agent Vector Store"
  policy = jsonencode({
    Rules = [
      {
        ResourceType = "collection"
        Resource     = ["collection/aqm-fisher-${terraform.workspace}"]
      }
    ]
    AWSOwnedKey = true
  })
}

# 3. Security Policy: Network Access
# Defines how the collection is accessed (Public for MVP, restricted by IAM).
resource "aws_opensearchserverless_security_policy" "AQM_FISHER_NETWORK_POLICY" {
  name        = "aqm-fisher-net-${terraform.workspace}"
  type        = "network"
  description = "Network access policy for Fisher Agent Vector Store"
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource     = ["collection/aqm-fisher-${terraform.workspace}"]
        },
        {
          ResourceType = "dashboard"
          Resource     = ["collection/aqm-fisher-${terraform.workspace}"]
        }
      ]
      AllowFromPublic = true
    }
  ])
}

# 4. Data Access Policy
# Defines WHO can actually perform data operations (indexing/searching).
# It grants access to the CI/CD Role to allow initial setup and testing.
resource "aws_opensearchserverless_access_policy" "AQM_FISHER_ACCESS_POLICY" {
  name        = "aqm-fisher-acc-${terraform.workspace}"
  type        = "data"
  description = "Data access policy for Fisher Agent Vector Store"
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "index"
          Resource     = ["index/aqm-fisher-${terraform.workspace}/*"]
          Permission   = ["indices:*", "dsy:*"]
        },
        {
          ResourceType = "collection"
          Resource     = ["collection/aqm-fisher-${terraform.workspace}"]
          Permission   = ["aoss:CreateCollectionItems", "aoss:DeleteCollectionItems", "aoss:UpdateCollectionItems", "aoss:DescribeCollectionItems"]
        }
      ],
      Principal = [
        # Granting access to the GitHub CI/CD Role
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/Aequitas-MAS-GitHub-CI-CD"
      ]
    }
  ])
}

# 5. OpenSearch Serverless Collection
# The actual Vector Store instance for the Fisher Agent.
resource "aws_opensearchserverless_collection" "AQM_FISHER_VECTOR_STORE" {
  name        = "aqm-fisher-${terraform.workspace}"
  type        = "VECTORSEARCH"
  description = "Vector storage for the Fisher Agent - Aequitas-MAS"

  # Ensure security policies are created BEFORE the collection
  depends_on = [
    aws_opensearchserverless_security_policy.AQM_FISHER_ENCRYPTION_POLICY,
    aws_opensearchserverless_security_policy.AQM_FISHER_NETWORK_POLICY
  ]

  tags = {
    Name         = "aqm-fisher-${terraform.workspace}"
    Environment  = terraform.workspace
    Project      = "Aequitas"
    Service      = "MAS"
    Architecture = "Graph-RAG"
    Component    = "RAG"
    CostCenter   = "TA-UFG-AI"
    ManagedBy    = "Terraform"
    PlannedOCU   = var.AQM_OS_CAPACITY[terraform.workspace]
  }
}

# Data source to fetch the current account ID for the Access Policy
data "aws_caller_identity" "current" {}