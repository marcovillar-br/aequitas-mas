# 🗺️ PLAN: Execução de Engenharia (Sprint 3.1)

O desenvolvimento deve ser estritamente sequencial. O GCA não deve avançar para o próximo passo sem aprovação do Tech Lead.

* [ ] **Passo 1 (Atómico):** Criar `src/infra/adapters/dynamo_saver.py`. Implementar a classe `DynamoDBSaver` (herdando de `BaseCheckpointSaver`). Fazer o setup do `boto3` no `__init__` respeitando a regra *Zero Trust*. Deixar os métodos `get_tuple` e `put` apenas com a assinatura (`pass`).
* [ ] **Passo 2:** Implementar a lógica de leitura (`get_tuple`) e escrita em lote (`put`) no `dynamo_saver.py`, garantindo o mapeamento correto do `thread_id` para a chave de partição do DynamoDB.
* [ ] **Passo 3:** Criar `tests/test_dynamo_saver.py`. Escrever testes unitários utilizando `pytest-mock` para simular o comportamento do `boto3.resource`, garantindo que não ocorram chamadas reais de rede.
* [ ] **Passo 4:** Atualizar `src/core/graph.py` para incluir o nó do Agente Macro no roteamento (`router_map` e `Conditional Edges`). Atualizar o `personas.md` para refletir esta mudança topológica.