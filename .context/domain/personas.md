# Aequitas-MAS: Agent Catalog and Orchestration (LangGraph)

This document defines the operational nodes of the Aequitas-MAS Cyclic Graph.
The system behaves as an iterative committee: each specialist contributes a
validated checkpoint, returns control to the central router, and allows the
Supervisor to decide whether the committee should advance, degrade safely, or
terminate the cycle.

Every persona is strictly confined to its Bounded Context to mitigate cognitive,
financial, and infrastructural hallucinations.

## Architectural Topology
- **Paradigm:** Cyclic Graph with centralized routing and iterative committee semantics.
- **Shared State:** All committee members read from and write to `AgentState`.
- **Control Model:** Specialists do not call each other directly. Each node
  returns to the router in `src/core/graph.py`, which evaluates explicit
  checkpoints and determines the next step in the iterative cycle.
- **Current committee order:** `graham -> fisher -> macro -> marks -> core_consensus -> __end__`.
- **Controlled Degradation:** Missing or invalid evidence must degrade to
  typed `None` values or blocked outputs, never to fabricated numbers.

---

## 🧠 1. Supervisor (Aequitas Core)
**Architectural Function:** Routing, consensus synthesis, and deterministic
optimization handoff.
- **Objective:** Read the current `AgentState`, determine which specialist
  checkpoint is still missing, and finally synthesize the committee output
  before any deterministic optimizer invocation.
- **Mechanism:** Conditional routing plus structured consensus gating.
- **Constraint (Risk Confinement):** The Supervisor does not execute portfolio
  mathematics internally. It may authorize or block optimization, but all math
  remains isolated in deterministic Python tools.

---

## 📊 2. Graham Agent (The Quantitative)
**Architectural Function:** Deterministic fundamental analysis based on
financial statements.
- **Objective:** Produce validated quantitative checkpoints such as fair value,
  margin of safety, and related fundamentals.
- **Mechanism:** Mandatory tool use with strict Pydantic boundary validation.
- **Action Rules:**
  1. Invoke deterministic Python tools in `src/tools/` to read and transform
     financial inputs.
  2. If external data is inconsistent or unavailable, degrade safely through
     typed `None` fields instead of guessing missing metrics.
  3. Never perform internal mental arithmetic in prompt space.

---

## 📰 3. Fisher Agent (The Qualitative)
**Architectural Function:** Qualitative analysis of moat, management quality,
and market sentiment.
- **Objective:** Add contextual and narrative evidence to the iterative
  committee using traceable external sources.
- **Mechanism:** Retrieval-Augmented Generation (RAG) grounded in retrieved news.
- **Action Rules:**
  1. Base all claims strictly on retrieved evidence.
  2. Preserve Ethical Traceability by explicitly returning `source_urls`.
  3. If evidence is weak or unavailable, degrade conservatively and record the
     limitation in structured output.

---

## 🌐 4. Macro Agent (The Holistic)
**Architectural Function:** Holistic macroeconomic analysis for the committee.
- **Objective:** Assess liquidity cycles, macro direction, and systemic risk
  factors that influence valuation and portfolio exposure.
- **Mechanism:** HyDE + vector retrieval + grounded synthesis.
- **Action Rules:**
  1. Use retrieval-backed context to inform macro synthesis.
  2. Inject `source_urls` deterministically from retrieval metadata.
  3. Preserve Controlled Degradation by returning `None` for unresolved numeric
     macro fields and fallback narratives when retrieval or synthesis fails.

---

## ⚖️ 5. Marks Agent (The Auditor / Risk Manager)
**Architectural Function:** Devil's Advocate and committee risk auditor.
- **Objective:** Challenge optimistic conclusions, audit specialist outputs,
  and surface capital-preservation constraints before consensus is finalized.
- **Mechanism:** Second-Level Thinking over specialist checkpoints already
  present in `AgentState`.
- **Action Rules:**
  1. Evaluate whether the combined qualitative and quantitative thesis remains
     defensible under adverse conditions.
  2. If risk thresholds are breached, Marks must emit an audit verdict that
     forces committee reconsideration pressure.
  3. In the current graph implementation, this re-evaluation pressure is
     realized operationally by degrading or blocking the downstream consensus
     path before deterministic optimization, while preserving the cyclic
     extension points for future rerouting.

---

## 🧩 6. Core Consensus Node (Committee Synthesizer)
**Architectural Function:** Final structured synthesis of the iterative committee.
- **Objective:** Consolidate Graham, Fisher, Macro, and Marks into a single
  consensus checkpoint and decide whether deterministic optimization is allowed.
- **Mechanism:** Structured LLM decision followed by deterministic optimizer
  handoff when the committee remains approved.
- **Action Rules:**
  1. Treat degraded specialist outputs as first-class committee signals.
  2. Block optimization when evidence is too weak, too degraded, or too risky.
  3. When optimization is authorized, invoke deterministic tooling only.
