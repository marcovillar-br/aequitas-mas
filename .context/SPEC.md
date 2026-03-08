# 📐 SPEC: Adaptador Hexagonal DynamoDB (GitHub Copilot SDD)
**Sprint:** 3.1
**Objetivo:** Implementar persistência Serverless (AWS DynamoDB) via Inversão de Dependência e garantir blindagem arquitetural contra o viés da IA.

## 1. Contratos de Interface (DIP)
* **Arquivo-Alvo:** `src/infra/adapters/dynamo_saver.py`
* **Herança Obrigatória:** `langgraph.checkpoint.base.BaseCheckpointSaver`
* **Isolamento de Nuvem:** A biblioteca `boto3` DEVE estar confinada a este ficheiro e a testes isolados. É expressamente proibido importar `boto3` em `/src/agents/` ou `/src/core/`.

## 2. Injeção de Dependência e Segurança (Zero Trust)
* **Construtor Testável:** A classe `DynamoDBSaver` DEVE suportar Injeção de Dependência no construtor. O recurso AWS (`boto3.resource('dynamodb')`) só deve ser invocado em *runtime* se o parâmetro `table` injetado for nulo. Isso permite que os testes utilizem `pytest-mock` sem estourar *timeouts* de rede.
* **Credenciais:** É proibida a manipulação e leitura de arquivos `.env` diretamente no código do adaptador.

## 3. Diretrizes de Tipagem e Anti-Viés para o GitHub Copilot
* **Bloqueio de Decimal:** Fica expressamente proibido o uso, importação ou conversão para `decimal.Decimal` em qualquer camada de persistência. A arquitetura exige que métricas continuem fluindo estritamente como `float` ou `None`.
* **Degradação Controlada:** Todos os estados baseados no `src/core/state.py` que possuam `Optional[float] = None` devem ter sua ausência mapeada (null values) tratada adequadamente durante a transação com o DynamoDB.