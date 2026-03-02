# SPEC: Marks Agent Integration (Risk Auditor Node)

## 1. Objective
Implement the `marks_agent` node in `src/agents/marks.py`. This agent acts as a "Devil's Advocate," auditing the outputs from Graham and Fisher to detect over-optimism and hidden risks.

## 2. Requirements
- **Input:** Receives the full `AgentState`, focusing on `metrics` and `qual_analysis`.
- **Logic:** Must evaluate the convergence between quantitative (Graham) and qualitative (Fisher) data.
- **Output:** Must append a critical summary (The Verdict) to the `audit_log` list.
- **LLM Configuration:** Use `temperature=0.2` to allow for diverse critical thinking and adversarial reasoning.
- **Persona:** Professional skeptic, focused on risk mitigation and "Margin of Safety" preservation.