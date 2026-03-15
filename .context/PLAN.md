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

### ✅ Sprint 4 — Core Agent & Portfolio Optimization
**Status:** CONCLUÍDA — Merge ready.

* [x] **Passo 1 — ADR 008 + Math Isolation em `portfolio_optimizer.py`:**
  Formalizar ADR 008 para delegar portfolio weighting a uma deterministic math tool.
  Implementar `src/tools/portfolio_optimizer.py` com `scipy.optimize.minimize`
  (`SLSQP`) e isolamento completo da matemática de portfólio fora do fluxo de LLM.

* [x] **Passo 2 — Explicit Ledger Routing em `src/core/graph.py` + `src/core/state.py`:**
  Atualizar `AgentState` com `executed_nodes`, `marks_verdict`, `portfolio_tickers`,
  `portfolio_returns` e `risk_appetite` para suportar roteamento explícito e handoff
  determinístico ao otimizador.
  Refatorar o `router` em `src/core/graph.py` para avançar por checkpoints explícitos
  (`graham -> fisher -> macro -> marks -> core_consensus -> __end__`) sem depender
  exclusivamente de `audit_log` ou `AIMessage.name`.

* [x] **Passo 3 — Implementação do `core_consensus` Node em `src/agents/core.py`:**
  Criar `src/agents/core.py` com `core_consensus_node` para structured synthesis dos
  Decision Tensors (`metrics`, `qual_analysis`, `macro_analysis`, `marks_verdict`) e
  gatilho controlado do `optimize_portfolio`.
  O nó bloqueia a etapa de otimização quando faltam evidências ou inputs determinísticos,
  preservando Controlled Degradation e Risk Confinement.

* [x] **Passo 4 — Deterministic Test Coverage para routing + consensus logic:**
  Reestruturar a suíte de grafo em `tests/test_graph.py`, `tests/test_graph_routing.py`
  e `tests/test_core_consensus_node.py` com `unittest.mock.patch` para validar
  transições de estado e consenso sem chamadas reais de LLM, OpenSearch ou SciPy fora
  da camada apropriada.
  **Resultado: 35 passed + `ruff check` green** na validação da integração.

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

### 📌 Sprint 5 — Observability, Telemetry & RAG Quality
**Status:** ACTIVE

#### Objective
Strengthen operational reliability for Aequitas-MAS by adding a searchable Decision Path
audit trail, graph-level telemetry, deterministic RAG quality scoring, and automated
architectural dogma enforcement in CI/CD.

#### Step 1 — AuditSinkPort + OpenSearch TIMESERIES Ingestion
- **File(s):** `src/core/interfaces/`, `src/infra/adapters/`, `infra/terraform/opensearch.tf`,
  `infra/terraform/variables.tf`
- **Change:** Establish an `AuditSinkPort` interface so `src/agents/` and `src/core/`
  emit structured audit events without importing cloud SDKs. Implement an infrastructure
  adapter in `src/infra/adapters/` that routes `structlog` JSON events to a dedicated
  OpenSearch Serverless `TIMESERIES` collection for Decision Path analytics, separate
  from the existing `VECTORSEARCH` RAG collection.
- **Dogma check:** Preserve DIP by keeping AWS/OpenSearch dependencies outside
  `src/agents/` and `src/core/`. No math logic in the logging path.
- **Tests:** Add adapter-level tests with mocked transport boundaries and graph-level
  tests confirming the supervisor can emit audit events without network calls.

#### Step 2 — OpenTelemetry Instrumentation for LangGraph Routing
- **File(s):** `src/core/graph.py`, `src/agents/`, `src/core/state.py` (only if trace
  correlation metadata becomes necessary)
- **Change:** Instrument the Specialists -> Marks -> Consensus execution path with
  OpenTelemetry spans. Capture node latency, degradation paths, and external dependency
  timing for retrieval and LLM synthesis, with particular focus on Fisher and Macro RAG
  bottlenecks.
- **Dogma check:** Telemetry must remain observational only. No routing decisions may
  depend on span exporters or network availability.
