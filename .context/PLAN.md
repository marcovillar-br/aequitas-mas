---
id: context-plan
title: "Plano de Execução de Engenharia — Aequitas-MAS"
status: active
last_updated: "2026-03-27"
tags: [context, plan, roadmap, academic, sprints, milestones]
---

# PLAN: Execução de Engenharia — Aequitas-MAS

## 1. Baseline Consolidado (Sprints 1–14)

Capacidades entregues e validadas no baseline:

### Sprints 1–8: Fundação Arquitetural
- **Orquestração:** LangGraph em modo Iterative Committee (`graham -> fisher -> macro -> marks -> core_consensus -> __end__`).
- **Estado:** `AgentState` imutável, tipado defensivamente e ancorado por `as_of_date`.
- **RAG macro:** Retrieval time-aware via `VectorStorePort`.
- **Dados históricos:** `B3HistoricalFetcher` e `HistoricalDataLoader` com degradação controlada.
- **Otimização:** tool determinístico isolado, consumido pelo `core_consensus_node` com fail-closed (`optimization_blocked=True`).
- **API:** FastAPI com fronteiras tipadas para `/analyze`, `/backtest/run` e `/portfolio`.
- **Segurança e infraestrutura:** credenciais via `SecretStorePort`, adapters desacoplados e disciplina Blackboard.

### Sprint 9: CoT Prompts & Quantitative Tools
- Piotroski F-Score e Altman Z-Score em `src/tools/fundamental_metrics.py`.
- Chain-of-Thought prompts para Graham, Fisher e Marks (`.ai/prompts/`).
- Intraday fallback com anti-look-ahead em `b3_fetcher.py`.
- `AuditStorePort` e `PresentationAdapter` boundaries.

### Sprint 10: AWS Serverless & Presentation
- `src/api/serverless.py` — Mangum handler para AWS Lambda.
- `PdfPresentationAdapter` determinístico (HTML-to-PDF mock).

### Sprint 11: Shift-Left CI/CD & DAIA
- Pipeline `feat/*` → `feature/*` fix + Dogma Audit 3 (`os.getenv` ban).
- Semgrep `dip-ban-os-getenv-in-agents` rule.
- DAIA edge cases: Piotroski all-None, Altman distress/safe, P/E negativo,
  covariância near-singular, retornos zero.
- Trust policy OIDC corrigida na AWS.
- **223 testes passando** (marco mais recente — Sprint 14).

### Sprint 12: Structured Output & Streaming
- `GrahamInterpretation` schema (`frozen=True`, confidence degradation).
- Todos os 5 agentes com `with_structured_output`.
- SSE `/analyze/stream` via `StreamingResponse` nativo.
- `core_consensus_node` recebe `graham_interpretation` tipado.
- `AnalyzeResponse` expõe `graham_interpretation` para Presentation Adapter.

### Sprint 13: Telemetry & Observability
- Request-scoped `structlog.contextvars` (thread_id + target_ticker).
- `__graph_summary__` DecisionPathEvent com `latency_ms`.
- `InstrumentedGraphApp` com `audit_sink` DI.
- Structured API logging (request/response com latency_ms).

### Sprint 14: CLI Observability, Presentation & Econometric Validation
- `structlog.dev.ConsoleRenderer` para ambiente local.
- `ThesisReportPayload` enriquecido (as_of_date, market_price, approval_status).
- Fail-fast router: ticker inválido pula Fisher/Macro/Marks.
- L10n pt-BR: recomendações, datas (DD/MM/YYYY), números (1.250,50).
- `src/tools/econometric.py`: OLS determinístico (Gujarati methodology).
- `EconometricResult` + `signal_significance` + `cross_validation` no `AgentState`.
- Audit warning quando `p_value > 0.05`.
- `cross_validate_agent_signals` (plumbing — aguardando score accumulator).
- **240 testes passando.**

---

## 2. Maturity Milestones Roadmap

O planejamento de longo prazo é agora organizado por marcos de maturidade
alinhados à grade de Pós-Graduação (UFG/USP ESALQ), sem hard-coupling a
meses específicos. A velocidade de entrega determina a progressão.

### v1.0 — Fundação Quantitativa ✅ DELIVERED
- Iterative Committee com tipagem estrita.
- Backtesting determinístico com anti-look-ahead.
- API Gateway com fronteiras tipadas.
- Risk Confinement end-to-end.

### v1.5 — Observability & Streaming ✅ DELIVERED
- Telemetria estruturada com correlação cross-cutting.
- SSE streaming para observação em tempo real.
- CI/CD shift-left com dogma enforcement automatizado.
- Structured output tipado em todos os agentes.
- Fail-fast router para tickets inválidos.

### v2.0 — Econometric Validation (NEXT)
*Alinhado com: EGI & AM (Econometria e Análise Multivariada)*
- Aplicar metodologia de Damodar Gujarati para provar significância
  estatística dos sinais HyDE RAG (Macro) e Fisher (Qualitativo).
- Implementar testes de hipótese (t-test, p-value) como ferramentas
  determinísticas em `src/tools/`.
- Validar que os sinais do comitê geram alpha sobre o benchmark (CDI/IBOV).

### v2.5 — Cyclic Graph Refinement
*Alinhado com: LLM & Agent*
- Aplicar ReAct e Tree-of-Thought (ToT) no `core_consensus_node`.
- Refinar o Agente Marks com reasoning estruturado.
- Regime-Aware Consensus (pesos dinâmicos por Selic).

### v3.0 — SOTA Factor Expansion
*Alinhado com: EAD (Educação a Distância / Expansão)*
- Integrar fatores quantitativos institucionais via Selenium/Pandas.
- Expandir `HistoricalMarketData` com novos indicadores.
- Semantic Chunking para Earnings Calls (MarketSenseAI).

### v4.0 — PA Defense & Final Thesis
*Alinhado com: PA (Projeto Aplicado)*
- Backtesting em larga escala na infra AWS.
- Formatação ABNT/USP-ESALQ.
- Paper final: Alpha vs Fórmula Mágica vs Ibovespa.

---

## 3. Cross-Cutting Engineering Track (AWS Serverless & FinOps)

Trilha paralela de infraestrutura. Progride conforme necessidade:

- **Lambda Deployment:** ✅ Mangum handler entregue (Sprint 10). Próximo:
  conectar DynamoDB e OpenSearch Serverless como persistência durável.
- **CI/CD Pipeline:** ✅ GitHub Actions com Terraform Plan/Apply e
  dogma audits automatizados (Sprint 11). Próximo: gates por ambiente
  (hom/prod) quando rollout iniciar.
- **Cloud Backtesting:** Pendente v4.0. Execução do backtest final na AWS.

---

## 4. Optional SOTA Backlog (If Time Permits)

- **XAI Dashboard:** Streamlit/Gradio consumindo FastAPI para visualizar
  LangGraph e CoT em tempo real na defesa.
- **Stress Testing:** Cenários de Cisne Negro (COVID-19, Joesley Day).
- **Graph-of-Thought / GraphRAG:** Prompting estruturado em grafos para
  causalidades econômicas complexas (Shao, 2024).
