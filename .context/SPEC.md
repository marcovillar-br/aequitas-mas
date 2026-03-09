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
