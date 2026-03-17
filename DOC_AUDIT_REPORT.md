# DOC_AUDIT_REPORT

## Escopo auditado
Arquivos revisados conforme a solicitação:

- `README.md`
- `setup.md`
- `.context/PLAN.md`
- `.context/SPEC.md`
- `.context/current-sprint.md`
- `.context/domain/personas.md`
- `.context/agents/skills-index.md`
- todos os arquivos em `.context/skills/`
- todos os ADRs em `.ai/adr/`

## Baseline de código usado para validação
O relatório foi cruzado com o estado atual do código, que hoje já contém:

- `AgentState.as_of_date` como boundary temporal explícita
- `VectorStorePort.search_macro_context(..., as_of_date=...)`
- `VectorSearchResult` e `PortfolioOptimizationResult` como contratos tipados imutáveis
- `SecretStorePort` + `EnvSecretAdapter` como boundary de secrets
- FastAPI com DI do grafo compilado e de `BaseCheckpointSaver`
- `B3HistoricalFetcher`, `HistoricalMarketData`, `HistoricalDataLoader.get_market_data_as_of(...)`
- `/backtest/run` habilitado, sem `HTTP 501`
- `BacktestEngine` registrando `vpa`, `lpa` e `selic_rate`

## Resumo executivo
Após a remediação recente em `.context/PLAN.md` e `.context/SPEC.md`, o drift
documental remanescente está concentrado em:

1. `README.md`
2. `setup.md`
3. `.context/current-sprint.md`
4. `.ai/adr/002-hyde-rag-pipeline.md`
5. `.ai/adr/009-fastapi-gateway-and-deterministic-backtesting.md`
6. `.ai/adr/010-api-boundary-hardening-and-honest-scaffolding.md`

`PLAN.md` e `SPEC.md` estão agora materialmente alinhados com o estado real do
Sprint 7 Step 1 e não entram mais como violação principal.

## Arquivos com informação desatualizada ou violação da diretiva de relevância

### `README.md`
**Problema**
- Ainda afirma que `POST /backtest/run` está em `HTTP 501 Not Implemented`.
- Continua descrevendo Sprint 6 como se o backtest ainda estivesse sob Honest
  Scaffolding.

**Divergência com o código**
- O endpoint já está ativo e encadeia `B3HistoricalFetcher ->
  HistoricalDataLoader -> BacktestEngine`.

**Ação recomendada**
- Atualizar a seção “Delivered Through Sprint 6”.
- Reescrever o roadmap para mostrar que a ativação real do backtest já ocorreu
  no Sprint 7.

### `setup.md`
**Problema**
- Ainda documenta `HistoricalDataLoader.get_data_as_of(...)` como contrato do
  replay.

**Divergência com o código**
- O loader atual expõe `get_market_data_as_of(...)` e opera sobre
  `HistoricalMarketData`.

**Ação recomendada**
- Atualizar a seção “Backtesting Contract” para:
  - `HistoricalDataLoader.get_market_data_as_of(...)`
  - `HistoricalMarketData`
  - replay point-in-time com boundary enriquecida

### `.context/current-sprint.md`
**Problema**
- Ainda mantém no Sprint 6 o item histórico `HTTP 501` como se fosse parte
  relevante do snapshot atual.
- A seção de riscos residuais ainda afirma que faltam ADRs dedicados para
  secret-store e strict-boundary hardening.

**Divergência com o código e com a documentação**
- O risco de indisponibilidade do backtest já foi mitigado e superado.
- Os temas de secret management e strict typing já estão formalizados pelos
  ADRs 007 e 008.

**Violação da diretiva de relevância**
- Para um arquivo de sprint corrente, manter comportamento transitório já
  revogado reduz o valor operacional do documento.

**Ação recomendada**
- Remover ou condensar o registro de Honest Scaffolding do Sprint 6.
- Atualizar os riscos residuais para refletir apenas gaps ainda abertos:
  - fonte point-in-time para fundamentos
  - benchmark/factors
  - dynamic constraints

## ADRs com drift parcial

### `.ai/adr/002-hyde-rag-pipeline.md`
**Problema**
- Ainda documenta `VectorStorePort.search_macro_context(hyde_text, top_k=5)`
  sem `as_of_date`.

**Divergência com o código**
- O retrieval atual é time-aware e exige `as_of_date` no contrato.

**Ação recomendada**
- Atualizar o ADR para registrar explicitamente retrieval point-in-time.

### `.ai/adr/009-fastapi-gateway-and-deterministic-backtesting.md`
**Problema**
- Ainda descreve `HistoricalDataLoader.get_data_as_of(...)` como enforcement
  principal de anti-look-ahead.
- Ainda trata ingestão histórica real como follow-up.

**Divergência com o código**
- O replay já usa `B3HistoricalFetcher` e `get_market_data_as_of(...)`.
- A ingestão histórica real já foi integrada.

**Ação recomendada**
- Atualizar o ADR para refletir a arquitetura pós-Sprint 7 Step 1.

