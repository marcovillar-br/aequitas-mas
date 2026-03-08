GEM, act as the Senior Architect and SOTA Engineer of Aequitas-MAS. We are starting a new coding session (Start of Day). 

> Immediate Required Actions:
> 1. **Context Loading:** Perform a full recursive sweep of `.context/current-sprint.md`, `setup.md` (Section 9), and `.context/rules/coding-guidelines.md`.
> 2. **State Validation:** Verify the Definition of Done (DoD) set for today's session.
> 3. **Daily Briefing Generation:** Generate the **SOD Execution Briefing** to be handed over to GCA. 

> The final report output MUST be formatted in formal Brazilian Portuguese (pt-BR) and contain:
> - **Foco do Dia:** A summary of the atomic objectives for today.
> - **Arquivos-Alvo:** Exact list of files in `/src` and `/tests` that will be modified or created.
> - **Dogmas a Aplicar:** Specific architectural rules that GCA must strictly enforce today: 'Zero Numerical Hallucination', 'Dependency Inversion' (no infrastructure SDKs like `boto3` in agents), and 'Controlled Degradation' (Strictly use Pydantic V2 with `Optional[float] = None` to handle missing data. **DO NOT use `Decimal`** as it breaks LangGraph state).
> - **Passo 1 (Atômico):** The exact, single first instruction GCA must execute when the session begins.

**Restrictive Warning:** DO NOT write Python code. Your output is exclusively a directive Markdown briefing for the Developer (GCA).