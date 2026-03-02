# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 3.1 - Cloud Infrastructure & Persistence (IaC)
**Daily Focus:** Iniciar o provisionamento da infraestrutura Serverless na AWS e implementar os adaptadores hexagonais de persistência (Dependency Inversion), garantindo que o núcleo (Core) do LangGraph permaneça agnóstico em relação ao provedor de nuvem.

### 🛠️ Immediate Session Objectives
1. **IaC Provisioning (Terraform):** Desenvolver o ficheiro `infra/dynamodb.tf` para implementar a tabela de Checkpointer do LangGraph utilizando o modo de faturamento *Pay-Per-Request*.
2. **Vector Database:** Desenvolver o ficheiro `infra/opensearch.tf` (Amazon OpenSearch Serverless) para preparar o pipeline RAG do Agente Fisher.
3. **Hexagonal Cloud Adapters:** Criar o diretório e os módulos em `src/infra/adapters/` para isolar a biblioteca `boto3`.

### 🚫 Architectural Constraints (Risk Confinement)
* **Dependency Inversion Principle (DIP):** É estritamente proibido importar `boto3` ou qualquer SDK de nuvem dentro dos diretórios `/src/agents` ou `/src/core`. Toda a comunicação deve ser injetada via interfaces/adaptadores.
* **FinOps:** Todos os recursos Terraform devem usar modelos de cobrança sob demanda (*Serverless*) para evitar custos ociosos durante a fase de desenvolvimento.
* **Zero Trust:** A gestão de segredos e chaves de API deve continuar a utilizar variáveis de ambiente injetadas pelo Secret Manager da IDE. Proibido o uso de ficheiros `.env` rastreados ou fixos no código.

### ✅ Definition of Done (DoD) for Tomorrow
- [ ] Ficheiros Terraform (`dynamodb.tf` e `opensearch.tf`) codificados e validados via `terraform fmt` e `terraform validate`.
- [ ] Adaptador de persistência (`src/infra/adapters/dynamo_saver.py`) criado para interfacear com a AWS.
- [ ] Cobertura de testes unitários para os adaptadores utilizando `pytest-mock` para simular as respostas do `boto3` sem realizar chamadas reais de rede.