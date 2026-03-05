#!/bin/bash
set -e

# 1. Identificação da Conta
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
ROLE_NAME="Aequitas-MAS-GitHub-CI-CD"

echo "----------------------------------------------------"
echo "🔍 Syncing Role for Account: $ACCOUNT_ID"

# 2. Busca o ARN do Provedor OIDC
PROVIDER_ARN=$(aws iam list-open-id-connect-providers --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')].Arn" --output text)

if [ -z "$PROVIDER_ARN" ] || [ "$PROVIDER_ARN" == "None" ]; then
    echo "❌ Error: GitHub OIDC Provider not found."
    exit 1
fi

# 3. Gera a Trust Policy (Quem pode assumir a Role)
cat <<EOF > trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "$PROVIDER_ARN" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": { "token.actions.githubusercontent.com:aud": "sts.amazonaws.com" },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": [
          "repo:marcovillar-br/aequitas-mas:ref:refs/heads/main",
          "repo:marcovillar-br/aequitas-mas:ref:refs/heads/development",
          "repo:marcovillar-br/aequitas-mas:ref:refs/heads/feat/*"
        ]
      }
    }
  }]
}
EOF

# 4. Criação ou Atualização da Trust Policy (Correção do Copilot)
echo "⚙️  Syncing Trust Relationship..."
if ! aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document file://trust-policy.json 2>/dev/null; then
    echo "⚠️  Role already exists. Updating Trust Policy to ensure synchronization..."
    aws iam update-assume-role-policy --role-name "$ROLE_NAME" --policy-document file://trust-policy.json
else
    echo "✅ Role created successfully."
fi

# 5. Aplicação da Política de Permissões (Hardened)
echo "🔐 Applying Hardened Permissions Policy..."
cat <<EOF > hardened-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "TerraformBackendAndState",
            "Effect": "Allow",
            "Action": ["s3:ListBucket", "s3:GetBucketLocation", "s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
            "Resource": [
                "arn:aws:s3:::aqm-terraform-state-${ACCOUNT_ID}",
                "arn:aws:s3:::aqm-terraform-state-${ACCOUNT_ID}/*"
            ]
        },
        {
            "Sid": "ProjectDynamoDBManagement",
            "Effect": "Allow",
            "Action": ["dynamodb:DescribeTable", "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem", "dynamodb:CreateTable", "dynamodb:DeleteTable", "dynamodb:UpdateTable", "dynamodb:TagResource"],
            "Resource": [
                "arn:aws:dynamodb:*:*:table/aqm-terraform-state-lock",
                "arn:aws:dynamodb:*:*:table/AQM_*"
            ]
        },
        {
            "Sid": "OpenSearchServerlessManagement",
            "Effect": "Allow",
            "Action": [
                "aoss:CreateCollection", "aoss:DeleteCollection", "aoss:UpdateCollection", "aoss:DescribeCollection", "aoss:ListCollections",
                "aoss:CreateSecurityPolicy", "aoss:DeleteSecurityPolicy", "aoss:UpdateSecurityPolicy", "aoss:DescribeSecurityPolicy",
                "aoss:CreateAccessPolicy", "aoss:DeleteAccessPolicy", "aoss:UpdateAccessPolicy", "aoss:DescribeAccessPolicy",
                "aoss:TagResource", "aoss:GetAccountSettings", "aoss:UpdateAccountSettings"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name "$ROLE_NAME" \
    --policy-name "AQM-CI-CD-Permissions" \
    --policy-document file://hardened-policy.json

echo "----------------------------------------------------"
echo "🎉 SUCCESS: Role $ROLE_NAME is fully synced in $ACCOUNT_ID!"
echo "----------------------------------------------------"

# Cleanup
rm trust-policy.json hardened-policy.json