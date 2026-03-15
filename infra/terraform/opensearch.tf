locals {
  opensearch_collection_name = "aequitas-vector-store-${terraform.workspace}"
  opensearch_index_resources = [
    "index/${local.opensearch_collection_name}/${var.opensearch_index.fisher}",
    "index/${local.opensearch_collection_name}/${var.opensearch_index.macro}"
  ]
  opensearch_audit_index_resource = "index/${local.opensearch_collection_name}/${var.opensearch_index.audit}"
  developer_sso_arn_trimmed       = trimspace(var.developer_sso_arn)
  enable_developer_sso_access = (
    terraform.workspace == "dev" &&
    local.developer_sso_arn_trimmed != ""
  )
}

# 1. Política de Criptografia
resource "aws_opensearchserverless_security_policy" "AQM_VECTOR_STORE_ENCRYPTION_POLICY" {
  name        = "aqm-vector-store-enc-${terraform.workspace}"
  type        = "encryption"
  description = "Encryption policy for Aequitas-MAS shared Vector Store collection"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection",
      Resource     = ["collection/${local.opensearch_collection_name}"]
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
      { ResourceType = "collection", Resource = ["collection/${local.opensearch_collection_name}"] },
      { ResourceType = "dashboard", Resource = ["collection/${local.opensearch_collection_name}"] }
    ],
    AllowFromPublic = true
  }])
}

# 3. Política de Acesso aos Dados
resource "aws_opensearchserverless_access_policy" "AQM_VECTOR_STORE_ACCESS_POLICY" {
  name        = "aqm-vector-store-acc-${terraform.workspace}"
  type        = "data"
  description = "Data access policy for Aequitas-MAS shared Vector Store collection"
  policy = jsonencode(
    concat(
      [
        {
          Rules = [
            {
              ResourceType = "index",
              Resource     = local.opensearch_index_resources,
              Permission = [
                "aoss:ReadDocument",
                "aoss:WriteDocument",
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex"
              ]
            },
            {
              ResourceType = "index",
              Resource     = [local.opensearch_audit_index_resource],
              Permission = [
                "aoss:WriteDocument",
                "aoss:CreateIndex"
              ]
            },
            {
              ResourceType = "collection",
              Resource     = ["collection/${local.opensearch_collection_name}"],
              Permission = [
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
        }
      ],
      local.enable_developer_sso_access ? [
        {
          Rules = [
            {
              ResourceType = "index",
              Resource     = local.opensearch_index_resources,
              Permission = [
                "aoss:ReadDocument",
                "aoss:WriteDocument",
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex"
              ]
            },
            {
              ResourceType = "index",
              Resource     = [local.opensearch_audit_index_resource],
              Permission = [
                "aoss:WriteDocument",
                "aoss:CreateIndex"
              ]
            },
            {
              ResourceType = "collection",
              Resource     = ["collection/${local.opensearch_collection_name}"],
              Permission = [
                "aoss:CreateCollectionItems",
                "aoss:DeleteCollectionItems",
                "aoss:UpdateCollectionItems",
                "aoss:DescribeCollectionItems"
              ]
            }
          ],
          Principal = [local.developer_sso_arn_trimmed]
        }
      ] : []
    )
  )
}

# 4. A Coleção OpenSearch Serverless (Shared Collection — ADR 006)
resource "aws_opensearchserverless_collection" "AQM_VECTOR_STORE" {
  name        = local.opensearch_collection_name
  type        = "VECTORSEARCH"
  description = "Shared vector store for all Aequitas-MAS agents (Fisher + Macro) - see ADR 006"

  tags = {
    Name         = local.opensearch_collection_name
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
