# Aequitas-MAS: Agent Catalog and Orchestration (LangGraph)

This document defines the operational nodes of the Aequitas-MAS Directed Acyclic Graph (DAG). Each agent is strictly confined to its Bounded Context to mitigate cognitive and financial hallucinations.

## 🧠 1. Supervisor (Aequitas Core)
**Architectural Function:** Routing and Orchestration (State Machine).
- **Objective:** Analyze the current state (`AequitasState`) and decide which specialist to trigger next, or if the cycle should be terminated due to lack of data (controlled degradation).
- **Mechanism:** Uses *Conditional Edges* in LangGraph.
- **Constraint (Risk Confinement):** The Supervisor does not analyze the asset. It only delegates tasks and verifies if Pydantic validated the data correctly.

---

## 📊 2. Graham Agent (The Quantitative)
**Architectural Function:** Rigorous fundamental analysis based on financial statements.
- **Objective:** Calculate the *Fair Price* and *Margin of Safety* of the asset.
- **Mechanism:** *Tool-Use Obligatory*. The agent is prohibited from performing mental arithmetic.
- **Action Rules:**
  1. Invariably trigger deterministic Python tools (`src/tools/`) to read data from official sources (e.g., yfinance via `get_graham_data`).
  2. If tools return an error (e.g., non-existent asset or insufficient data), the agent must fail fast and return the error to the Supervisor.
  3. Do not consider, under any circumstances, intangible future growth projections.

---

## 📰 3. Fisher Agent (The Qualitative)
**Architectural Function:** Analysis of "Economic Moat", management quality, and corporate market sentiment.
- **Objective:** Understand the context beyond the numbers (IR Reports, material facts, governance).
- **Mechanism:** *Retrieval-Augmented Generation (RAG)*.
- **Action Rules:**
  1. Base all statements strictly on documents injected into the context.
  2. Comply with Ethical Traceability: Mandatorily return an array with URLs/Sources (`source_urls`) for every generated analysis.
  3. If information is not in the retrieved context, explicitly declare: "Insufficient qualitative data".

---

## ⚖️ 4. Marks Agent (The Auditor / Risk Manager)
**Architectural Function:** Act as *Devil's Advocate* and mitigate survivorship bias/excessive optimism.
- **Objective:** Audit the combined *outputs* of Graham and Fisher.
- **Mechanism:** *Second-Level Thinking*.
- **Action Rules:**
  1. Evaluate the current phase of the Market Pendulum (Market Cycle).
  2. Challenge Graham's thesis: "Does the margin of safety compensate for the governance risk pointed out by Fisher?".
  3. Generate the final audit log that approves or vetoes the recommendation, adding restrictions focused on capital protection (Drawdown).