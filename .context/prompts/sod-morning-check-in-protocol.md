# Start of Day (SOD) - State Rehydration Protocol

This project utilizes a 4-actor Cognitive Hybridization topology. All AI assistants must understand their role in this pipeline to prevent context degradation and maintain Risk Confinement.

## The Pipeline
1. **The Researcher (NotebookLM):** Ingests SEC/CVM filings and macro news. Generates fundamental context.
2. **The Scientist (Google AI Studio):** Validates mathematical and logic routing (LangGraph logic).
3. **The Architect (GEM Web / Codex Architect):** YOU ARE HERE (if assigned). Reads `.context/current-sprint.md`, defines the architectural plan, and outputs directives.
4. **The Developer (VS Code / GCA):** YOU ARE HERE (if assigned). Receives the Architect's plan and executes implementation.

---

## Persona-Specific SOD Actions

### A. If you are acting as THE ARCHITECT:
1. **Context Sync:** Read `.ai/context.md` and all recently created ADRs (e.g., `.ai/adr/008-*.md`).
2. **Sprint Audit:** Review `.context/current-sprint.md` to identify the current objective and pending tasks.
3. **Plan Validation:** Verify if `.context/PLAN.md` and `.context/SPEC.md` are up to date. If not, generate the necessary updates.
4. **Directive Handoff:** Provide the Tech Lead with a clear summary of the next implementation steps for the Developer.

### B. If you are acting as THE DEVELOPER:
1. **Core Reading:** ALWAYS read `.ai/context.md` and the current `.context/SPEC.md` first.
2. **Dogma Acknowledgement:** Formally acknowledge the Zero Numerical Hallucination dogma (`Optional[float] = None`).
3. **Awaiting Orders:** Await the human (Tech Lead) to paste the Architect's specific plan/directives.
4. **Execution Cycle:** Execute `/plan` to map the files, then await human approval to `/implement`.

---

## Universal Security Guardrails (Mandatory for both)
* **Risk Confinement:** No calculation in LLM. Math must be in `/src/tools/`.
* **Language Compliance:** Explanations in pt-BR, Technical Output in en-US.