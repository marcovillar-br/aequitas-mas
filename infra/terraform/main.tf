# Terraform configuration and AWS provider setup
terraform {
  required_version = ">= 1.5.0"

  # S3 Backend for State Persistence and Locking (Risk Confinement)
  backend "s3" {
    bucket         = "aqm-terraform-state-689366766340" # Replace with your unique bucket name
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "aqm-terraform-state-lock" # For state locking
  }

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
    Project      = "Aequitas"
    Service      = "MAS"
    Owner        = "Marco Villar"
    CostCenter   = "TA-UFG-AI"
    Architecture = "Graph-RAG"
    Environment  = terraform.workspace
    ManagedBy    = "Terraform"
  }
}