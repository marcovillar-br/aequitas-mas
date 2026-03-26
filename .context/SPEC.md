---
id: context-spec
title: "Especificações de Engenharia — Aequitas-MAS"
status: active
last_updated: "2026-03-24"
tags: [context, spec, architecture, contracts, ssot]
---

# 📐 SPEC: Especificações de Engenharia — Aequitas-MAS

Este documento é o **SSOT arquitetural** do projeto. Contratos de runtime,
boundaries, ingestão, apresentação, segurança e backtesting vivem aqui.
`setup.md` permanece operacional; `.context/rules/coding-guidelines.md`
permanece normativo para estilo, tipagem e topologia de execução.

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
- Strict Boundary Mapping: em schemas Pydantic que atuam como boundaries,
  campos podem ser tipados como `Optional[T]`, mas NÃO devem usar
  `default=None`; todas as propriedades devem ser explicitamente mapeadas na
  instanciação, mesmo quando o valor passado for `None`
- o estado nunca deve transportar valores baseados em `Decimal`

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

### 2.5 Contrato de Apresentação (Thesis-CoT Reporting)

Para evitar alucinações visuais ou formatação corrompida, o sistema adota o
padrão **Thesis-CoT** (Chain-of-Thought) inspirado no framework FinRobot,
preservando rastreabilidade, separação de responsabilidades e profissionalismo
na entrega final do PA.

Contrato documental de apresentação:

```python
class ThesisReportPayload(BaseModel):
    model_config = ConfigDict(frozen=True)
    thesis: str
    evidence: list[str]
    quantitative_data: dict[str, object]


@runtime_checkable
class PresentationAdapter(Protocol):
    def render_pdf(self, payload: ThesisReportPayload) -> bytes: ...
```

Regras obrigatórias:
1. O output final do Multi-Agent System é um JSON estritamente estruturado e
   validado via Pydantic, contendo tese, evidências e dados quantitativos já
   resolvidos pelas fronteiras determinísticas.
2. A renderização visual pertence exclusivamente a um **Presentation Adapter**
   desacoplado em Python, capaz de consumir esse JSON para gerar gráficos e
   relatórios PDF por ferramentas determinísticas como Matplotlib e WeasyPrint.
3. O LLM é terminantemente proibido de gerar gráficos ASCII, markdown tables
   com finalidade visual, layout de relatório ou formatação direta de PDF.
4. A camada de apresentação é downstream do estado estruturado; ela não altera
   os dados, não recalcula métricas e não move lógica de domínio para prompts.

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

O sistema fica preparado para futuros adapters, como
`AWSSecretsManagerAdapter`, sem exigir mudança em `src/agents/` ou
`src/core/`.

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

Reference: `[.ai/adr/011-point-in-time-architecture-and-temporal-invariance.md]`
governs temporal synchronization between the Graham path, historical data
loaders, and RAG/HyDE retrieval so that quantitative and qualitative flows
share the same `as_of_date` boundary.

### 5.1 HistoricalDataLoader

`HistoricalDataLoader(start_date, end_date, fetcher=...)` é a fronteira de
acesso a dados históricos point-in-time.

Protocolo obrigatório:

```python
@runtime_checkable
class HistoricalDataLoaderPort(Protocol):
    def get_market_data_as_of(
        self,
        ticker: str,
        current_date: date,
    ) -> Optional[HistoricalMarketData]: ...

    def get_benchmark_data_as_of(
        self,
        benchmark: BenchmarkType,
        current_date: date,
    ) -> Optional[HistoricalBenchmarkData]: ...
```

#### Regras invioláveis

1. Apenas observações com `observed_at <= current_date` podem ser vistas.
2. Pontos ausentes ou inválidos devem degradar para `None` nos campos do
   `HistoricalMarketData`.
3. Não é permitido forward-fill com dados futuros.
4. Não é permitida interpolação sintética.
5. Benchmark and factor series must never be shifted beyond `current_date`.
6. If benchmark data is unavailable for a specific date, the boundary must
   degrade to `None` and trigger an audit log entry.

### 5.2 Boundary de ingestão

`HistoricalMarketData` é o contrato imutável de mercado/fundamentos e contém:

- `ticker: str`
- `as_of_date: date`
- `price: Optional[float] = None`
- `book_value_per_share: Optional[float] = None`
- `earnings_per_share: Optional[float] = None`
- `selic_rate: Optional[float] = None`
- `piotroski_f_score: Optional[int] = None`
- `altman_z_score: Optional[float] = None`

