# 🎯 Project Status: Aequitas-MAS

## 📌 Current Sprint: 3.1 - Infraestrutura de Persistência (Serverless)
**Foco Imediato:** Liquidar a dívida técnica de infraestrutura implementando o `DynamoDBSaver` via Inversão de Dependência, garantindo testabilidade absoluta local.

### 🛠️ Objetivos da Próxima Sessão (SOD)
1.  **Implementação do Adaptador DynamoDB:** Criar a classe `DynamoDBSaver` com Injeção de Dependência (DI) para isolar o `boto3`.
2.  **Validação de Zero Trust (Testes):** Desenvolver testes unitários rigorosos com `pytest-mock` simulando o comportamento da tabela DynamoDB sem chamadas de rede.
3.  **Integração Dinâmica do Checkpointer:** Atualizar a função `create_graph` para selecionar entre `MemorySaver` (local) e `DynamoDBSaver` (cloud) com base no ambiente.

### ✅ Definition of Done (DoD)
- [ ] `DynamoDBSaver` implementado sem ferir o confinamento da nuvem (DIP).
- [ ] Cobertura de testes (`pytest-mock`) confirmando o isolamento da AWS.
- [ ] Ausência estrita da biblioteca `decimal.Decimal` na serialização, preservando a degradação controlada com `Optional[float] = None`.