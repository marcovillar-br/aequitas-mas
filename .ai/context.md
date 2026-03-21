# AEQUITAS-MAS: AI ASSISTANT CONTEXT (SSOT)

> **This file is the agnostic Single Source of Truth for all AI coding assistants**
> (Claude Code, Gemini Code Assist, GitHub Copilot, Cursor, etc.).
> Every assistant MUST read and obey this file before executing any task in this repository.

---

## 1. Project Identity

- **Name:** Aequitas-MAS — Multi-Agent System for Value Investing on B3.
- **Domain:** Quantitative and qualitative financial analysis of Brazilian equities (B3), grounded in the principles of Graham, Fisher, and Howard Marks.
- **Architecture:** Hexagonal (Ports & Adapters) with Domain-Driven Design (DDD), orchestrated via LangGraph stateful DAGs.
- **Runtime:** Python 3.12+, Poetry, Pydantic V2, LangGraph, AWS (multi-cloud agnostic by design).

---

## 2. Mandatory Pre-Task Checklist

Before generating any code, plan, or architectural suggestion, every AI assistant MUST:

1. **Read** `.context/rules/coding-guidelines.md` in full. This document is the authoritative source for stack constraints, naming conventions, typing rules, and testing requirements. It overrides any default assistant behavior.
2. **Confirm** the task scope aligns with the current sprint definition in `.context/current-sprint.md`.
3. **Consult** `.context/agents/skills-index.md` before loading specialized skill context.
4. **Treat** the YAML frontmatter in `.context/skills/*.md` as the canonical metadata source for skill routing, especially `name`, `title`, `description`, `triggers`, `applies_to`, and `priority`.
5. **Verify** the three non-negotiable dogmas described in Section 3 below before writing a single line of code.

---

## 3. Core Dogmas (Non-Negotiable — Risk Confinement)

### 3.1 Zero Numerical Hallucination

> **The LLM is the brain (semantic reasoning). Tools are the muscle (deterministic math).**

Language Models MUST NOT perform financial calculations internally. There are no exceptions.
All quantitative logic — intrinsic value, P/E ratio, margin of safety, DCF, CAGR — MUST be
implemented as pure, strictly-typed Python functions inside `src/tools/`, covered by `pytest`
unit tests. The LLM's sole role is to invoke those tools and synthesize their outputs into
structured, grounded analysis.

### 3.2 Controlled Degradation (`Optional[float] = None`)

All financial fields in `AgentState` and LLM-facing Pydantic schemas MUST be typed as
`Optional[float] = None`. A `None` value is a first-class signal that a data point is
unavailable — it is never an error. This prevents the LLM from substituting a hallucinated
value when real data is absent.

`decimal.Decimal` is **STRICTLY FORBIDDEN** in state schemas. It breaks LangGraph's JSON
serialization and is incompatible with DynamoDB-based checkpointers. Internal tools
(`src/tools/`) MAY use `Decimal` for intermediate precision but MUST cast to `float | None`
before returning values to the Graph State.

### 3.3 Dependency Inversion Principle (DIP)

Cloud SDK imports (`boto3`, `opensearch-py`, etc.) are **STRICTLY FORBIDDEN** inside
`src/agents/` and `src/core/`. All infrastructure interactions are abstracted behind
Ports (`src/core/interfaces/`) and implemented in Adapters (`src/infra/adapters/`).
This keeps the agent reasoning layer cloud-agnostic and independently testable.

---

## 4. Language Protocol

| Context | Language |
|---|---|
| Source code, variables, comments, docstrings, commit messages | **English** |
| All user-facing output, analysis reports, chat responses | **Brazilian Portuguese (pt-BR)** |
| Technical terms within pt-BR text (e.g., *State Machine*, *Embeddings*) | **English** (kept verbatim) |

---

## 5. Key Entry Points

| Concern | Path |
|---|---|
| Full coding rules | `.context/rules/coding-guidelines.md` |
| Agent personas & permissions | `.context/domain/personas.md` |
| Current sprint objectives | `.context/current-sprint.md` |
| Skill routing index | `.context/agents/skills-index.md` |
| LangGraph graph definition | `src/core/graph.py` |
| Shared agent state schema | `src/core/state.py` |
| Vector store port (interface) | `src/core/interfaces/vector_store.py` |
| Infrastructure adapters | `src/infra/adapters/` |
| Deterministic financial tools | `src/tools/` |
