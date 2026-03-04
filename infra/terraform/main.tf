# Terraform configuration and AWS provider setup
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.AQM_REGION
}

# Centralized tagging metadata for compliance and FinOps
locals {
  common_tags = {
    Project      = "Aequitas"      # Consistent with 99_Etimologia.docx
    Service      = "MAS"           # Multi-Agent System identifier
    Owner        = "Marco Villar"  # Institutional responsibility
    CostCenter   = "PA-UFG-AI"     # FinOps tracking (ETD v5, Section 5.1)
    Architecture = "Graph-RAG"     # Paradigm descriptor
    Environment  = terraform.workspace
    ManagedBy    = "Terraform"     # Zero manual configuration enforcement
  }
}