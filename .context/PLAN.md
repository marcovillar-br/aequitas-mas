# 🗺️ PLAN: Execução de Engenharia — Aequitas-MAS

O desenvolvimento deve ser estritamente sequencial. O implementador atuará como "Implementador Cirúrgico". Não avance para o próximo passo sem aprovação do Tech Lead.

---

## 📚 Histórico — Sprints Concluídas

> Registro imutável do desenvolvimento executado. Reflete a ordem sequencial real de
> implementação e serve como fonte de verdade para auditoria arquitetural e onboarding.

---

### ✅ Sprint 3.1 — Persistência DynamoDB (GitHub Copilot SDD)
**Status:** CONCLUÍDA — Merge na `development` via PR #22 (commit `76acc5f`).

* [x] **Passo 1 (Atômico):** Criar `src/infra/adapters/dynamo_saver.py`. Implementar a classe `DynamoDBSaver` (herdando de `BaseCheckpointSaver`). A classe utiliza Injeção de Dependência em seu construtor (`__init__`) para receber a tabela alvo (`table=None`), instanciando `boto3.resource` apenas se nenhuma tabela for injetada.
* [x] **Passo 2:** Implementar a lógica de leitura (`get_tuple`) e escrita (`put`) no `dynamo_saver.py`, mapeando `thread_id` para a chave de partição do DynamoDB. Valores `Optional[float] = None` serializados corretamente via `Binary` para evitar quebras no estado LangGraph.
* [x] **Passo 3:** Criar `tests/test_dynamo_saver.py`. Testes unitários com `pytest-mock` injetando mock da tabela no construtor, garantindo zero interações com a rede (AWS). **4 testes passando.**
* [x] **Passo 4:** Atualizar `src/core/graph.py` para injetar o *checkpointer* dinamicamente em `create_graph()`. `os.getenv("ENVIRONMENT", "local")` decide entre `MemorySaver()` (local) e `DynamoDBSaver()` (dev/hom/prod).

---

### ✅ Sprint 3.2 — Agente Macro: RAG HyDE + OpenSearch (Claude Code)
**Status:** CONCLUÍDA — Branch `feat/macro-hyde-opensearch-integration` (commits `1e27dea` → `e54017c`). Aguardando PR para `development`.

* [x] **Passo 1 — Implementação da Interface VectorStore em `src/core/interfaces/` (DIP Boundary):**
  Criar `src/core/interfaces/__init__.py` e `src/core/interfaces/vector_store.py`.
  Definir `VectorStorePort` como `@runtime_checkable Protocol` com método
  `search_macro_context(query: str, top_k: int = 5) -> list[dict]`.
  Adicionar `NullVectorStore` (Null Object Pattern) como implementação de degradação
  controlada para execução local/offline sem OpenSearch configurado.

* [x] **Passo 2 — Implementação do `OpenSearchAdapter` em `src/infra/adapters/` (Confinamento de Infraestrutura):**
  Criar `src/infra/adapters/opensearch_client.py`.
  Implementar `OpenSearchAdapter` satisfazendo `VectorStorePort` por subtipagem estrutural.
  Autenticação via `AWSV4SignerAuth` + `boto3.Session().get_credentials()` — cadeia padrão
  AWS (IAM role → env vars → `~/.aws/`). Zero credenciais hardcoded.
  Factory `from_env()` lê `OPENSEARCH_ENDPOINT`, `OPENSEARCH_INDEX`, `OPENSEARCH_REGION`,
  `OPENSEARCH_SERVICE` de variáveis de ambiente.
  Helpers privados `_build_knn_query` e `_parse_hit` isolam o DSL do OpenSearch.
  `search_macro_context` nunca propaga exceções — retorna `[]` com log estruturado
  (Controlled Degradation).