### `.ai/adr/010-api-boundary-hardening-and-honest-scaffolding.md`
**Problema**
- Ainda congela como decisão ativa que `/backtest/run` deve retornar
  `HTTP 501 Not Implemented`.

**Divergência com o código**
- A condição arquitetural desse ADR já foi satisfeita e o endpoint foi
  desbloqueado.

**Ação recomendada**
- Marcar a decisão como parcialmente superseded ou amendá-la.
- Manter como vigentes apenas os pontos ainda válidos:
  - sanitização de erros
  - patch explícito de estado

## Arquivos auditados sem drift material relevante

### Alinhados
- `.context/PLAN.md`
- `.context/SPEC.md`
- `.context/domain/personas.md`
- `.context/agents/skills-index.md`
- `.context/skills/aws-advisor.md`
- `.context/skills/context-manager.md`
- `.context/skills/domain-analysis.md`
- `.context/skills/github-manager.md`
- `.context/skills/playwright.md`
- `.context/skills/security.md`
- `.context/skills/subagent-creator.md`
- `.context/skills/tech-design-doc.md`
- `.ai/adr/001-ssot-and-lazy-persistence-loading.md`
- `.ai/adr/003-opensearch-shared-collection.md`
- `.ai/adr/004-dogma-audit-grep-strategy.md`
- `.ai/adr/005-portfolio-optimization-tool.md`
- `.ai/adr/006-agnostic-operational-flow.md`
- `.ai/adr/007-cloud-first-secret-management.md`
- `.ai/adr/008-strict-boundary-interface-typing.md`

## Avaliação específica dos upgrades do Sprint 6

### Strict Interface Typing
**Status documental**
- Coberto por `.context/SPEC.md` e `.ai/adr/008-strict-boundary-interface-typing.md`.

**Gap remanescente**
- Não há gap crítico no núcleo documental auditado.

### Zero Trust Security
**Status documental**
- Coberto por `README.md`, `setup.md`, skills de segurança e
  `.ai/adr/007-cloud-first-secret-management.md`.

**Gap remanescente**
- Não há necessidade de novo ADR para secret management.

### Backtesting Engine Paradigm
**Status documental**
- Parcialmente coberto.

**Gap remanescente**
- `README.md`, `setup.md`, `.context/current-sprint.md`, `ADR 009` e `ADR 010`
  ainda não consolidaram totalmente:
  - `B3HistoricalFetcher`
  - `HistoricalMarketData`
  - endpoint de backtest ativo
  - `BacktestStepLog` com fundamentos

### FastAPI Gateway
**Status documental**
- Majoritariamente alinhado.

**Gap remanescente**
- O README ainda mantém o endpoint de backtest como indisponível.

### Graph Paradigm
**Status documental**
- Alinhado no escopo auditado.

**Observação**
- Não encontrei resíduos materiais de vocabulário legado no conjunto principal
  auditado; a nomenclatura dominante já é `Cyclic Graph` / `Iterative Committee`.

## Diretiva de pruning para `current-sprint.md`, `PLAN.md` e `SPEC.md`

### Situação atual
- `.context/PLAN.md`: alinhado e enxuto o suficiente para o estado atual.
- `.context/SPEC.md`: alinhado e atualizado para o contrato pós-ingestão real.
- `.context/current-sprint.md`: ainda merece pruning adicional por manter
  conteúdo histórico do `HTTP 501` e risco de ADR já resolvido.

### O que deve ser removido ou comprimido em `current-sprint.md`
- referência ao `HTTP 501` como marco ainda relevante do snapshot corrente
- risco residual sobre ausência de ADR para secret-store e strict typing

## ADRs: criar novos ou apenas atualizar?

### Não é necessário criar ADR novo para:
- Cloud-First Secret Management
- Strict Boundary Interface Typing

**Justificativa**
- Esses temas já estão formalizados por:
  - `.ai/adr/007-cloud-first-secret-management.md`
  - `.ai/adr/008-strict-boundary-interface-typing.md`

### Novo ADR: opcional, não obrigatório
**Tema sugerido**
- `Point-in-Time Retrieval and Historical Ingestion Boundaries`

**Motivação**
- As mudanças de Sprint 7 já são amplas o suficiente para um registro
  consolidado:
  - `AgentState.as_of_date`
  - retrieval time-aware
  - `B3HistoricalFetcher`
  - `HistoricalMarketData`
  - desbloqueio do `/backtest/run`

**Alternativa mínima**
- Atualizar os ADRs 002, 009 e 010 sem criar novo ADR.

## Ordem recomendada de remediação
1. `README.md`
2. `setup.md`
3. `.context/current-sprint.md`
4. `.ai/adr/009-fastapi-gateway-and-deterministic-backtesting.md`
5. `.ai/adr/010-api-boundary-hardening-and-honest-scaffolding.md`
6. `.ai/adr/002-hyde-rag-pipeline.md`
