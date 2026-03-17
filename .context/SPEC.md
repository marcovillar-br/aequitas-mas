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
- `as_of_date: date` é obrigatório como referência temporal point-in-time
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
        as_of_date: date,
        top_k: int = 5,
    ) -> list[VectorSearchResult]: ...
```

#### Regras obrigatórias

1. O retorno do retrieval é sempre uma coleção tipada de `VectorSearchResult`,
   nunca uma coleção crua baseada em mappings.
2. Toda consulta qualitativa deve receber `as_of_date` explicitamente para
   preservar o boundary temporal do grafo.
3. Campos ausentes devem degradar para string vazia ou `0.0` já na fronteira
   do adapter.
4. Falhas de rede ou cluster nunca podem escapar do adapter; o retorno deve ser
   `[]`.
5. `NullVectorStore` permanece a implementação local/offline de degradação.

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
- a rota está ativa e retorna `BacktestResult`
- o handler instancia `B3HistoricalFetcher`, injeta o fetcher em
  `HistoricalDataLoader` e executa `BacktestEngine`
- falhas de validação devem resultar em erro HTTP explícito
- falhas internas devem ser encapsuladas sem fabricar replay sintético

## 5. Backtesting Determinístico

### 5.1 HistoricalDataLoader

`HistoricalDataLoader(start_date, end_date, fetcher=...)` é a fronteira de
acesso a dados históricos point-in-time.

Método obrigatório:

```python
get_market_data_as_of(
    ticker: str,
    current_date: date,
) -> Optional[HistoricalMarketData]
```

#### Regras invioláveis

1. Apenas observações com `observed_at <= current_date` podem ser vistas.
2. Pontos ausentes ou inválidos devem degradar para `None` nos campos do
   `HistoricalMarketData`.
3. Não é permitido forward-fill com dados futuros.
4. Não é permitida interpolação sintética.

### 5.2 Boundary de ingestão

`HistoricalMarketData` é o contrato imutável de mercado/fundamentos e contém:

- `ticker: str`
- `as_of_date: date`
- `price: Optional[float] = None`
- `book_value_per_share: Optional[float] = None`
- `earnings_per_share: Optional[float] = None`
- `selic_rate: Optional[float] = None`

`B3HistoricalFetcher.fetch_as_of(ticker, as_of_date)` é o adapter
determinístico atual para preencher esse boundary.

### 5.3 Engine

`BacktestEngine` executa um loop diário inclusivo entre `start_date` e
`end_date`, sempre consultando o loader com o `as_of_date` da iteração.

Saída:

```python
class BacktestStepLog(BaseModel):
    model_config = ConfigDict(frozen=True)
    as_of_date: date
    observed_price: Optional[float] = None
    vpa: Optional[float] = None
    lpa: Optional[float] = None
    selic_rate: Optional[float] = None
```

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

### 5.4 Controlled Degradation

Se o preço inicial, final ou intermediário estiver ausente:
- métricas derivadas degradam para `None`
- o replay continua quando possível
- os logs precisam registrar a degradação explicitamente

Se fundamentos ou taxa livre de risco estiverem ausentes:
- `vpa`, `lpa` e `selic_rate` permanecem `None`
- o boundary continua válido sem inventar números

## 6. Terminologia Obrigatória

Os documentos operacionais do projeto devem preferir:
- `Cyclic Graph`
- `Iterative Committee`
- `AgentState`

Os documentos não devem reintroduzir vocabulário legado de grafo linear nem
contratos baseados em coleções ou payloads não tipados.

## 7. Próxima Extensão Planejada

Os próximos passos de Sprint 7 focam em:
- benchmarks e fatores externos
- restrições dinâmicas de portfólio
- eventual formalização futura do endpoint `/portfolio`
