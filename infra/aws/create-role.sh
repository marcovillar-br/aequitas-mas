#!/bin/bash
set -e

# 1. Identificação da Conta
ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
ROLE_NAME="Aequitas-MAS-GitHub-CI-CD"

echo "----------------------------------------------------"
echo "🔍 Checking OIDC Provider for Account: $ACCOUNT_ID"

# 2. Busca o ARN do Provedor OIDC do GitHub
PROVIDER_ARN=$(aws iam list-open-id-connect-providers --query "OpenIDConnectProviderList[?contains(Arn, 'token.actions.githubusercontent.com')].Arn" --output text)

if [ -z "$PROVIDER_ARN" ] || [ "$PROVIDER_ARN" == "None" ]; then
    echo "❌ Error: GitHub OIDC Provider not found in this account."
    echo "Please run the create-open-id-connect-provider command first."
    exit 1
fi

echo "✅ Provider found: $PROVIDER_ARN"

# 3. Gera a Trust Policy (Política de Confiança)
# Usando o ARN exato que a AWS retornou
cat <<EOF > trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "$PROVIDER_ARN"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:marcovillar-br/aequitas-mas:*"
        }
      }
    }
  ]
}
EOF

# 4. Criação da Role
echo "🛠️ Creating Role: $ROLE_NAME..."
aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json || echo "⚠️ Role might already exist, attempting to update policy..."

# 5. Anexa a Permissions Policy (Acesso ao Projeto e Backend)
echo "🔐 Attaching Permissions Policy..."
cat <<EOF > permissions-policy.json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowAllProjectResources",
            "Effect": "Allow",
            "Action": [
                "s3:*",
                "dynamodb:*",
                "aoss:*",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name "AQM-CI-CD-Permissions" \
    --policy-document file://permissions-policy.json

echo "----------------------------------------------------"
echo "🎉 SUCCESS: Role $ROLE_NAME is ready in account $ACCOUNT_ID!"
echo "----------------------------------------------------"