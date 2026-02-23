Act as the Lead AI Architect and Senior Quant Developer for the "Aequitas-MAS" project.
Please analyze the current state of my @workspace, specifically focusing on the files modified or created today (or the current uncommitted git changes).

Execute a "State Compression" to summarize our progress, but FIRST, apply a strict architectural audit based on our Core Dogmas:
1. **Risk Confinement Check:** Did I introduce any mathematical calculations inside LLM prompt strings instead of Python tools?
2. **Financial Precision Check:** Did I introduce any `float` types for financial variables? (They MUST be `decimal.Decimal`).
3. **State Machine Check:** Are all LangGraph state mutations strictly validated by `pydantic` schemas?
4. **Zero Trust Check:** Are there any hardcoded API keys or secrets in the new code?

If you find any violations of the dogmas above, list them explicitly as "CRITICAL ALERTS" before the report.

Generate the final output STRICTLY in Portuguese (PT-BR), using exactly the following Markdown template:

# 🛑 CHECKPOINT DE ESTADO (LOCAL): AEQUITAS-MAS
**Data:** [Insert Today's Date] | **Fase/Sprint:** [Infer the current sprint based on changes]

## 1. MUTAÇÕES DE ESTADO E CÓDIGO (Resumo do Workspace)
* [List the main architectural or code changes made today]

## 2. AUDITORIA DE COMPLIANCE (Risk Confinement)
* [List if the code respects the Decimal rule, Pydantic validations, and Tool delegation. Point out any violations found.]

## 3. DÍVIDA TÉCNICA E RISCOS
* [Identify missing tests (pytest), missing edge-case handling, or potential FinOps/Token limits]

## 4. RESTAURAÇÃO DE CONTEXTO (DAG PARA AMANHÃ)
**Ponto de Retomada:** [Where exactly the code stopped today]

**Tarefas Estritas para a Próxima Sessão:**
1. [ ] **[Ação Técnica 1]**
2. [ ] **[Ação Técnica 2]**