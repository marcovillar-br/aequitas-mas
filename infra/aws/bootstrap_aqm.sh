#!/bin/bash
# AQM Multi-Account Bootstrap - Level 0 Infrastructure
# Purpose: Setup S3 Backend and DynamoDB Locking for Terraform

# 1. Identity Check
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
if [ $? -ne 0 ]; then
    echo "❌ Error: Could not get AWS Account ID. Are you logged in?"
    exit 1
fi

REGION="us-east-1"
BUCKET_NAME="aqm-terraform-state-${ACCOUNT_ID}"
TABLE_NAME="aqm-terraform-state-lock"

echo "----------------------------------------------------"
echo "🚀 Starting AQM Bootstrap for Account: $ACCOUNT_ID"
echo "📍 Region: $REGION"
echo "🪣 Bucket: $BUCKET_NAME"
echo "🔒 Table:  $TABLE_NAME"
echo "----------------------------------------------------"

# 2. Create S3 Bucket (Private by default)
echo "📦 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION

# 3. Enable Versioning (Critical for state recovery/undo)
aws s3api put-bucket-versioning \
    --bucket $BUCKET_NAME \
    --versioning-configuration Status=Enabled

# 4. Strict Public Access Block (Zero Trust Compliance)
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 5. Create DynamoDB Table for State Locking
echo "🔐 Creating DynamoDB locking table..."
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION

echo "----------------------------------------------------"
echo "✅ Bootstrap complete for Account $ACCOUNT_ID!"
echo "⚠️  REMEMBER: Repeat this for your other 2 accounts."
echo "----------------------------------------------------"