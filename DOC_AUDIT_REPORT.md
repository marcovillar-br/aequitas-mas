# DOC_AUDIT_REPORT

## Escopo auditado
Foram auditados os artefatos solicitados:
- `README.md`
- `setup.md`
- `.context/PLAN.md`
- `.context/SPEC.md`
- `.context/current-sprint.md`
- `.context/domain/personas.md`
- `.context/agents/skills-index.md`
- todos os arquivos em `.context/skills/`
- todos os ADRs em `.ai/adr/`

Também foi feita uma varredura complementar de drift terminológico em outros `.md` do repositório para verificar resíduos de `DAG`, `Pipeline`, `AequitasState` e contratos antigos.

## Resumo executivo
- A documentação do Sprint 6 está parcialmente refletida.
- Os maiores pontos de drift estão em:
  - contratos antigos com `list[dict]` e `dict[str, object]`
  - secret management ainda descrito como `.env`/`os.getenv` em vez de `SecretStorePort`
  - roadmap e status ainda tratando API/Backtesting como futuro, quando já foram entregues
  - excesso de histórico em `PLAN.md`, `SPEC.md` e `current-sprint.md`
  - resíduos terminológicos de `DAG`/`Pipeline` em documentos que orientam implementação

## Validação de topologia
- `.context/prompts/sod-context-enforcement.md` referencia corretamente `.context/agents/skills-index.md`.
- `.context/current-sprint.md` já referencia o Skill Registry e está topologicamente alinhado com `.context/agents/skills-index.md`.
- `.context/agents/skills-index.md` está exaustivo para os arquivos atuais em `.context/skills/`.
- `.context/domain/personas.md` está substancialmente alinhado ao `Cyclic Graph` atual e não foi identificado como fonte principal de drift.

## Arquivos com drift ou violação da diretiva de relevância

### Alta prioridade

#### `README.md`
- **Divergência:** ainda descreve a arquitetura como `Directed Acyclic Graph (DAG)`.
- **Divergência:** a seção de variáveis de ambiente trata `.env` como caminho obrigatório para `GEMINI_API_KEY`, sem mencionar `SecretStorePort` + `EnvSecretAdapter`.
- **Divergência:** o roadmap ainda coloca `FastAPI` e API externa como entrega futura (`Q1/2027`), mas `src/api/` e `POST /backtest/run` já existem.
- **Divergência:** o documento não reflete Sprint 6, `BacktestEngine`, `BaseCheckpointSaver` via DI, `VectorSearchResult` nem `PortfolioOptimizationResult`.
- **Bloat:** o caso PETR4 com números datados tende a envelhecer mal e não representa contrato arquitetural.
- **Reescrita recomendada:** converter o README em visão atual do sistema:
  - `Cyclic Graph / Iterative Committee`
  - FastAPI gateway já entregue
  - backtesting determinístico já entregue
  - typing hardening com `VectorSearchResult` e `PortfolioOptimizationResult`
  - secret management por porta/adaptador
  - mover o caso PETR4 para um exemplo versionado ou remover

#### `setup.md`
- **Divergência:** afirma que `dev.nix` é a fonte definitiva do ambiente, mas o arquivo não existe no repositório.
- **Divergência:** reforça `.env` como mecanismo obrigatório de secrets, sem refletir `SecretStorePort` e `EnvSecretAdapter`.
- **Divergência:** a seção de segurança ainda descreve `.env` como regra operacional principal, quando a arquitetura atual já abstrai a origem do secret.
- **Bloat:** o documento mistura filosofia, bootstrap, Terraform SSO e operação local em um único artefato.
- **Reescrita recomendada:** separar em setup operacional enxuto:
  - dependências reais do repositório
  - fluxo local via Poetry
  - secrets locais via environment variables consumidas por `EnvSecretAdapter`
  - nota explícita de evolução para `AWSSecretsManagerAdapter`
  - remover ou tornar opcional qualquer referência a `dev.nix`

#### `.context/PLAN.md`
- **Violação de relevância:** contém grande volume de histórico de Sprints antigas, checkpoints de preparação e logs de execução que não são mais plano acionável.
- **Divergência:** Sprint 6 ainda aparece como `PLANNED`, apesar de estar entregue.
- **Divergência:** ainda documenta `VectorStorePort.search_macro_context(...) -> list[dict]`.
- **Divergência:** ainda descreve `POST /portfolio`, que não foi entregue no gateway atual.
- **Divergência terminológica:** usa `Pipeline RAG` e outros termos de fluxo sequencial que conflitam com a diretriz lexical atual.
- **Reescrita recomendada:** reduzir o arquivo para:
  - estado atual consolidado da arquitetura
  - próximos passos reais
  - backlog curto e acionável
  - mover o histórico detalhado para `docs/archive/` ou ADRs

