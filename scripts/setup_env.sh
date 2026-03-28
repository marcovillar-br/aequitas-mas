#!/bin/bash

# Aequitas-MAS Environment Setup Script
# This script generates a local .env file securely.

ENV_FILE=".env"

echo "==================================================="
echo "  Aequitas-MAS: Local Environment Setup"
echo "==================================================="

# Security check: Prevent accidental overwrite of existing keys
if [ -f "$ENV_FILE" ]; then
    echo "WARNING: An existing $ENV_FILE file was found."
    read -p "Do you want to overwrite it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Operation cancelled. Existing $ENV_FILE preserved."
        exit 0
    fi
fi

echo ""
echo "Please provide the following credentials (press Enter to leave blank/default):"

read -p "OpenSearch Endpoint (e.g., https://bw526xpyvixs3y1e0ytg.us-east-1.aoss.amazonaws.com): " opensearch_endpoint
read -p "OpenSearch Macro Index (default: macro-index): " opensearch_macro_index
read -p "OpenSearch Audit Index (default: aequitas-decision-path): " opensearch_audit_index
read -p "OpenSearch Region (default: us-east-1): " opensearch_region
read -p "Gemini API Key: " gemini_api_key
read -p "Terraform AWS Region (default: same as OpenSearch Region): " tf_var_aqm_region
read -p "Developer SSO ARN for Terraform (optional, for dev OpenSearch policy): " tf_var_developer_sso_arn
read -p "Enable Free Tier API throttling? (true/false, default: false): " free_tier_throttle

# Apply defaults
opensearch_macro_index=${opensearch_macro_index:-macro-index}
opensearch_audit_index=${opensearch_audit_index:-aequitas-decision-path}
opensearch_region=${opensearch_region:-us-east-1}
tf_var_aqm_region=${tf_var_aqm_region:-$opensearch_region}
free_tier_throttle=${free_tier_throttle:-false}

echo ""
echo "Generating $ENV_FILE..."

# Write securely to the .env file
cat <<EOF > $ENV_FILE
# Aequitas-MAS Local Environment Variables
# DO NOT COMMIT THIS FILE - IT CONTAINS SENSITIVE KEYS

# --- AWS OpenSearch Serverless ---
OPENSEARCH_ENDPOINT=$opensearch_endpoint
OPENSEARCH_INDEX=$opensearch_macro_index
OPENSEARCH_AUDIT_INDEX=$opensearch_audit_index
OPENSEARCH_REGION=$opensearch_region
OPENSEARCH_SERVICE=aoss

# --- LLM Provider ---
GEMINI_API_KEY=$gemini_api_key

# --- Terraform Variables (auto-loaded via TF_VAR_*) ---
TF_VAR_AQM_REGION=$tf_var_aqm_region
TF_VAR_developer_sso_arn=$tf_var_developer_sso_arn

# --- LangGraph Checkpointer ---
# Set to 'local' to use MemorySaver, or 'dev'/'prod' for DynamoDBSaver
ENVIRONMENT=local

# --- API Rate Limiting ---
# Set to 'true' for Free Tier (15s delay between LLM calls), 'false' for paid keys
AEQUITAS_FREE_TIER_THROTTLE=$free_tier_throttle
EOF

echo "Success: $ENV_FILE created."
echo "Security Check: Please verify that .env is listed in your .gitignore file."
echo "==================================================="
