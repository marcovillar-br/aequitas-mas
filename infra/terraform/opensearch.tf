# 1. Política de Criptografia
resource "aws_opensearchserverless_security_policy" "AQM_VECTOR_STORE_ENCRYPTION_POLICY" {
  name        = "aqm-vector-store-enc-${terraform.workspace}"
  type        = "encryption"
  description = "Encryption policy for Aequitas-MAS shared Vector Store collection"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection",
      Resource     = ["collection/aequitas-vector-store-${terraform.workspace}"]
    }],
    AWSOwnedKey = true
  })
}

# 2. Política de Rede (Acesso Público para MVP)
resource "aws_opensearchserverless_security_policy" "AQM_VECTOR_STORE_NETWORK_POLICY" {
  name        = "aqm-vector-store-net-${terraform.workspace}"
  type        = "network"
  description = "Network access policy for Aequitas-MAS shared Vector Store collection"
  policy = jsonencode([{
    Rules = [
      { ResourceType = "collection", Resource = ["collection/aequitas-vector-store-${terraform.workspace}"] },
      { ResourceType = "dashboard", Resource = ["collection/aequitas-vector-store-${terraform.workspace}"] }
    ],
    AllowFromPublic = true
  }])
}

# 3. Política de Acesso aos Dados
resource "aws_opensearchserverless_access_policy" "AQM_VECTOR_STORE_ACCESS_POLICY" {
  name        = "aqm-vector-store-acc-${terraform.workspace}"
  type        = "data"
  description = "Data access policy for Aequitas-MAS shared Vector Store collection"
  policy = jsonencode([{
    Rules = [
      {
        ResourceType = "index",
        Resource     = ["index/aequitas-vector-store-${terraform.workspace}/*"],
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
        Resource     = ["collection/aequitas-vector-store-${terraform.workspace}"],
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

# 4. A Coleção OpenSearch Serverless (Shared Collection — ADR 006)
resource "aws_opensearchserverless_collection" "AQM_VECTOR_STORE" {
  name        = "aequitas-vector-store-${terraform.workspace}"
  type        = "VECTORSEARCH"
  description = "Shared vector store for all Aequitas-MAS agents (Fisher + Macro) - see ADR 006"

  tags = {
    Name         = "aequitas-vector-store-${terraform.workspace}"
    Environment  = terraform.workspace
    Project      = "Aequitas"
    Service      = "MAS"
    Component    = "RAG"
    Architecture = "Graph-RAG"
    PlannedOCU   = "2"
    CostCenter   = "TA-UFG-AI"
  }

  depends_on = [
    aws_opensearchserverless_security_policy.AQM_VECTOR_STORE_ENCRYPTION_POLICY,
    aws_opensearchserverless_security_policy.AQM_VECTOR_STORE_NETWORK_POLICY,
    aws_opensearchserverless_access_policy.AQM_VECTOR_STORE_ACCESS_POLICY
  ]
}
