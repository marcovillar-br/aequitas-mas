#!/bin/bash
# Script de correção de permissões - Aequitas-MAS

ROLE_NAME="Aequitas-MAS-GitHub-CI-CD"
POLICY_NAME="GitHubActionsAccess"
PROFILES=("aqm-dev" "aqm-hom" "aqm-prod")

# Criar o arquivo JSON da política
cat <<'EOT' > ci-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "TerraformStateAndBackend",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject", "s3:GetObject", "s3:ListBucket",
        "dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:DeleteItem", "dynamodb:DescribeTable"
      ],
      "Resource": "*"
    },
    {
      "Sid": "OpenSearchServerlessAdmin",
      "Effect": "Allow",
      "Action": [
        "aoss:*",
        "iam:CreateServiceLinkedRole"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DynamoDBFullAccess",
      "Effect": "Allow",
      "Action": ["dynamodb:*"],
      "Resource": "*"
    }
  ]
}
EOT

echo "🔐 Iniciando atualização das permissões IAM..."

for p in "${PROFILES[@]}"; do
    echo "--------------------------------------------------"
    echo "🚀 Processando perfil: $p"
    
    # Executa o comando e captura a saída de erro
    output=$(aws iam put-role-policy \
        --role-name "$ROLE_NAME" \
        --policy-name "$POLICY_NAME" \
        --policy-document file://ci-policy.json \
        --profile "$p" 2>&1)

    if [ $? -eq 0 ]; then
        echo "✅ Sucesso: Política atualizada em $p"
    else
        echo "❌ Erro no perfil $p:"
        echo "$output"
    fi
done

# Limpeza
rm ci-policy.json
echo "--------------------------------------------------"
echo "🎉 Fim do processo."
