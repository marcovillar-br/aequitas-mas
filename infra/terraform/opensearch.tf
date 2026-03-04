# OpenSearch Serverless collection for Fisher Agent's Qualitative analysis
resource "aws_opensearchserverless_collection" "AQM_FISHER_VECTOR_STORE" {
  # OpenSearch naming requires lowercase and hyphens
  name        = "aqm-fisher-${terraform.workspace}"
  type        = "VECTORSEARCH"
  description = "Vector storage for the Fisher Agent - Aequitas-MAS"

  # Integration with global governance tags
  tags = merge(local.common_tags, {
    Component = "RAG"
  })
}

# Note: Access policies should be added here in the next sprint
# to allow the GitHub Actions Role to manage the index.