`B3HistoricalFetcher.fetch_as_of(ticker, as_of_date)` é o adapter
determinístico atual para preencher esse boundary.

Regras invioláveis da boundary:

1. `piotroski_f_score` atua como filtro de qualidade/value trap e
   `altman_z_score` atua como sinal determinístico de risco de insolvência.
2. Ambos os indicadores devem ser calculados exclusivamente por ferramentas em
   Python puro sob `src/tools/`.
3. As assinaturas documentais mínimas para esses cálculos são:

```python
def calculate_piotroski_f_score(...) -> Optional[int]: ...
def calculate_altman_z_score(...) -> Optional[float]: ...
```

4. É proibido ao LLM estimar, inferir probabilisticamente ou recomputar esses
   indicadores em prompt space.
5. Quando as evidências de entrada forem ausentes, inválidas ou temporalmente
   incompatíveis com `as_of_date`, os campos devem degradar para `None`.

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

Se os insumos necessários para `piotroski_f_score` ou `altman_z_score`
estiverem ausentes ou inválidos:
- `piotroski_f_score` e `altman_z_score` devem degradar para `None`
- nenhum fallback probabilístico pode ser produzido pelo LLM
- o cálculo deve permanecer restrito a tooling determinístico em `src/tools/`

Se benchmark ou fator estiver indisponível para uma data específica:
- `HistoricalBenchmarkData.value` deve degradar para `None`
- o replay não pode usar forward-fill nem deslocamento temporal para compensar
- a ausência deve gerar um audit log entry explícito

### 5.5 Benchmark and Factor Contracts

Benchmarks e séries de fatores devem usar uma fronteira tipada e imutável para
permitir cálculo futuro de alpha, benchmark-relative performance e opportunity
cost sem violar a invariância temporal do replay.

```python
class BenchmarkType(str, Enum):
    CDI = "CDI"
    IBOV = "IBOV"
    SELIC = "SELIC"
    IPCA = "IPCA"


class HistoricalBenchmarkData(BaseModel):
    model_config = ConfigDict(frozen=True)

    benchmark: BenchmarkType
    as_of_date: date
    value: Optional[float] = None
    description: str
```

Regras obrigatórias:

1. `CDI`, `IBOV`, `SELIC` e `IPCA` são tratados como séries point-in-time,
   nunca como constantes globais atemporais.
2. O loader deve resolver benchmarks somente para datas válidas em
   `<= current_date`.
3. Não é permitido forward-fill ou qualquer deslocamento de benchmark para além
   de `current_date`.
4. Se uma série estiver indisponível em uma data específica, `value` deve
   degradar para `None`.
5. A indisponibilidade de benchmark ou fator deve ser registrada em audit log
   para preservar observabilidade do replay.

## 6. Terminologia Obrigatória

Os documentos operacionais do projeto devem preferir:
- `Cyclic Graph`
- `Iterative Committee`
- `AgentState`

Os documentos não devem reintroduzir vocabulário legado de grafo linear nem
contratos baseados em coleções ou payloads não tipados.

## 7. Próxima Extensão Planejada

O baseline consolidado (Sprint 11) entrega CI/CD shift-left com dogma
enforcement automatizado e cobertura DAIA estatística.

Os próximos passos (Sprint 12: Abr/26 — Framework & API) focam em:
- Elevação do Graham agent para `with_structured_output` (`GrahamInterpretation`),
  eliminando a última assimetria de tipagem no comitê.
- Exposição de streaming SSE via `/analyze/stream` para observação em tempo
  real da deliberação do comitê iterativo.
- Preparação da superfície de API para o XAI Dashboard opcional.

## 8. SDLC & Git Flow

Regras obrigatórias:

1. Cada novo sprint exige uma nova working branch. Antes de iniciar o próximo
   sprint, a branch do sprint anterior deve estar finalizada e com push
   realizado para o repositório remoto.
2. Ao final de todo sprint, e antes de qualquer remote push ser autorizado, o
   agente Code Reviewer ("The Shield") deve inspecionar o diff da working
   branch contra sua BASE BRANCH, isto é, a branch exata a partir da qual ela
   foi criada, como a branch do sprint anterior ou `main`, dependendo da
   origem. Toda correção resultante da revisão deve ser commitada na própria
   working branch antes da autorização de push.
3. O prefixo `fix/` é reservado estritamente para hotfixes de produção.
   Correções de bugs identificadas durante o sprint ativo devem ser entregues
   como commits normais na working branch corrente, sem criação de branch
   `fix/`.
