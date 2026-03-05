#!/bin/bash
set -e

# 1. Identificação Automática da Conta
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
ROLE_NAME="Aequitas-MAS-GitHub-CI-CD"
POLICY_NAME="AQM-CI-CD-Permissions"

echo "----------------------------------------------------"
echo "🔐 Updating Hardened Policy for Account: $ACCOUNT_ID"
echo "🎯 Role: $ROLE_NAME"

# 2. Geração do JSON de Política com Privilégio Mínimo (Hardening)
# O heredoc substitui automaticamente o ${ACCOUNT_ID}
cat <<EOF > hardened-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "TerraformBackendAndState",
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::aqm-terraform-state-${ACCOUNT_ID}",
                "arn:aws:s3:::aqm-terraform-state-${ACCOUNT_ID}/*"
            ]
        },
        {
            "Sid": "ProjectDynamoDBManagement",
            "Effect": "Allow",
            "Action": [
                "dynamodb:DescribeTable",
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:CreateTable",
                "dynamodb:DeleteTable",
                "dynamodb:UpdateTable",
                "dynamodb:TagResource"
            ],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/aqm-terraform-state-lock",
                "arn:aws:dynamodb:*:*:table/AQM_*"
            ]
        },
        {
            "Sid": "OpenSearchServerlessManagement",
            "Effect": "Allow",
            "Action": [
                "aoss:CreateCollection",
                "aoss:DeleteCollection",
                "aoss:UpdateCollection",
                "aoss:DescribeCollection",
                "aoss:ListCollections",
                "aoss:CreateSecurityPolicy",
                "aoss:DeleteSecurityPolicy",
                "aoss:UpdateSecurityPolicy",
                "aoss:DescribeSecurityPolicy",
                "aoss:CreateAccessPolicy",
                "aoss:DeleteAccessPolicy",
                "aoss:UpdateAccessPolicy",
                "aoss:DescribeAccessPolicy",
                "aoss:TagResource",
                "aoss:GetAccountSettings",
                "aoss:UpdateAccountSettings"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# 3. Aplicação da Política na AWS
echo "🚀 Applying policy to IAM..."
aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "$POLICY_NAME" \
    --policy-document file://hardened-policy.json

echo "✅ Success! Account $ACCOUNT_ID is now hardened."
echo "----------------------------------------------------"

# Limpeza do arquivo temporário
rm hardened-policy.json