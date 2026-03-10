# Start of Day (SOD) - State Rehydration Protocol

This project utilizes a 4-actor Cognitive Hybridization topology. All AI assistants must understand their role in this pipeline to prevent context degradation and maintain Risk Confinement.

## The Pipeline
1. **The Researcher (NotebookLM):** Ingests SEC/CVM filings and macro news. Generates the fundamental context (e.g., Selic, ERP).
2. **The Scientist (Google AI Studio):** Validates the mathematical and logic routing (LangGraph logic) without writing production code.
3. **The Architect (GEM Web):** Reads `.context/current-sprint.md` and the Researcher's context. Defines the strict architectural plan and outputs directives for the Developer.
4. **The Developer (VS Code + Claude/Copilot):** YOU ARE HERE. You receive the Architect's plan.

## Developer SOD Actions
When starting a new session in the IDE:
1. ALWAYS read `.ai/context.md` first.
2. Acknowledge the Zero Numerical Hallucination dogma (`Optional[float] = None`).
3. Await the human (Tech Lead) to paste the GEM Architect's plan.
4. Execute `/plan` to map the files, then await human approval to `/implement`.