- **Tests:** Add deterministic tests for span creation and correlation metadata using
  mock exporters or in-memory span processors only.

#### Step 3 — Deterministic RAG Evaluator with Aequitas Calibration
- **File(s):** `src/tools/`, `src/core/state.py`, `src/agents/core.py`, `tests/`
- **Change:** Implement a deterministic RAG evaluation tool for `FisherAnalysis` and
  `MacroAnalysis`, producing a confidence metric `C_rag` grounded on:
  `w_f = 0.60`, `w_r = 0.30`, `w_s = 0.10`, where Faithfulness, Answer Relevance, and
  Retrieval Support are evaluated outside the LLM reasoning path. Append the resulting
  confidence signal to the supervisor-facing consensus state.
- **Dogma check:** The score must be computed by deterministic tooling, not by free-form
  LLM arithmetic. Any numeric outputs must continue to use `Optional[float] = None`
  semantics when evidence is absent.
- **Tests:** Add isolated tests for metric computation, degraded-context behavior,
  and state handoff into the Core supervisor.

#### Step 4 — Semgrep CI Enforcement for Architectural Dogmas
- **File(s):** `.github/workflows/pipeline.yml`, `.semgrep/` (new), optional docs in
  `.context/`
- **Change:** Integrate Semgrep into CI/CD to enforce architectural dogmas that exceed
  basic grep coverage, including bans on `decimal`, `scipy`, and other deterministic math
  libraries inside `src/agents/`, plus prohibited infrastructure imports in the domain
  layer. Keep the existing grep audits as a fast first-pass control.
- **Dogma check:** Enforcement rules must reinforce Risk Confinement and DIP without
  blocking approved tool-layer usage in `src/tools/` or adapter-layer usage in
  `src/infra/adapters/`.
- **Tests:** Validate the ruleset with positive and negative fixtures before making the
  Semgrep job merge-blocking.

---

### 📌 Sprint 6 — API Gateway & Backtesting
**Status:** PLANNED

#### Objective
Expose the Aequitas Core workflow through a FastAPI gateway and deliver a deterministic
backtesting foundation that replays historical signals without look-ahead bias, while
preserving LangGraph checkpointing, Risk Confinement, and Controlled Degradation.

#### Step 1 — FastAPI Gateway Foundation + Checkpointer Dependency Injection
- **File(s):** `src/api/`, `src/core/graph.py`, `src/core/interfaces/`,
  `src/infra/adapters/`
- **Change:** Introduce a FastAPI application boundary with lifespan-managed dependency
  providers for the compiled LangGraph app and its `BaseCheckpointSaver` implementation.
  The API layer must resolve the concrete checkpointer once at startup (`MemorySaver` for
  local/CI, `DynamoDBSaver` for cloud environments) and inject the compiled graph through
  typed providers instead of constructing persistence objects inside route handlers.
- **Dogma check:** No cloud SDK imports in `src/api/` or `src/core/`. Route handlers must
  depend on interfaces/providers only, not `boto3` or adapter internals.
- **Tests:** Add API dependency tests confirming the graph app reuses a shared
  checkpointer and propagates `configurable.thread_id` deterministically.

#### Step 2 — Endpoint Surface for Analysis, Portfolio, and Backtesting
- **File(s):** `src/api/app.py`, `src/api/dependencies.py`, `src/api/routers/`,
  `src/api/schemas.py`, `tests/`
- **Change:** Deliver the initial HTTP surface with:
  - `POST /analyze` for single-ticker supervisor execution.
  - `POST /portfolio` for deterministic portfolio optimization handoff.
  - `POST /backtest/run` for synchronous historical replay against a defined date range.
  Optional operational endpoints such as `GET /health` or `GET /backtest/{run_id}` may be
  added only if they remain read-only and do not dilute the initial delivery.
- **Dogma check:** API request/response schemas must preserve `Optional[float] = None`
  semantics for any missing financial or historical values.
