# 🎯 Project Status: Aequitas-MAS

## ✅ Sprint Concluída: 3.2 - Agente Macro e RAG HyDE (OpenSearch)
**Status:** DONE — Entregue em 09/03/2026. Branch: `feat/macro-hyde-opensearch-integration`. Commit: `1e27dea`.

### 🛠️ Objetivos Entregues

1. **[x] Integração OpenSearch (Prioridade 1):** Pipeline HyDE de dois estágios implementado em `src/agents/macro.py`.
   - Stage 1: LLM gera documento hipotético COPOM/FED (`_HYDE_PROMPT` — texto puro, sem *structured output*).
   - Stage 2: Documento hipotético usado como query semântica via `VectorStorePort.search_macro_context(hyde_text, top_k=5)`.
   - Stage 3: LLM sintetiza `MacroAnalysis` grounded no contexto recuperado.

2. **[x] Rastreabilidade Ética:** `source_urls` preenchido deterministicamente via `_extract_source_urls(retrieved_docs)` e injetado com `model_copy(update={"source_urls": dynamic_urls})` — nunca alucinado pelo LLM. `audit_log` registra score de cosseno e URL de cada documento selecionado.

3. **[x] Confinamento de Infraestrutura (DIP):** `boto3` e `opensearch-py` confinados exclusivamente em `src/infra/adapters/opensearch_client.py`. O agente depende apenas de `VectorStorePort` (`src/core/interfaces/vector_store.py`). Varredura confirmou zero SDKs de infra em `src/agents/`.

### ✅ Definition of Done (DoD)

- [x] `macro_agent` realizando *retrieval* dinâmico com base no vetor de similaridade via `OpenSearchAdapter` (produção) ou `NullVectorStore` (local/offline).
- [x] Histórico de execução validado sem alucinações: `Optional[float] = None` enforced para `interest_rate_impact` e `inflation_outlook` quando não há dados explícitos no contexto recuperado. Testado em `test_macro_agent_empty_retrieval_controlled_degradation` e `test_macro_agent_opensearch_connection_failure_degrades_gracefully`.
- [x] Grafo executado de ponta a ponta (`pytest tests/test_graph.py`) — **9 passed**, incluindo testes de DI do nó macro. Suite completa: **40 passed, 0 regressões** (09/03/2026).

### 📊 Cobertura de Testes Adicionada

| Arquivo | Testes | Cobertura |
|---|---|---|
| `tests/test_macro_agent.py` | 13 | Pipeline HyDE, degradação, falha de conexão, helpers privados, conformidade de protocolo |
| `tests/test_graph.py` | +2 | DI do VectorStorePort, shape do AgentState recebido pelo macro |

---

## 📌 Próxima Sprint: 3.3 - Provisionamento OpenSearch e Teste End-to-End Real

**Foco:** Configurar o índice OpenSearch Serverless, indexar documentos reais (atas BCB/FED) e executar o pipeline HyDE+RAG com retrieval real.

### 🛠️ Objetivos da Próxima Sessão (SOD)

1. **Provisionamento AWS (Terraform):** Criar domínio OpenSearch Serverless com collection `aequitas-macro-docs`, política de acesso OIDC e pipeline de embedding (neural search).
2. **Indexação Inicial:** Script de ingestão das atas do COPOM (BCB) e FED com geração de embeddings via SageMaker ou Bedrock.
3. **Teste E2E Real:** Configurar `OPENSEARCH_ENDPOINT` no ambiente `dev` e executar `macro_agent` com retrieval real, validando `source_urls` preenchidos com URLs reais do BCB/FED.
4. **Validação de `audit_log`:** Confirmar que o score de cosseno retornado pelo OpenSearch real é registrado corretamente no `audit_log`.

### ✅ Definition of Done (DoD)

- [ ] Domínio OpenSearch Serverless provisionado via Terraform (`dev`).
- [ ] Ao menos 10 documentos indexados com embeddings (atas COPOM 2024-2025).
- [ ] `macro_agent` executando com `OPENSEARCH_ENDPOINT` configurado e retornando `source_urls` com URLs reais.
- [ ] `pytest tests/` — 40+ testes passando após integração com OpenSearch real.
