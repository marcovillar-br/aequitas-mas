# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 3.1 - Cloud Infrastructure & Persistence (IaC)
**Weekly Focus:** Transitioning from local memory (`MemorySaver`) to AWS Serverless infrastructure (DynamoDB & OpenSearch) using Terraform and Dependency Inversion.

### 🛠️ Immediate Session Objectives
1. **IaC Provisioning:** Develop `infra/dynamodb.tf` to implement the production Checkpointer (Pay-Per-Request mode).
2. **Vector Database:** Develop `infra/opensearch.tf` to support the Fisher Agent's RAG pipeline (Serverless).
3. **Hexagonal Adapters:** Implement `src/infra/adapters/` to isolate `boto3` and AWS SDKs from the core logic (DIP compliance).

### 🚫 Architectural Constraints (Risk Confinement)
* **Dependency Inversion:** It is strictly forbidden to import `boto3` or any cloud SDK inside `/src/agents` or `/src/core`. All cloud interactions must occur via Adapters.
* **FinOps:** Ensure all Terraform resources use serverless/on-demand billing models to minimize costs during development.
* **Zero Trust:** Secret Management must be strictly via IDE Secret Manager or AWS Secrets Manager. No `.env` files for cloud credentials.

### ✅ Definition of Done (DoD) for the Session
- [ ] Terraform files (`dynamodb.tf` and `opensearch.tf`) created and validated.
- [ ] `boto3` persistence adapter implemented and unit-tested with mocks.
- [ ] Environment isomorphism maintained: Code must still run locally via `SqliteSaver` if cloud flags are disabled.