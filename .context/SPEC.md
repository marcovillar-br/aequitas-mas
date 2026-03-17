# 📐 SPEC: Especificações de Engenharia — Aequitas-MAS

## 1. Topologia Vigente do Sistema

O Aequitas-MAS opera como **Cyclic Graph** com semântica de
**Iterative Committee**. O roteador central em `src/core/graph.py` controla a
sequência:

`graham -> fisher -> macro -> marks -> core_consensus -> __end__`

### Invariantes

1. O estado compartilhado é sempre `AgentState`.
2. O grafo não usa matemática em prompts.
3. Toda fronteira relevante usa modelos Pydantic v2 imutáveis ou `TypedDict`
   quando o nó retorna patch parcial compatível com LangGraph.
4. `recursion_limit=15` permanece obrigatório como circuit breaker de FinOps.

## 2. Contratos de Tipagem Estrita

### 2.1 AgentState

`src/core/state.py` define o estado canônico do grafo.

Regras:
- `model_config = ConfigDict(frozen=True)`
- métricas financeiras ausentes ou inválidas devem degradar para
  `Optional[float] = None`
- o estado nunca deve transportar `decimal.Decimal`

### 2.2 Contrato Vetorial

`src/core/interfaces/vector_store.py` define:

```python
class VectorSearchResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    document_id: str
    source_url: str
    content: str
    score: float


@runtime_checkable
class VectorStorePort(Protocol):
    def search_macro_context(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[VectorSearchResult]: ...
```

#### Regras obrigatórias

1. O retorno do retrieval é sempre uma coleção tipada de `VectorSearchResult`,
   nunca uma coleção crua baseada em mappings.
2. Campos ausentes devem degradar para string vazia ou `0.0` já na fronteira
   do adapter.
3. Falhas de rede ou cluster nunca podem escapar do adapter; o retorno deve ser
   `[]`.
4. `NullVectorStore` permanece a implementação local/offline de degradação.

### 2.3 Contrato do Otimizador

O tool determinístico de alocação retorna:

```python
def optimize_portfolio(
    tickers: Sequence[str],
    returns: Sequence[Sequence[float]],
    risk_appetite: float,
) -> Optional[PortfolioOptimizationResult]: ...
```

`PortfolioOptimizationResult` é um modelo Pydantic imutável e contém:
- `weights: list[PortfolioWeight]`
- `expected_return: Optional[float] = None`
- `expected_volatility: Optional[float] = None`
- `sharpe_ratio: Optional[float] = None`

#### Regras obrigatórias

1. O tool nunca retorna payload genérico não tipado.
2. Inputs com `NaN`, `Inf`, shape inválido ou covariância singular degradam para
   `None`.
3. Toda matemática permanece em `src/tools/`.

### 2.4 Contrato do Supervisor

`core_consensus_node` retorna um patch tipado para LangGraph:

- `core_analysis`
- `audit_log`
- `messages`
- `executed_nodes`
- `optimization_blocked`

Esse patch usa `TypedDict` para evitar retorno solto e documentar explicitamente
os campos mutáveis do nó.

Mandatory state rule:
- when `optimize_portfolio(...)` degrades to `None`, the patch must explicitly
  set `optimization_blocked=True`

## 3. Secret Management Cloud-First

### 3.1 Port/Adapter

`src/core/interfaces/secret_store.py` define:

```python
@runtime_checkable
class SecretStorePort(Protocol):
    def get_secret(self, key: str) -> Optional[str]: ...
```

`src/infra/adapters/env_secret_adapter.py` implementa `EnvSecretAdapter`.

### 3.2 Regra de Runtime

`src/core/llm.py` resolve `GEMINI_API_KEY` por `SecretStorePort`, nunca por
acoplamento direto da camada de domínio a um provider específico.

### 3.3 Consequência arquitetural

O sistema fica preparado para um futuro `AWSSecretsManagerAdapter` sem exigir
mudança em `src/agents/` ou `src/core/`.

## 4. FastAPI Gateway

### 4.1 Dependências compartilhadas

`src/api/dependencies.py` expõe:
- `get_graph_app()`
- `get_checkpointer()`

Regras:
- o gateway reutiliza o grafo compilado
- o `BaseCheckpointSaver` é resolvido fora das rotas
- `src/api/` não importa SDK cloud diretamente

### 4.2 Endpoint `/analyze`

Contrato:
- body: `AnalyzeRequest`
- dependências: grafo compilado + checkpointer via `Depends`
- `thread_id` determinístico em `RunnableConfig`
- retorno: `AnalyzeResponse`
- internal LangGraph / LLM exceptions must be logged server-side
- client-facing failures must return a stable, sanitized response instead of
  raw exception text

### 4.3 Endpoint `/backtest/run`

Contrato:
- body: `BacktestRequest`
- until real historical ingestion is integrated, the route returns
  `HTTP 501 Not Implemented`
- the route must not execute a degraded replay over empty history and present
  that output as a usable backtest
- falhas de validação devem resultar em erro HTTP explícito
- `BacktestResult` becomes the public response contract only after historical
  ingestion is available at the API boundary

## 5. Backtesting Determinístico

### 5.1 HistoricalDataLoader

`HistoricalDataLoader(start_date, end_date, price_history)` é a fronteira de
acesso a dados históricos.

Método obrigatório:

```python
get_data_as_of(ticker: str, current_date: date) -> Optional[float]
```

#### Regras invioláveis

1. Apenas observações com `observed_at <= current_date` podem ser vistas.
2. Pontos ausentes retornam `None`.
3. Não é permitido forward-fill com dados futuros.
4. Não é permitida interpolação sintética.

### 5.2 Engine

`BacktestEngine` executa um loop diário inclusivo entre `start_date` e
`end_date`, sempre consultando o loader com o `as_of_date` da iteração.

Saída:

```python
class BacktestResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    ticker: str
    start_date: date
    end_date: date
    cumulative_return: Optional[float] = None
    max_drawdown: Optional[float] = None
    logs: list[BacktestStepLog]
```

### 5.3 Controlled Degradation

Se o preço inicial, final ou intermediário estiver ausente:
- métricas derivadas degradam para `None`
- o replay continua quando possível
- os logs precisam registrar a degradação explicitamente

## 6. Terminologia Obrigatória

Os documentos operacionais do projeto devem preferir:
- `Cyclic Graph`
- `Iterative Committee`
- `AgentState`

Os documentos não devem reintroduzir vocabulário legado de grafo linear nem
contratos baseados em coleções ou payloads não tipados.

## 7. Próxima Extensão Planejada

Sprint 7 focará em:
- ingestão histórica real como prerequisite to unlock `/backtest/run`
- benchmarks e fatores externos
- restrições dinâmicas de portfólio
- possível formalização futura do endpoint `/portfolio`
