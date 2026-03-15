# 📐 SPEC: Especificações de Engenharia — Aequitas-MAS

---

## ✅ Especificação 3.1: Adaptador Hexagonal DynamoDB (GitHub Copilot SDD)
**Sprint:** 3.1 | **Status:** CONCLUÍDA (PR #22, commit `76acc5f`)
**Objetivo:** Implementar persistência Serverless (AWS DynamoDB) via Inversão de Dependência e garantir blindagem arquitetural contra o viés da IA.

### 1. Contratos de Interface (DIP)
* **Arquivo-Alvo:** `src/infra/adapters/dynamo_saver.py`
* **Herança Obrigatória:** `langgraph.checkpoint.base.BaseCheckpointSaver`
* **Isolamento de Nuvem:** A biblioteca `boto3` DEVE estar confinada a este ficheiro e a testes isolados. É expressamente proibido importar `boto3` em `/src/agents/` ou `/src/core/`.

### 2. Injeção de Dependência e Segurança (Zero Trust)
* **Construtor Testável:** A classe `DynamoDBSaver` DEVE suportar Injeção de Dependência no construtor. O recurso AWS (`boto3.resource('dynamodb')`) só deve ser invocado em *runtime* se o parâmetro `table` injetado for nulo. Isso permite que os testes utilizem `pytest-mock` sem estourar *timeouts* de rede.
* **Credenciais:** É proibida a manipulação e leitura de arquivos `.env` diretamente no código do adaptador.

### 3. Diretrizes de Tipagem e Anti-Viés
* **Bloqueio de Decimal:** Fica expressamente proibido o uso, importação ou conversão para `decimal.Decimal` em qualquer camada de persistência. A arquitetura exige que métricas continuem fluindo estritamente como `float` ou `None`.
* **Degradação Controlada:** Todos os estados baseados no `src/core/state.py` que possuam `Optional[float] = None` devem ter sua ausência mapeada (*null values*) tratada adequadamente durante a transação com o DynamoDB.

---

## ✅ Especificação 3.2: RAG HyDE & Vetorização Macro (Claude Code)
**Sprint:** 3.2 | **Status:** CONCLUÍDA (branch `feat/macro-hyde-opensearch-integration`, commits `1e27dea`–`01195e7`)
**Objetivo:** Substituir o fluxo puramente generativo do Agente Macro por um pipeline RAG (Retrieval-Augmented Generation) baseado em Hypothetical Document Embeddings (HyDE), conectado ao AWS OpenSearch Serverless, garantindo rastreabilidade ética de fontes e confinamento total de SDKs de infraestrutura.

---

### 1. Contrato do Adaptador de Busca Vetorial (Port/Adapter DIP)

A camada de agentes (`/src/agents/`) é vedada a qualquer importação de SDK de nuvem. O acesso ao OpenSearch é mediado exclusivamente por um **contrato de interface** definido em `src/core/interfaces/vector_store.py`.

#### 1.1 VectorStorePort — Interface Pública

```python
# src/core/interfaces/vector_store.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class VectorStorePort(Protocol):
    def search_macro_context(self, query: str, top_k: int = 5) -> list[dict]: ...
```

**Contrato do retorno** — cada `dict` da lista DEVE conter:

| Campo | Tipo | Descrição |
|---|---|---|
| `document_id` | `str` | Identificador único do chunk indexado |
| `source_url` | `str` | URL rastreável da fonte (BCB, FED, etc.) |
| `content` | `str` | Texto bruto do chunk recuperado |
| `score` | `float` | Score de similaridade de cosseno `[0.0, 1.0]` |

**Regras invioláveis do protocolo:**
1. O método NUNCA deve propagar exceções para fora — falhas de rede devem retornar `[]` (Controlled Degradation).
2. Campos ausentes no hit do OpenSearch devem degradar para string vazia `""` ou `0.0` — nunca `KeyError`.
3. O adaptador concreto (`OpenSearchAdapter`) satisfaz `VectorStorePort` por **subtipagem estrutural** (`typing.Protocol`) — herança explícita não é necessária nem desejada.

#### 1.2 NullVectorStore — Implementação de Degradação

```python
class NullVectorStore:
    def search_macro_context(self, query: str, top_k: int = 5) -> list[dict]:
        return []
```

Implementa o **Null Object Pattern**: garante que o Agente Macro execute em modo offline (local/CI) sem qualquer dependência de AWS, retornando lista vazia e ativando o fluxo de Controlled Degradation.

#### 1.3 OpenSearchAdapter — Adaptador de Infraestrutura

**Arquivo:** `src/infra/adapters/opensearch_client.py`
**Confinamento:** `import boto3` e `from opensearchpy import ...` SOMENTE neste arquivo.

| Variável de Ambiente | Obrigatória | Padrão |
|---|---|---|
| `OPENSEARCH_ENDPOINT` | **Sim** — `ValueError` se ausente | — |
| `OPENSEARCH_INDEX` | Não | `aequitas-macro-docs` |
| `OPENSEARCH_REGION` | Não | `us-east-1` |
| `OPENSEARCH_SERVICE` | Não | `aoss` (Serverless) |

**Autenticação:** cadeia padrão AWS via `boto3.Session().get_credentials()` — IAM Role → env vars → `~/.aws/credentials`. **Zero credenciais hardcoded.**

**Factory de produção:**
```python
adapter = OpenSearchAdapter.from_env()   # produção
adapter = OpenSearchAdapter(client=mock) # testes (DI por construtor)
```

**Diagrama de dependências (DIP enforced):**
```
Macro Agent  ──depends on──►  VectorStorePort  (src/core/interfaces/)
                                      ▲
                               implementado por
                                      │
                             OpenSearchAdapter  (src/infra/adapters/)
                                      │
                              boto3 + opensearch-py  (confinados)
```

---

### 2. Pipeline HyDE (Hypothetical Document Embeddings)

O pipeline HyDE resolve o problema de *vocabulary mismatch* entre a query do usuário e os documentos indexados, substituindo a query por um documento hipotético sintetizado pelo LLM.

#### Sequência obrigatória de execução

```
[AgentState.target_ticker]
        │
        ▼
Stage 1 — HyDE Generation
  Prompt: _HYDE_PROMPT (texto puro, sem structured_output)
  Input:  ticker
  Output: hyde_text (str) — documento hipotético COPOM/FED
        │
        ▼
Stage 2 — Vector Retrieval
  Input:  hyde_text (usado como query semântica)
  Call:   vector_store.search_macro_context(hyde_text, top_k=5)
  Output: retrieved_docs [{ document_id, source_url, content, score }]
        │
        ├──► _format_retrieved_context(docs) → context_block (injetado no prompt)
        ├──► _extract_source_urls(docs)       → dynamic_urls  (injetado no MacroAnalysis)
        └──► _build_audit_trace(ticker, hyde_text, docs) → audit_entry
        │
        ▼
Stage 3 — Grounded Synthesis
  Prompt: _SYNTHESIS_PROMPT com {ticker} e {context}
  LLM:    llm.with_structured_output(MacroAnalysis)
  Output: raw_result (MacroAnalysis com source_urls=[])
        │
        ▼
Injeção Determinística de source_urls
  raw_result.model_copy(update={"source_urls": dynamic_urls})
        │
        ▼
Return: { "macro_analysis": result, "audit_log": [audit_entry] }
```

**Restrição crítica do Stage 1:** O prompt HyDE NÃO deve usar `with_structured_output`. A saída deve ser texto puro de máxima densidade semântica para maximizar a qualidade do embedding de consulta.

**Restrição crítica do Stage 3:** O prompt de síntese DEVE instruir explicitamente o LLM a retornar `source_urls: []`. O preenchimento real é feito deterministicamente pelo código — nunca pelo LLM.

---

### 3. Dogma de Tipagem: Optional[float] = None (Zero Numerical Hallucination)

Este dogma é **inviolável** em toda a Sprint 3.2 e nas sprints seguintes.

#### 3.1 Regra Fundamental

> **LLMs não calculam e não estimam métricas numéricas.** Se um valor quantitativo não estiver **explicitamente presente** no contexto recuperado do OpenSearch, o campo correspondente no schema Pydantic DEVE ser `None`.

#### 3.2 Aplicação no Schema `MacroAnalysis`

```python
class MacroAnalysis(BaseModel):
    model_config = ConfigDict(frozen=True)

    trend_summary: str                    # único campo obrigatório — narrativa qualitativa
    interest_rate_impact: Optional[float] = None   # ← NUNCA estimado pelo LLM
    inflation_outlook: Optional[str]      = None   # ← ausente se não recuperado
    source_urls: list[str]                          # ← injetado do retrieval, nunca do LLM
```

**Por que `Optional[float]` e não `Decimal`?**
`Decimal` quebra a serialização do estado LangGraph (não é JSON-serializável por padrão). O schema Pydantic usa `float` com validação `math.isfinite()` para rejeitar `NaN`/`Inf`. Internamente, ferramentas em `/src/tools/` podem usar `Decimal` para precisão, mas DEVEM fazer cast para `float | None` antes de retornar ao estado do grafo.

#### 3.3 Comportamento por Cenário

| Cenário | `interest_rate_impact` | `source_urls` | `audit_log` |
|---|---|---|---|
| Retrieval bem-sucedido + dado explícito no contexto | `float` (extraído) | URLs reais do BCB/FED | Score de cosseno por documento |
| Retrieval bem-sucedido + dado ausente no contexto | `None` | URLs reais do BCB/FED | Score de cosseno por documento |
| Retrieval vazio (`NullVectorStore` / índice vazio) | `None` | `[]` | "nenhum documento recuperado" |
| Falha de conexão OpenSearch (`ConnectionError`) | `None` | `[]` | `"ALERTA: ..."` |
| Falha de LLM (`ResourceExhausted`) | `None` | `[]` | `"ALERTA: ..."` |

**Invariante absoluto:** em nenhum cenário o Agente Macro propaga uma exceção para o LangGraph. O nó SEMPRE retorna um `dict` com `macro_analysis` presente — garantia anti-Death Loop.

---

### 4. Rastreabilidade Ética (audit_log)

O campo `audit_log` do `AgentState` (tipo `Annotated[List[str], operator.add]`) é o veículo de rastreabilidade do sistema. O Agente Macro DEVE sempre adicionar exatamente **uma entrada** ao `audit_log` por execução, independentemente do resultado.

**Formato obrigatório — execução com retrieval:**
```
[Macro/HyDE] Recuperação vetorial concluída para '{ticker}': N documento(s) selecionado(s)
por similaridade de cosseno.
Critério de seleção: distância vetorial entre o documento hipotético (HyDE) e os chunks
indexados do BCB/FED.
Documentos selecionados:
  [1] score=0.XXXX | fonte=https://...
  [2] score=0.XXXX | fonte=https://...
Consulta HyDE (prévia): "..."
```

**Formato obrigatório — execução sem retrieval (degradação):**
```
[Macro/HyDE] Análise sem RAG para '{ticker}': nenhum documento recuperado do índice
vetorial. O agente utilizou conhecimento interno do LLM com Controlled Degradation
aplicada a todos os campos numéricos.
Consulta HyDE (prévia): "..."
```

**Formato obrigatório — falha crítica:**
```
ALERTA: Agente Macro degradou para fallback em '{ticker}'. Pipeline HyDE+RAG não
concluído. Análise macroeconômica indisponível.
```

---

### 5. Wiring de Injeção de Dependência no Grafo

```python
# src/core/graph.py

def _resolve_vector_store() -> VectorStorePort:
    try:
        return OpenSearchAdapter.from_env()      # produção (OPENSEARCH_ENDPOINT obrigatório)
    except (ValueError, RuntimeError):
        return NullVectorStore()                 # fallback local/offline

macro_agent = create_macro_agent(_resolve_vector_store())  # nome preservado para patch() em testes
workflow.add_node("macro", macro_agent)
```

O nome `macro_agent` DEVE ser preservado como atributo de módulo em `graph.py` para que `patch("src.core.graph.macro_agent")` continue funcional nos testes de integração existentes.

---

### 6. Especificação 3.2 — Recuperação Vetorial HyDE: Contrato de Dados e Tipagem Defensiva

Esta seção consolida, em formato de contrato formal, o fluxo de dados do pipeline HyDE+RAG
e reafirma a aplicação do dogma `Optional[float] = None` em **cada elo** da cadeia de
recuperação macroeconômica — desde a geração do documento hipotético até a persistência
no `AgentState`.

#### 6.1 Contrato de Dados: Três Fases Obrigatórias

O Agente Macro DEVE executar as três fases abaixo na ordem exata. Nenhuma fase pode ser
omitida, reordenada ou substituída por inferência direta do LLM.

---

**Fase A — Geração do Documento Hipotético (HyDE Generation)**

| Item | Especificação |
|---|---|
| **Responsável** | LLM (`gemini-2.5-flash`, `temperature=0.0`) |
| **Entrada** | `AgentState.target_ticker` (ex: `"PETR4"`) |
| **Saída** | `hyde_text: str` — texto puro, denso, sem estrutura JSON |
| **Formato** | Simulação de trecho de ata COPOM/FED em pt-BR |
| **Restrição** | `with_structured_output` PROIBIDO — preserva máxima densidade semântica |
| **Tipo retornado** | `str` (extraído de `AIMessage.content`) |

O documento hipotético NÃO é armazenado no `AgentState`. É utilizado exclusivamente como
vetor de consulta para a Fase B.

---

**Fase B — Recuperação Vetorial (Vector Retrieval)**

| Item | Especificação |
|---|---|
| **Responsável** | `VectorStorePort` (injetado via DI) |
| **Entrada** | `hyde_text: str` (saída da Fase A) |
| **Chamada** | `vector_store.search_macro_context(hyde_text, top_k=5)` |
| **Saída** | `retrieved_docs: list[dict]` |
| **Campos obrigatórios por doc** | `document_id: str`, `source_url: str`, `content: str`, `score: float` |
| **Comportamento em falha** | Retorna `[]` — NUNCA propaga exceção |
| **Metadados para rastreabilidade** | `source_url` e `score` extraídos de cada hit do OpenSearch |

O critério de seleção dos documentos é **exclusivamente** a distância vetorial (similaridade
de cosseno) entre o embedding do `hyde_text` e os embeddings dos chunks indexados.
Nenhum filtro heurístico ou regra de negócio adicional é aplicado nesta fase.

---

**Fase C — Síntese Grounded (Grounded Synthesis)**

| Item | Especificação |
|---|---|
| **Responsável** | LLM com `with_structured_output(MacroAnalysis)` |
| **Entradas** | `ticker: str` + `context_block: str` (chunks formatados da Fase B) |
| **Saída (LLM)** | `MacroAnalysis` com `source_urls=[]` (instrução explícita no prompt) |
| **Saída (pós-injeção)** | `MacroAnalysis` com `source_urls=dynamic_urls` (do retrieval) |
| **Mecanismo de injeção** | `raw_result.model_copy(update={"source_urls": dynamic_urls})` |
| **Garantia** | `source_urls` NUNCA alucinados pelo LLM — sempre extraídos da Fase B |

---

#### 6.2 Tipagem Defensiva `Optional[float] = None` — Reafirmação por Elo da Cadeia

O dogma `Optional[float] = None` é aplicado em **quatro pontos distintos** da cadeia de
recuperação macroeconômica. A falha em qualquer ponto NÃO deve produzir valores numéricos
estimados — deve produzir `None`.

```
Cadeia de Recuperação                   Ponto de aplicação de Optional[float] = None
─────────────────────────────────────   ──────────────────────────────────────────────────────────
[1] Fase B — retrieval retorna []       → context_block = fallback text sem dados numéricos
                                          LLM não encontra valores → interest_rate_impact = None ✓

[2] Fase C — LLM não encontra valor     → Prompt instrui: "se ausente, retorne null"
    numérico explícito no contexto        interest_rate_impact = None ✓

[3] Fase C — LLM retorna valor inválido → Pydantic field_validator: math.isfinite() rejeita
    (NaN, Inf, não-numérico)               → ValidationError → Controlled Degradation = None ✓

[4] Fallback crítico (exceção LLM/rede) → MacroAnalysis instanciado diretamente com
                                           interest_rate_impact=None, inflation_outlook=None ✓
```

**Regra de ouro:** Se houver qualquer dúvida sobre a proveniência de um valor numérico,
o campo DEVE ser `None`. A narrativa qualitativa (`trend_summary`) é o único canal
permitido para informação macroeconômica quando dados quantitativos não estão disponíveis.

#### 6.3 Invariantes do Schema `MacroAnalysis` ao Longo da Cadeia

| Campo | Fase A | Fase B | Fase C (LLM) | Fase C (pós-injeção) | Fallback |
|---|---|---|---|---|---|
| `trend_summary` | — | — | **obrigatório** (str) | inalterado | texto fixo de fallback |
| `interest_rate_impact` | — | — | `float \| None` (se explícito) | inalterado | `None` |
| `inflation_outlook` | — | — | `str \| None` (se presente) | inalterado | `None` |
| `source_urls` | — | `dynamic_urls` extraídas | `[]` (instrução) | **`dynamic_urls`** | `[]` |

A coluna "Fase C (pós-injeção)" representa o estado final que entra no `AgentState`.
É o único estado autorizado a ser gravado no grafo LangGraph.

---

## ✅ Specification 3.3: OpenSearch Infrastructure Hardening (Delivered)
**Sprint:** 3.3 | **Status:** DELIVERED
**Objective:** Stabilize real HyDE retrieval on OpenSearch Serverless with explicit vector mapping and deterministic indexing/retrieval behavior.

### 1. Mandatory OpenSearch Mapping Contract

The target index (e.g., `macro-index`) MUST define the following vector field:

```json
{
  "content_embedding": {
    "type": "knn_vector",
    "dimension": 3072,
    "method": {
      "name": "hnsw",
      "engine": "nmslib",
      "space_type": "cosinesimil"
    }
  }
}
```

Required companion fields:
- `content: text`
- `source_url: keyword`
- `document_id: keyword`
- `published_at: date`

### 2. Retrieval Contract Update

`OpenSearchAdapter.search_macro_context(...)` MUST use explicit `knn` queries with local query vectorization:

```json
{
  "size": 5,
  "query": {
    "knn": {
      "content_embedding": {
        "vector": [ ... ],
        "k": 5
      }
    }
  }
}
```

`neural` query mode is NOT the default runtime path for this architecture.

### 3. Index Creation and Validation Guardrails

Before indexing, adapter logic MUST:
1. Check whether the target index exists.
2. Create it with the exact `knn_vector` mapping if absent.
3. Fail fast if `content_embedding` exists with an incompatible type (e.g., `float`).

This requirement eliminates the previous OpenSearch `500` retrieval failure caused by invalid vector field mapping.

---

## 📌 Specification 4.0: Aequitas Core (Supervisor) + Portfolio Optimization
**Sprint:** 4 | **Status:** CONCLUÍDA
**Objective:** Implement the Core Supervisor agent and deterministic portfolio optimization workflow.

### Delivered Scope
1. Explicit execution ledger delivered in `src/core/state.py` via `executed_nodes`,
   plus dedicated supervisor checkpoints such as `marks_verdict`, `portfolio_tickers`,
   `portfolio_returns`, and `risk_appetite`.
2. `core_consensus` node delivered in `src/agents/core.py` and integrated into
   `src/core/graph.py` for structured synthesis of specialist outputs before the final
   optimization handoff.
3. Deterministic portfolio weighting delivered through `src/tools/portfolio_optimizer.py`
   using `scipy.optimize.minimize(method="SLSQP")`, preserving full math isolation from
   the LLM path.

### 1. Agent Topology: Core Supervisor

The **Aequitas Core** node is the orchestration authority in LangGraph and MUST:
1. Route execution across specialist agents (Graham, Fisher, Macro, Marks).
2. Gather consensus-ready outputs from all sub-agents.
3. Invoke deterministic optimization via `src/tools/portfolio_optimizer.py`.
4. Return structured output through strict Pydantic V2 schemas.

### 2. Output Schema Requirement (Pydantic V2)

Aequitas Core output MUST include an optimized portfolio allocation array, for example:

```python
class OptimizedWeight(BaseModel):
    model_config = ConfigDict(frozen=True)
    ticker: str
    weight: float

class PortfolioOptimizationResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    weights: list[OptimizedWeight]
    expected_return: Optional[float] = None
    expected_volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
```

If optimization inputs are incomplete, quantitative fields MUST degrade to `None` under Defensive Typing rules.

### 3. Risk Confinement Requirement

Portfolio mathematics (covariance matrix, efficient frontier optimization, constraints) MUST be executed exclusively by deterministic Python tooling in `src/tools/portfolio_optimizer.py`.

The LLM MUST NOT:
- compute allocations,
- derive optimized weights,
- perform probabilistic numeric estimation.

The LLM may only orchestrate tool calls and summarize deterministic outputs.

### 4. Delivered Implementation Notes

The implemented supervisor flow is:

```
graham -> fisher -> macro -> marks -> core_consensus -> __end__
```

Routing is controlled by explicit state checkpoints rather than implicit `audit_log`
side effects. Controlled degradation remains valid at every step: a specialist may fail
gracefully, record execution in the ledger, and still allow the Core Supervisor to reach
structured consensus without inventing numeric values.
