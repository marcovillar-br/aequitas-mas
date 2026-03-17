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
**Status:** IN PROGRESS

### Objetivo

Substituir a carga sintética/local do backtesting por ingestão histórica real e
introduzir restrições dinâmicas de alocação sem violar Risk Confinement,
Controlled Degradation ou Zero Trust.

### Entregas consolidadas

#### Passo 1 — Real Historical Data Adapter
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

#### Passo 1.1 — Backtest Engine Integration
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

### Immediate Priority

Os próximos unlocks do Sprint 7 são:

1. **Benchmark and Factor Inputs**
   - adicionar séries de benchmark e fatores opcionais ao engine
   - proibir qualquer preenchimento com dados futuros
   - formalizar faltas de benchmark como degradação explícita, não como zero
2. **Dynamic Portfolio Constraints**
   - introduzir restrições dinâmicas para concentração, liquidez e regime
   - executar a lógica exclusivamente em tooling determinístico
   - expor resultados por modelos Pydantic imutáveis

### Próximos passos

#### Passo 2 — Benchmark and Factor Inputs
- Adicionar séries de benchmark e fatores opcionais ao engine
- Proibir qualquer preenchimento com dados futuros
- Formalizar faltas de benchmark como degradação explícita, não como zero

#### Passo 3 — Dynamic Portfolio Constraints
- Introduzir restrições dinâmicas para concentração, liquidez e regime
- Executar a lógica exclusivamente em tooling determinístico
- Expor resultados por modelos Pydantic imutáveis

#### Passo 4 — API Boundary Extension
- Avaliar entrega de `/portfolio` apenas quando houver contrato final validado
- Manter o gateway baseado em providers, nunca em SDKs cloud diretos

### Definition of Done — Sprint 7

- ingestão histórica real conectada ao backtester
- engine de backtest consumindo dados fundamentais point-in-time
- benchmark e fatores externos integrados com anti-look-ahead
- restrições dinâmicas formalizadas fora do caminho LLM
- novos contratos tipados documentados e testados
- nenhuma regressão em anti-look-ahead ou Controlled Degradation
