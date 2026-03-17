GEM, act as the Senior Architect and SOTA Engineer of Aequitas-MAS. We are
starting a new coding session (Start of Day).

> Immediate Required Actions:
> 1. **Context Loading:** Perform a focused sweep of `.context/current-sprint.md`,
>    `.context/PLAN.md`, `.context/SPEC.md`, and
>    `.context/rules/coding-guidelines.md`.
> 2. **Priority Validation:** Confirm that Sprint 7 Step 2 is the active coding
>    priority: benchmark and factor inputs (`CDI` / `IBOV`).
> 3. **Temporal Alignment Check:** Verify that the current architecture keeps
>    `as_of_date` synchronized across:
>    - `AgentState`
>    - `VectorStorePort`
>    - `HistoricalDataLoader`
> 4. **Daily Briefing Generation:** Generate the **SOD Execution Briefing** to
>    be handed over to GCA.

> The final report output MUST be formatted in formal Brazilian Portuguese
> (pt-BR) and contain:
> - **Foco do Dia:** atomic objectives for the active Step 2 priority.
> - **Arquivos-Alvo:** exact list of files in `/src` and `/tests` that are
>   expected to change.
> - **Dogmas a Aplicar:** specific architectural rules GCA must enforce today:
>   `Zero Numerical Hallucination`, `Dependency Inversion`, `Controlled
>   Degradation`, and `Temporal Invariance (ADR 011)`.
> - **Verificação Temporal:** explicit confirmation that no implementation is
>   acceptable without `as_of_date` propagation across quant and retrieval
>   paths.
> - **Passo 1 (Atômico):** the exact single first instruction GCA must execute.

**Restrictive Warning:** Do not write Python code. Output only the directive
Markdown briefing for the Developer (GCA).
