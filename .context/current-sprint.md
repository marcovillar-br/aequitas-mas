# 🎯 Project Status: Aequitas-MAS

---

# 🎯 Project Status: Aequitas-MAS

---

## 🔄 Sprint Ativa: 3.3 — Provisionamento OpenSearch e Teste End-to-End Real
**Status:** IN PROGRESS — Iniciada em 10/03/2026. Branch: `feat/macro-hyde-opensearch-integration` (PR pendente para `development`).

### 🛠️ Objetivos da Sessão SOD (Amanhã)

1. **Provisionamento AWS (Terraform):**
   Refatorar e aplicar domínio OpenSearch Serverless. O script `opensearch.tf` atual mapeou o *Agente Fisher* (`aqm-fisher`), necessitando ajuste para a collection `aequitas-macro-docs` (Macro) ou abstração para suportar ambos.
   Restrição: Sem `terraform apply` automático em CI — execução manual supervisionada pelo Tech Lead.

2. **Script de Ingestão (Isomorfismo BCB/FED):**
   Criar `src/tools/opensearch_indexer.py` — script Python isomorfo para indexar atas do COPOM (BCB) e *minutes* do FED com geração de embeddings.
   Campos obrigatórios por documento: `content`, `source_url`, `document_id`, `published_at`.

3. **Integração E2E Real:**
   Configurar `OPENSEARCH_ENDPOINT` no ambiente `dev` e executar `macro_agent` com retrieval real.
   Validar `source_urls` e `audit_log` registrando scores de cosseno > 0.0.

### 🚧 Impedimentos / Débitos Técnicos (Check-out 10/03/2026)
* **Desalinhamento Terraform:** O provisionamento AWS em `infra/terraform/opensearch.tf` foi construído visando o escopo do Fisher (`aqm-fisher`) em vez do Macro. Ação necessária no próximo SOD: duplicar/refatorar o `.tf` para garantir suporte à coleção `aequitas-macro-docs`.
* **Script de Ingestão Pendente:** A estrutura da AWS está sendo levantada, mas o injetor de vetores não foi desenvolvido hoje.

### ✅ Definition of Done (DoD)

- [ ] Domínio OpenSearch Serverless provisionado via Terraform (`dev`) com collection `macro` correta.
- [ ] Ao menos 10 documentos indexados com embeddings (atas COPOM 2024-2025).
- [ ] `macro_agent` executando com `OPENSEARCH_ENDPOINT` real.
- [ ] `pytest tests/` — 40+ testes passando.
- [ ] PR `feat/macro-hyde-opensearch-integration` → `development` aprovado.
---

## ✅ Histórico — Sprint 3.2: Agente Macro e RAG HyDE (OpenSearch)
**Status:** DONE — Entregue em 09/03/2026. Branch: `feat/macro-hyde-opensearch-integration`. Commits: `1e27dea` → `d94ab5b`.

### 🛠️ Objetivos Entregues

- [x] **Integração OpenSearch (Substituição de mocks por adaptador real):**
  Pipeline HyDE de três estágios implementado em `src/agents/macro.py`. O mock generativo
  foi substituído por chamada real ao adaptador vetorizado via `VectorStorePort`:
  - Stage 1: LLM gera documento hipotético COPOM/FED (`_HYDE_PROMPT` — texto puro, sem *structured output*).
  - Stage 2: Documento hipotético usado como query k-NN via `VectorStorePort.search_macro_context(hyde_text, top_k=5)`.
  - Stage 3: LLM sintetiza `MacroAnalysis` grounded no contexto recuperado do OpenSearch.
  `OpenSearchAdapter.from_env()` consome `OPENSEARCH_ENDPOINT` e autentica via AWS SigV4.
  `NullVectorStore` garante execução local sem infraestrutura (Controlled Degradation).

- [x] **Rastreabilidade Ética (Preenchimento de `source_urls` no schema `MacroAnalysis`):**
  `source_urls` preenchido deterministicamente a partir dos metadados do retrieval via
  `_extract_source_urls(retrieved_docs)` e injetado com
  `raw_result.model_copy(update={"source_urls": dynamic_urls})` — nunca alucinado pelo LLM.
  `audit_log` registra score de cosseno e URL de cada documento selecionado pelo critério HyDE.

- [x] **Confinamento de Infraestrutura (DIP aplicado via `/src/infra/adapters/`):**
  `import boto3` e `from opensearchpy import ...` confinados exclusivamente em
  `src/infra/adapters/opensearch_client.py`. Auditoria estática confirmou zero SDKs de
  infraestrutura em `src/agents/`. `VectorStorePort` injetado via `create_macro_agent(vector_store)`.

- [x] **Correções de Code Review (GitHub Copilot):**
  Prompts HyDE e síntese reescritos em English (`coding-guidelines §1`). `Optional` não
  utilizado removido (`Ruff F401`). `-> VectorStorePort` e `ImportError` adicionados ao
  `_resolve_vector_store()`. Docstrings de testes traduzidos para English.

- [x] **Correções de Auditoria SOTA:**
  `Decimal` erradicado dos fixtures de teste (substituído por `float` literal).
  `RECURSION_LIMIT: int = 15` formalizado como constante nomeada em `graph.py`.
  `pytest-asyncio` adicionado ao grupo `dev`. `boto3`/`opensearch-py` movidos para grupo
  opcional `[infra]` em `pyproject.toml`.

### ✅ Definition of Done (DoD) — CONCLUÍDA

- [x] `macro_agent` realizando *retrieval* dinâmico via `OpenSearchAdapter` (produção) ou `NullVectorStore` (local/offline).
- [x] `Optional[float] = None` enforced para campos numéricos ausentes. Testado em 2 cenários de falha de conexão OpenSearch.
- [x] Suite completa: **40 passed, 0 regressões** (09/03/2026).
- [x] Auditoria SOTA aprovada: zero `🚨 Critical Blockers`, zero `⚠️ Warnings` remanescentes.

### 📊 Cobertura de Testes Adicionada

| Arquivo | Testes | Cobertura |
|---|---|---|
| `tests/test_macro_agent.py` | 13 | Pipeline HyDE, degradação, falha OpenSearch, helpers privados, protocolo |
| `tests/test_graph.py` | +2 | DI do VectorStorePort, shape do AgentState recebido pelo macro |
