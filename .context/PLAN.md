# 🗺️ PLAN: Execução de Engenharia — Aequitas-MAS

## Estado Atual Consolidado

O baseline arquitetural vigente do repositório já entrega:

- **Cyclic Graph / Iterative Committee** com a ordem:
  `graham -> fisher -> macro -> marks -> core_consensus -> __end__`
- **AgentState** como estado canônico, imutável e tipado, com `as_of_date`
  como boundary temporal explícita
- **HyDE retrieval flow** com `VectorStorePort -> list[VectorSearchResult]`
  e retrieval time-aware
- **Otimização determinística** via
  `optimize_portfolio(...) -> Optional[PortfolioOptimizationResult]`
- **Secret management cloud-first** via
  `SecretStorePort` e `EnvSecretAdapter`
- **FastAPI gateway** com DI do grafo compilado e do `BaseCheckpointSaver`
- **Backtesting determinístico** com anti-look-ahead, degradação para `None`
  e logs fundamentais enriquecidos
- **B3HistoricalFetcher** integrado ao replay histórico determinístico como
  adapter real de ingestão
- **Active `/backtest/run` endpoint** wired to the deterministic ingestion path
- **Temporal invariance governance** formalized by
  `[.ai/adr/011-point-in-time-architecture-and-temporal-invariance.md]`

## Sprint 6 — API Gateway & Boundary Hardening
**Status:** DONE

### Entregas consolidadas

1. `src/api/` entregue com:
   - `POST /analyze`
   - `POST /backtest/run`
2. Dependências compartilhadas do gateway resolvidas por providers:
   - `get_graph_app()`
   - `get_checkpointer()`
3. Contratos HTTP tipados por modelos Pydantic imutáveis:
   - `AnalyzeRequest`
   - `AnalyzeResponse`
   - `BacktestRequest`
   - `BacktestResult`
4. Hardening de fronteiras concluído:
   - `VectorSearchResult`
   - `PortfolioOptimizationResult`
   - patch tipado de `core_consensus_node`
5. Secret management desacoplado do domínio via:
   - `SecretStorePort`
   - `EnvSecretAdapter`
6. Backtesting determinístico entregue em `src/tools/backtesting/` com:
   - `HistoricalDataLoader`
   - métricas determinísticas
   - `BacktestEngine`

## Sprint 7 — Real Data Ingestion & Dynamic Constraints
**Status:** DONE

### Objetivo

Substituir a carga sintética/local do backtesting por ingestão histórica real e
introduzir restrições dinâmicas de alocação sem violar Risk Confinement,
Controlled Degradation ou Zero Trust.

### Entregas consolidadas

#### Passo 1 — Real Historical Data Adapter — DONE
- `B3HistoricalFetcher` implementado como adapter determinístico para ingestão
  histórica real compatível com o mercado brasileiro
- `HistoricalMarketData` consolidado como boundary imutável para:
  - `price`
  - `book_value_per_share`
  - `earnings_per_share`
  - `selic_rate`
- `AgentState.as_of_date` promovido a boundary temporal de primeira classe
- retrieval qualitativo propagado com `as_of_date` em `VectorStorePort`,
  adapter OpenSearch e agentes qualitativos

#### Passo 1.1 — Backtest Engine Integration — DONE
- `HistoricalDataLoader` refatorado para injetar `B3HistoricalFetcher` via DI
- `HistoricalDataLoader.get_market_data_as_of(...)` exposto como contrato
  principal de replay point-in-time
- `BacktestEngine` atualizado para consumir dados fundamentais completos
- `BacktestStepLog` enriquecido com:
  - `observed_price`
  - `vpa`
  - `lpa`
  - `selic_rate`
- `/backtest/run` ativado no gateway com wiring determinístico de ponta a ponta

### Definition of Done — Sprint 7

- ingestão histórica real conectada ao backtester
- engine de backtest consumindo dados fundamentais point-in-time
- benchmark e fatores externos integrados com anti-look-ahead
- restrições dinâmicas formalizadas fora do caminho LLM
- novos contratos tipados documentados e testados
- nenhuma regressão em anti-look-ahead ou Controlled Degradation

## Sprint 8 — Portfolio API & Resilient Graph Integration
**Status:** DONE

### Objetivo

Finalizar a boundary do otimizador determinístico e integrá-la ao supervisor
do grafo sem permitir cálculo financeiro no caminho LLM.

### Entregas consolidadas

1. `POST /portfolio` entregue no gateway FastAPI com contratos tipados para:
   - universo ordenado de tickers B3
   - matriz de retornos validada na boundary
   - constraints determinísticas opcionais
2. Hardening da API concluído com:
   - normalização defensiva de tickers
   - reshape explícito de série 1D para matriz `observations x 1`
   - mensagens estáveis em pt-BR para falhas do otimizador
3. `core_consensus_node` endurecido para:
   - bloquear otimização ao faltar `portfolio_returns` ou `risk_appetite`
   - bloquear otimização quando o tool falha ou degrada para `None`
   - retornar patch imutável e auditável com `optimization_blocked=True`
4. Artefatos operacionais consolidados em `.ai/handoffs/` para fechamento da Sprint 8.

### Definition of Done — Sprint 8

- endpoint `/portfolio` ativo fora do caminho LLM
- contratos HTTP alinhados ao comportamento do tool determinístico
- `core_consensus_node` falhando fechado com rastreabilidade explícita
- documentação ativa refletindo Blackboard Architecture sem resquícios do fluxo RPI
