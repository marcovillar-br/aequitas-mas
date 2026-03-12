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

## 📋 Plano Aprovado — Formalização Arquitetural (Prep Sprint 3.3)

> **Status:** APROVADO pelo Tech Lead em 10/03/2026.
> Decisões executivas registradas. Pronto para `/implement`.

---

### Objetivo
Formalizar decisões arquiteturais descobertas na auditoria de 10/03/2026 criando os ADRs 005, 006 e 007, e aplicar os patches necessários em CI e infraestrutura Terraform.

---

### Step 1 — Criar ADR 005: HyDE RAG Pipeline
- **File(s):** `.ai/adr/005-hyde-rag-pipeline.md`
- **Change:** Formalizar a decisão de usar HyDE (Generate → k-NN) em vez de RAG direto. Registrar trade-off: +1 LLM call + latência vs. precisão semântica institucional (MarketSenseAI alignment).
- **Dogma check:** Documento apenas. CLEAN.
- **Tests:** N/A.

### Step 2 — Criar ADR 006: OpenSearch Shared Collection Strategy ⚠️ Confirmar antes de executar Step 5
- **File(s):** `.ai/adr/006-opensearch-shared-collection.md`
- **Change:** Formalizar Opção B — coleção compartilhada `aequitas-vector-store` com índices separados por agente (`fisher-index`, `macro-index`). Resolve bloqueador da Sprint 3.3.
- **Dogma check:** Documento apenas. CLEAN.
- **Tests:** N/A.

### Step 3 — Criar ADR 007: Dogma Audit via Grep Estático
- **File(s):** `.ai/adr/007-dogma-audit-grep-strategy.md`
- **Change:** Formalizar grep estático como estratégia pragmática para MVP. Documentar limitação de alias imports como dívida técnica. Registrar decisão de expandir regex neste sprint.
- **Dogma check:** Documento apenas. CLEAN.
- **Tests:** N/A.

### Step 4 — Patch CI: Expandir Regex dos Dogma Audits ⚠️ Confirmar antes de executar
- **File(s):** `.github/workflows/pipeline.yml`
- **Change:** Audit 1 — adicionar padrão para alias de Decimal (`from decimal import.*Decimal.*as`). Audit 2 — adicionar padrão para alias de boto3 (`import boto3.*as`). Padrões existentes preservados.
- **Dogma check:** Alteração defensiva no CI, sem impacto em `src/`. CLEAN.
- **Tests:** Validação: `grep -E` nos padrões expandidos deve retornar vazio na suite atual antes do merge.

### Step 5 — Refatorar Terraform: Shared Collection + Separate Indices ⚠️ Confirmar antes de executar. Sem `terraform apply` automático.
- **File(s):** `infra/terraform/opensearch.tf`, `infra/terraform/variables.tf`
- **Change:** Renomear recursos de `AQM_FISHER_*` → `AQM_VECTOR_STORE_*`. Collection: `aequitas-vector-store-${terraform.workspace}`. Adicionar variável `opensearch_index` em `variables.tf` para isolamento lógico por agente (Fisher: `fisher-index`, Macro: `macro-index`). Policies de criptografia/rede/acesso compartilhadas na collection única.
- **Dogma check:** Infra pura — fora de `src/agents/` e `src/core/`. CLEAN.
- **Tests:** `terraform validate` (job CI existente). `terraform plan` manual supervisionado pelo Tech Lead antes de qualquer `apply`.

---

## Next Sprint Execution

---

### ✅ Sprint 3.3 — OpenSearch Serverless + Real Indexing
**Status:** DELIVERED

#### Completed Tasks
* [x] **Step 1 — Terraform (AWS OpenSearch Serverless):**
  Refactored Terraform for shared collection strategy (`aequitas-vector-store`) with
  separate logical indices and policy hardening for dev validation.

* [x] **Step 2 — Initial Indexing Script:**
  Implemented `src/tools/opensearch_indexer.py` with deterministic payload structure and
  mandatory fields: `content`, `source_url`, `document_id`, `published_at`.

* [x] **Step 3 — dev Environment Configuration:**
  Standardized local/dev setup via `scripts/setup_env.sh` and documented environment variables
  (`OPENSEARCH_ENDPOINT`, `OPENSEARCH_INDEX`, `OPENSEARCH_REGION`, `GEMINI_API_KEY`).

* [x] **Step 4 — Real E2E Retrieval Test:**
  Validated Macro Agent retrieval against OpenSearch Serverless with real cosine scores
  logged in `audit_log`, plus deterministic `source_urls` injection.

* [x] **Step 5 — Final Validation and Integration Readiness:**
  Confirmed retrieval stability after migrating from neural query mode to explicit `knn`
  query mode using local Gemini query vectorization.

#### Key Achievements
1. ADR 005, ADR 006, and ADR 007 were implemented and operationalized.
2. AWS OpenSearch `500` retrieval failure was resolved by explicit index mapping:
   `content_embedding` as `knn_vector` with dimension `3072` and `cosinesimil`.
3. Retrieval architecture migrated to explicit `knn` queries with local Gemini embedding
   generation for HyDE query text.
4. E2E fallback behavior validated Zero Hallucination (`Optional[float] = None`) when
   numeric evidence is not explicitly present in retrieved context.

---

### 📌 Sprint 4 — Core Agent & Portfolio Optimization
**Status:** PLANNED

#### Step 1 — ADR 008: Portfolio Optimization Tool Strategy
- **File(s):** `.ai/adr/008-portfolio-optimization-tool-strategy.md`
- **Change:** Formalize the deterministic optimization strategy (e.g., `scipy.optimize`
  or PyPortfolioOpt), trade-offs, and strict Risk Confinement boundaries.
- **Dogma check:** Documentation only. CLEAN.
- **Tests:** N/A.

#### Step 2 — Deterministic Tool Implementation
- **File(s):** `src/tools/portfolio_optimizer.py`
- **Change:** Implement a pure Python deterministic optimizer for Markowitz Efficient
  Frontier calculations.
- **Dogma check:** LLM MUST NOT perform portfolio mathematics; tool executes all math.
- **Tests:** Required in Step 4.

#### Step 3 — Aequitas Core Node Integration
- **File(s):** `src/core/graph.py`, `src/agents/` (core supervisor integration points)
- **Change:** Implement Aequitas Core (Supervisor) routing to gather consensus from
  Graham, Fisher, Macro, and Marks, then invoke `portfolio_optimizer`.
- **Dogma check:** Preserve DIP and immutable state transitions.
- **Tests:** Routing behavior validated without real LLM API calls.

#### Step 4 — Shift-Left Testing for Math Tool
- **File(s):** `tests/test_portfolio_optimizer.py` (new)
- **Change:** Add isolated pytest coverage for deterministic optimizer behavior,
  constraints, edge cases, and controlled degradation outputs.
- **Dogma check:** No stochastic dependencies in math tests.
- **Tests:** Mandatory before merge.
