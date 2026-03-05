# ==============================================================================
# AEQUITAS-MAS: Core Infrastructure Configuration
# This file defines the Provider, Backend (Partial), and Global Tags.
# ==============================================================================

terraform {
  required_version = ">= 1.14.5"

  # PARTIAL BACKEND CONFIGURATION
  # ----------------------------------------------------------------------------
  # Critical for Multi-Account safety: bucket, region, and dynamodb_table 
  # are NOT hardcoded. They must be supplied via -backend-config during 
  # 'terraform init' in the CI/CD pipeline.
  # ----------------------------------------------------------------------------
  backend "s3" {
    key     = "terraform.tfstate"
    encrypt = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.100.0"
    }
  }
}

# AWS Provider configuration with unified tagging
provider "aws" {
  region = var.AQM_REGION

  default_tags {
    tags = local.common_tags
  }
}

# ==============================================================================
# LOCALS: Centralized Governance & FinOps Tags
# ==============================================================================
locals {
  common_tags = {
    Project    = "Aequitas"
    Service    = "MAS"
    Owner      = "Marco Villar"
    ManagedBy  = "Terraform"
    CostCenter = "TA-UFG-AI"
    # Dynamically tracks the environment (dev, hom, prod)
    Environment = terraform.workspace
  }
}

# ==============================================================================
# DATA SOURCES: Identity & Context
# ==============================================================================
# Used to fetch current account ID for resource policies (e.g., OpenSearch)
data "aws_caller_identity" "current" {}