- **Tests:** Add FastAPI `TestClient` coverage for request validation, dependency wiring,
  and degraded responses without invoking real AWS or LLM services.

#### Step 3 — Deterministic Backtesting Engine Skeleton in `src/tools/backtesting/`
- **File(s):** `src/tools/backtesting/`, `tests/`
- **Change:** Structure the tool layer with deterministic modules such as:
  - `data_loader.py` for ordered historical price retrieval,
  - `signal_adapter.py` for translating Aequitas signals into replayable positions,
  - `portfolio_simulator.py` for time-stepped account evolution,
  - `metrics.py` for post-run analytics,
  - `engine.py` for orchestration.
  The architecture should follow the strongest reusable patterns found in the FinRL
  ecosystem: explicit data layer, time-driven simulation, post-run metrics, and benchmark
  comparison; while keeping the higher-level multi-signal orchestration aligned with the
  publicly documented MarketSenseAI approach of combining news, fundamentals, price
  dynamics, and macro signals before portfolio construction.
- **Dogma check:** All backtesting math remains in `src/tools/backtesting/`. The LLM path
  may describe strategy rationale but must not compute returns, weights, or benchmarks.
- **Tests:** Add isolated unit tests for simulator determinism, missing-data degradation,
  and reproducible metrics from synthetic input series.

#### Step 4 — Historical Data Feeding Strategy and Anti-Look-Ahead Guardrails
- **File(s):** `src/tools/backtesting/`, `src/core/state.py`, `src/api/schemas.py`,
  `tests/`
- **Change:** Formalize an `as_of_date` replay contract so the backtester consumes only
  observations available up to each timestamp. Historical feeds must be sorted
  chronologically, windowed by explicit `start_date` and `end_date`, and split into
  training/selection/backtest ranges where applicable. Missing price or feature points
  must degrade to `Optional[float] = None` rather than being forward-filled by the LLM.
- **Dogma check:** No synthetic future interpolation, no prompt-based numeric estimation,
  and no hidden reordering of bars that could introduce look-ahead bias.
- **Tests:** Add fixtures proving that future rows are inaccessible during replay, and
  that missing observations propagate as `None` without crashing the engine.

#### Component Architecture
- **API Layer:** FastAPI routers call typed dependency providers and never instantiate
  infrastructure clients directly.
- **Application Layer:** The compiled LangGraph app remains the orchestration authority for
  live analysis requests, receiving `thread_id` from `RunnableConfig`.
- **Tool Layer:** The backtesting engine lives entirely under `src/tools/backtesting/`
  with deterministic, testable modules.
- **Infrastructure Layer:** Checkpointers and historical-data adapters remain confined to
  `src/infra/adapters/`.

#### Data Flow (LangGraph State Mutations + Backtesting Handoff)
1. `POST /analyze` receives a ticker and runtime options, resolves the shared graph app,
   and invokes LangGraph with `configurable.thread_id`.
2. Live analysis mutates `AgentState` through the existing specialist -> auditor ->
   supervisor path and returns structured checkpoints.
3. `POST /backtest/run` loads historical bars in strictly ordered slices, converts the
   replay context into deterministic signal inputs, and runs the simulator step-by-step.
4. Backtest outputs produce metrics and traces without mutating LangGraph checkpoints with
   future information.

#### Controlled Degradation
- Missing historical prices, sparse fundamentals, or incomplete benchmark series MUST map
  to `Optional[float] = None` at the schema boundary.
- A replay window with partial data may still complete if the simulator can skip or mark
  the affected timestep without fabricating numbers.
- If a required benchmark or price series is entirely unavailable, the backtest must fail
  fast with a typed validation error at the API boundary rather than inventing fallback
  values.

#### Definition of Done
- FastAPI gateway delivered with DI-safe graph/checkpointer providers.
- Endpoint contract implemented for `/analyze`, `/portfolio`, and `/backtest/run`.
- Deterministic backtesting modules created under `src/tools/backtesting/`.
- Historical replay contract documented and covered by anti-look-ahead tests.
