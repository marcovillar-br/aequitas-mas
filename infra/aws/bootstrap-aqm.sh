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

# 4. Configuração de Segurança do Bucket S3
echo "🔐 Securing S3 Bucket: $BUCKET_NAME..."

# Bloqueio de Acesso Público
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Habilitar Criptografia Padrão (SSE-S3) - Correção do Copilot
echo "💎 Enabling Default SSE-S3 Encryption..."
aws s3api put-bucket-encryption \
    --bucket "$BUCKET_NAME" \
    --server-side-encryption-configuration '{
        "Rules": [
            {
                "ApplyServerSideEncryptionByDefault": {
                    "SSEAlgorithm": "AES256"
                }
            }
        ]
    }'

# Habilitar Versionamento (Best Practice para State Files)
echo "📜 Enabling Bucket Versioning..."
aws s3api put-bucket-versioning \
    --bucket "$BUCKET_NAME" \
    --versioning-configuration Status=Enabled

# 5. Create DynamoDB Table for State Locking
# Switching to PAY_PER_REQUEST for optimal FinOps and zero-maintenance
echo "⚡ Creating DynamoDB Lock Table: $TABLE_NAME..."
aws dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Project,Value=Aequitas Key=Service,Value=MAS Key=Environment,Value=Shared-Infra

# 6. Enforce TLS (HTTPS only) via Bucket Policy
echo "🔒 Enforcing TLS 1.2+ for S3 Bucket..."
cat <<EOF > s3-tls-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "EnforceTLS",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME",
        "arn:aws:s3:::$BUCKET_NAME/*"
      ],
      "Condition": {
        "Bool": { "aws:SecureTransport": "false" }
      }
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket "$BUCKET_NAME" --policy file://s3-tls-policy.json
rm s3-tls-policy.json

echo "----------------------------------------------------"
echo "✅ Bootstrap complete for Account $ACCOUNT_ID!"
echo "⚠️  REMEMBER: Repeat this for your other 2 accounts."
echo "----------------------------------------------------"