* [x] **Passo 3 — Refatoração do `macro_agent` para o Fluxo HyDE (Pipeline RAG):**
  Refatorar `src/agents/macro.py` introduzindo `create_macro_agent(vector_store: VectorStorePort)`
  como factory que retorna o nó LangGraph com DI por closure.
  Pipeline de três estágios:
  - **Stage 1 (HyDE):** `_HYDE_PROMPT | llm` gera documento hipotético COPOM/FED em texto puro.
    Sem `with_structured_output` para preservar densidade semântica máxima.
  - **Stage 2 (Retrieval):** `vector_store.search_macro_context(hyde_text, top_k=5)` realiza
    busca k-NN. O documento hipotético é o vetor de consulta.
  - **Stage 3 (Síntese):** `_SYNTHESIS_PROMPT | llm.with_structured_output(MacroAnalysis)`
    gera análise estruturada grounded no contexto recuperado.
  `source_urls` injetados deterministicamente via `model_copy(update={"source_urls": urls})`
  após o retrieval — nunca alucinados pelo LLM (Zero Hallucination).
  `_build_audit_trace` registra score de cosseno e fonte de cada documento selecionado.
  `macro_agent` module-level usa `NullVectorStore` para compatibilidade retroativa.

* [x] **Passo 4 — Wiring DI no Grafo:**
  Atualizar `src/core/graph.py` com `_resolve_vector_store()`: tenta `OpenSearchAdapter.from_env()`,
  faz fallback para `NullVectorStore` com warning estruturado se `OPENSEARCH_ENDPOINT` ausente.
  `macro_agent = create_macro_agent(_resolve_vector_store())` preserva o nome no namespace
  do módulo para manter `patch("src.core.graph.macro_agent")` funcional nos testes.

* [x] **Passo 5 — Cobertura de Testes (TDD):**
  Criar `tests/test_macro_agent.py` com **13 testes** cobrindo:
  - Success path (HyDE → retrieval → síntese com `source_urls` reais).
  - Controlled Degradation por retrieval vazio (`NullVectorStore`).
  - Deduplicação de `source_urls`.
  - Fallback por falha de LLM (`ResourceExhausted` e `RuntimeError`).
  - Falha de conexão OpenSearch (`ConnectionError`) — sem propagação de exceção.
  - Timeout OpenSearch (`TimeoutError`) — garantia anti-Death Loop no LangGraph.
  - Helpers privados: `_extract_source_urls`, `_format_retrieved_context`, `_build_audit_trace`.
  - Conformidade de protocolo: `isinstance(NullVectorStore(), VectorStorePort)`.
  Expandir `tests/test_graph.py` com **+2 testes de DI**:
  - Fallback para `NullVectorStore` quando `OPENSEARCH_ENDPOINT` ausente.
  - `AgentState` recebido pelo macro contém `metrics` e `qual_analysis` populados.
  **Resultado: 40 passed, 0 regressões** (09/03/2026).

---

## 📌 Próxima Sprint — Em Execução

---

### 📌 Sprint 3.3 — Provisionamento OpenSearch Serverless + Indexação Real
**Status:** PLANEJADA — Iniciar na próxima sessão SOD.

* [ ] **Passo 1 — Terraform (AWS OpenSearch Serverless):**
  Criar módulo Terraform em `infra/terraform/opensearch/` com collection `aequitas-macro-docs`,
  política de acesso OIDC restrita ao role de execução e pipeline de embedding (neural search).
  Target environment: `dev`. Sem `terraform apply` automático em CI (Observação aws-advisor §4).

* [ ] **Passo 2 — Script de Indexação Inicial:**
  Criar `src/tools/opensearch_indexer.py`. Script de ingestão das atas do COPOM 2024-2025
  (BCB) e minutes do FED, com geração de embeddings via Bedrock ou SageMaker.
  Campos obrigatórios: `content`, `source_url`, `document_id`, `published_at`.

* [ ] **Passo 3 — Configuração de Ambiente `dev`:**
  Adicionar `OPENSEARCH_ENDPOINT`, `OPENSEARCH_INDEX`, `OPENSEARCH_REGION` nas variáveis
  de ambiente do ambiente `dev` (AWS Secrets Manager ou GitHub Actions env secrets).

* [ ] **Passo 4 — Teste E2E com Retrieval Real:**
  Executar `macro_agent` com `OpenSearchAdapter` real apontando para o índice `dev`.
  Validar que `source_urls` retorna URLs reais do BCB/FED e que `audit_log` registra
  scores de cosseno reais (> 0.0).

* [ ] **Passo 5 — Validação Final da Suite e PR:**
  `pytest tests/` com 40+ testes passando após integração com OpenSearch real.
  Abrir PR `feat/macro-hyde-opensearch-integration` → `development` para revisão do Tech Lead.