#### `.context/SPEC.md`
- **Violação de relevância:** acumulou especificações históricas extensas de múltiplas Sprints; hoje mistura contrato vigente com arquivo de memória institucional.
- **Divergência:** ainda define `VectorStorePort` com retorno `list[dict]`.
- **Divergência:** ainda exemplifica `NullVectorStore` retornando `list[dict]`.
- **Divergência:** a especificação do retrieval continua baseada em `dict`, não em `VectorSearchResult`.
- **Divergência:** não documenta a remediação de `SecretStorePort` + `EnvSecretAdapter`.
- **Divergência:** não consolida o hardening recente de `PortfolioOptimizationResult` como retorno explícito do otimizador.
- **Divergência:** Sprint 6 está descrita como planejada, embora já implementada.
- **Divergência:** menciona `/portfolio` como endpoint mínimo, o que não corresponde ao gateway atualmente entregue.
- **Reescrita recomendada:** quebrar o arquivo em duas camadas:
  - `SPEC-current.md` com somente contratos vigentes
  - arquivo histórico/arquivo morto para sprints antigas
  - atualizar imediatamente os contratos de interface, secrets e API/backtesting

#### `.context/current-sprint.md`
- **Violação de relevância:** ainda carrega blocos completos de Sprints 3.3, 3.4 e 4; isso é histórico, não estado corrente.
- **Divergência:** apesar de marcar Sprint 6 como `DONE`, não registra as remediações finais de estabilidade:
  - `VectorSearchResult`
  - `PortfolioOptimizationResult` como boundary explícita
  - `SecretStorePort`
  - `EnvSecretAdapter`
- **Divergência:** não registra o hardening de tipagem do `core_consensus_node`.
- **Reescrita recomendada:** manter apenas:
  - Sprint atual/última concluída
  - arquitetura vigente
  - próximos passos
  - riscos abertos

#### `.context/skills/context-manager.md`
- **Divergência crítica:** o auditor de compliance manda verificar `Decimal for financial logic`, quando a dogmática atual proíbe `Decimal` nos modelos de estado e no caminho LLM-facing.
- **Divergência terminológica:** ainda usa `DAG/Tasks for Tomorrow`.
- **Reescrita recomendada:** atualizar a skill para:
  - reforçar banimento de `Decimal` em `src/core/` e `src/agents/`
  - usar `AgentState`
  - substituir `DAG` por `Cyclic Graph` ou `Iterative Committee`

#### `.context/skills/domain-analysis.md`
- **Divergência:** ainda usa `AequitasState` em vez de `AgentState`.
- **Divergência:** não reflete a camada supervisor/consensus atual nem os contratos tipados de fronteira já endurecidos.
- **Reescrita recomendada:** atualizar nomenclatura e incluir:
  - `AgentState`
  - `CoreAnalysis`
  - fronteiras tipadas com modelos Pydantic imutáveis

#### `.context/skills/subagent-creator.md`
- **Divergência:** ainda exige `AequitasState` como argumento do agente.
- **Divergência:** fixa modelos Gemini antigos (`gemini-flash-latest`, `gemini-1.5-pro`) e não acompanha o uso atual.
- **Divergência:** generaliza `with_structured_output` como regra total, sem observar exceções arquiteturais como HyDE Stage 1.
- **Reescrita recomendada:** atualizar a skill para:
  - `AgentState`
  - modelos Gemini vigentes no repositório
  - regra: structured output por padrão, exceto quando a especificação exigir texto puro

#### `.context/skills/tech-design-doc.md`
- **Divergência terminológica:** ainda orienta diagramas de `DAG workflows`.
- **Divergência:** não menciona boundary typing duro, `SecretStorePort`, FastAPI DI nem o backtesting determinístico do Sprint 6.
- **Reescrita recomendada:** trocar a linguagem para `Cyclic Graph`/`Iterative Committee` e atualizar o checklist mínimo de TDD para incluir:
  - ports/adapters
  - secret store abstraction
  - interface models imutáveis
  - anti-look-ahead contracts

#### `.ai/adr/005-hyde-rag-pipeline.md`
- **Divergência:** o ADR ainda descreve o retorno do `VectorStorePort` como lista de documentos genéricos, sem formalizar `VectorSearchResult`.
- **Divergência lexical:** o termo `Pipeline` permanece no título e em várias seções.
- **Reescrita recomendada:** atualizar o ADR para:
  - explicitar `VectorSearchResult`
  - alinhar o vocabulário a `retrieval flow` ou `retrieval stages`
  - registrar que o contrato de interface foi endurecido após Sprint 6

#### `.ai/adr/008-portfolio-optimization-tool.md`
- **Divergência crítica:** ainda documenta `optimize_portfolio(...) -> dict[str, object]`.
- **Divergência:** os outputs listados não refletem a boundary atual `PortfolioOptimizationResult`.
- **Divergência:** não registra Controlled Degradation para `None` em entradas inválidas/singulares.
- **Reescrita recomendada:** atualizar o ADR para:
  - `Optional[PortfolioOptimizationResult]`
  - `PortfolioWeight` como unidade de alocação
  - degradação determinística para `None`

### Média prioridade

