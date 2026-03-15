# 🗺️ PLAN: Execução de Engenharia — Aequitas-MAS

## Estado Atual Consolidado

O baseline arquitetural vigente do repositório já entrega:

- **Cyclic Graph / Iterative Committee** com a ordem:
  `graham -> fisher -> macro -> marks -> core_consensus -> __end__`
- **AgentState** como estado canônico, imutável e tipado
- **HyDE retrieval flow** com `VectorStorePort -> list[VectorSearchResult]`
- **Otimização determinística** via
  `optimize_portfolio(...) -> Optional[PortfolioOptimizationResult]`
- **Secret management cloud-first** via
  `SecretStorePort` e `EnvSecretAdapter`
- **FastAPI gateway** com DI do grafo compilado e do `BaseCheckpointSaver`
- **Backtesting determinístico** com anti-look-ahead e degradação para `None`

## Sprint 6 — API Gateway & Backtesting
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
5. Backtesting entregue em `src/tools/backtesting/` com:
   - `HistoricalDataLoader`
   - métricas determinísticas
   - `BacktestEngine`

## Sprint 7 — Real Data Ingestion & Dynamic Constraints
**Status:** NEXT

### Objetivo

Substituir a carga sintética/local do backtesting por ingestão histórica real e
introduzir restrições dinâmicas de alocação sem violar Risk Confinement,
Controlled Degradation ou Zero Trust.

### Passos propostos

#### Passo 1 — Real Historical Data Adapter
- Criar adaptador determinístico para ingestão histórica real de preços
- Manter a fronteira de replay baseada em `as_of_date`
- Garantir retorno degradado com `Optional[float] = None` quando séries vierem
  incompletas

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
- restrições dinâmicas formalizadas fora do caminho LLM
- novos contratos tipados documentados e testados
- nenhuma regressão em anti-look-ahead ou Controlled Degradation
