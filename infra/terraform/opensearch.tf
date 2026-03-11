# 1. Política de Criptografia
resource "aws_opensearchserverless_security_policy" "AQM_FISHER_ENCRYPTION_POLICY" {
  name        = "aqm-fisher-enc-${terraform.workspace}"
  type        = "encryption"
  description = "Encryption policy for Fisher Agent Vector Store"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection",
      Resource     = ["collection/aqm-fisher-${terraform.workspace}"]
    }],
    AWSOwnedKey = true
  })
}

# 2. Política de Rede (Acesso Público para MVP)
resource "aws_opensearchserverless_security_policy" "AQM_FISHER_NETWORK_POLICY" {
  name        = "aqm-fisher-net-${terraform.workspace}"
  type        = "network"
  description = "Network access policy for Fisher Agent Vector Store"
  policy = jsonencode([{
    Rules = [
      { ResourceType = "collection", Resource = ["collection/aqm-fisher-${terraform.workspace}"] },
      { ResourceType = "dashboard", Resource = ["collection/aqm-fisher-${terraform.workspace}"] }
    ],
    AllowFromPublic = true
  }])
}

# 3. Política de Acesso aos Dados (CORRIGIDA)
resource "aws_opensearchserverless_access_policy" "AQM_FISHER_ACCESS_POLICY" {
  name        = "aqm-fisher-acc-${terraform.workspace}"
  type        = "data"
  description = "Data access policy for Fisher Agent Vector Store"
  policy = jsonencode([{
    Rules = [
      {
        ResourceType = "index",
        Resource     = ["index/aqm-fisher-${terraform.workspace}/*"],
        Permission   = [
          "aoss:ReadDocument",
          "aoss:WriteDocument",
          "aoss:CreateIndex",
          "aoss:DeleteIndex",
          "aoss:UpdateIndex",
          "aoss:DescribeIndex"
        ]
      },
      {
        ResourceType = "collection",
        Resource     = ["collection/aqm-fisher-${terraform.workspace}"],
        Permission   = [
          "aoss:CreateCollectionItems",
          "aoss:DeleteCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ]
      }
    ],
    Principal = [
      "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/Aequitas-MAS-GitHub-CI-CD"
    ]
  }])
}

# 4. A Coleção OpenSearch Serverless
resource "aws_opensearchserverless_collection" "AQM_FISHER_VECTOR_STORE" {
  name        = "aqm-fisher-${terraform.workspace}"
  type        = "VECTORSEARCH"
  description = "Vector storage for the Fisher Agent - Aequitas-MAS"

  tags = {
    Name         = "aqm-fisher-${terraform.workspace}"
    Environment  = terraform.workspace
    Project      = "Aequitas"
    Service      = "MAS"
    Component    = "RAG"
    Architecture = "Graph-RAG"
    PlannedOCU   = "2"
    CostCenter   = "TA-UFG-AI"
  }

  depends_on = [
    aws_opensearchserverless_security_policy.AQM_FISHER_ENCRYPTION_POLICY,
    aws_opensearchserverless_security_policy.AQM_FISHER_NETWORK_POLICY,
    aws_opensearchserverless_access_policy.AQM_FISHER_ACCESS_POLICY
  ]
}