#### `.context/skills/aws-advisor.md`
- **Divergência:** ainda usa `GOOGLE_API_KEY`; o nome padronizado no repositório é `GEMINI_API_KEY`.
- **Divergência:** a skill não faz ponte com a abstração atual `SecretStorePort`.
- **Reescrita recomendada:** padronizar para `GEMINI_API_KEY` e mencionar que produção deve ser modelada via adapter futuro compatível com `SecretStorePort`.

#### `.context/skills/security.md`
- **Divergência:** a seção de secret management ainda privilegia `IDE-native Secret Managers` no local e não descreve a abstração atual `EnvSecretAdapter`.
- **Reescrita recomendada:** alinhar a skill ao contrato vigente:
  - local/CI: `EnvSecretAdapter`
  - produção: adapter dedicado como `AWSSecretsManagerAdapter`
  - código de domínio sempre dependente de `SecretStorePort`

#### `.context/skills/github-manager.md`
- **Divergência:** a nota de secret management ainda remete a `Google IDX Secret Manager or local environment variables`, sem refletir o boundary `SecretStorePort`.
- **Reescrita recomendada:** atualizar a orientação de revisão pré-commit para procurar violações do contract de secrets, não apenas `.env`.

### Baixa prioridade

#### `.context/skills/aws-advisor.md`, `.context/skills/security.md`, `.context/skills/github-manager.md`
- **Observação consolidada:** as três skills já apontam para Zero Trust, mas ainda falam em secrets de forma operacional demais e pouco arquitetural.
- **Ação mínima:** harmonizar o vocabulário com o modelo port/adapter recém-entregue.

## Arquivos auditados sem drift material relevante
- `.context/domain/personas.md`
- `.context/agents/skills-index.md`
- `.context/skills/playwright.md`
- `.ai/adr/004-ssot-and-lazy-persistence-loading.md`
- `.ai/adr/006-opensearch-shared-collection.md`
- `.ai/adr/007-dogma-audit-grep-strategy.md`
- `.ai/adr/009-agnostic-operational-flow.md`

## Observações adicionais fora do escopo principal, mas relevantes
Esses arquivos não estavam no núcleo obrigatório da solicitação, mas apareceram como fontes reais de drift em uma varredura repo-wide:

#### `.context/prompts/for-new-ai-coding-assistant.md`
- ainda usa `Directed Acyclic Graph (DAG)`

#### `.context/prompts/sod-morning-check-in-protocol.md`
- ainda usa `The Pipeline`

#### `.context/rules/coding-guidelines.md`
- ainda usa `LangGraph (Stateful DAGs)`
- ainda cita `AequitasState` no exemplo de naming

**Recomendação:** corrigir esses três arquivos junto com a poda documental principal, porque eles influenciam diretamente futuros assistentes e podem reintroduzir drift no código.

## Poda recomendada para os arquivos de planejamento

### `.context/current-sprint.md`
- remover seções detalhadas de Sprints 3.3, 3.4 e 4
- manter apenas arquitetura vigente, Sprint 6 entregue e próximos passos

### `.context/PLAN.md`
- remover histórico operacional extenso já resolvido
- manter backlog acionável e decisões ainda abertas

### `.context/SPEC.md`
- remover metadados históricos de PR/commit por Sprint
- mover especificações antigas para ADRs ou apêndice arquivado
- manter apenas contratos ativos do sistema

## ADRs novos recomendados

### ADR 010 — Cloud-First Secret Management via Port/Adapter
**Motivação:** a arquitetura já mudou materialmente e isso ainda não foi formalizado em ADR.

**Escopo sugerido:**
- `SecretStorePort`
- `EnvSecretAdapter`
- future-proofing para `AWSSecretsManagerAdapter`
- remoção de acoplamento direto de `os.getenv` da camada de domínio

### ADR 011 — Strict Boundary Interface Typing
**Motivação:** a migração de `dict` cru para modelos imutáveis (`VectorSearchResult`, `PortfolioOptimizationResult`) altera contratos centrais do sistema.

**Escopo sugerido:**
- typed ports em `src/core/interfaces/`
- eliminação de `list[dict]` e `dict[str, object]`
- `TypedDict` para patches de nó no LangGraph quando apropriado

### ADR 012 — FastAPI Gateway and Deterministic Backtesting Boundary
**Motivação:** Sprint 6 já entregou um boundary novo importante e ainda não existe ADR específico consolidando essa decisão.

**Escopo sugerido:**
- DI de `BaseCheckpointSaver`
- boundary HTTP via FastAPI
- `BacktestEngine` com anti-look-ahead
- política de Controlled Degradation para replay histórico

## Ordem sugerida de remediação documental
1. `README.md`
2. `setup.md`
3. `.context/SPEC.md`
4. `.context/PLAN.md`
5. `.context/current-sprint.md`
6. skills com drift (`context-manager`, `domain-analysis`, `subagent-creator`, `tech-design-doc`, `aws-advisor`, `security`, `github-manager`)
7. ADR 005 e ADR 008
8. prompts/guidelines auxiliares fora do escopo principal
