---
id: adr-001
title: "Multi-AI SSOT and Lazy Loading for Graph Persistence"
status: accepted
sprint: "Sprint 3.1"
date: "2026-03-10"
tags: [adr, ssot, ci, lazy-loading, persistence]
---

> **⚠ SUPERSEDED REFERENCE:** This ADR was written when `.ai/context.md`
> served as the SSOT for all architectural dogmas. That file has since been
> archived to `.ai/archive/context.md`. The current canonical SSOT is
> `.ai/aidd-001-unified-system-prompt.md`. The lazy-loading decision
> documented in Section 2.2 remains valid and is unaffected by this change.

# ADR 001: Multi-AI SSOT & Lazy Loading for Graph Persistence

## 1. Context
The project relies on multiple AI assistants (Claude, Copilot, Gemini) and a CI/CD pipeline running in ephemeral environments. We faced two critical issues:
1. **Dogma Fragmentation:** Risk Confinement rules were scattered across multiple assistant-specific prompt files, leading to inconsistent code generation.
2. **CI/CD Flakiness:** The `src/core/graph.py` routing logic imported `boto3` (via `DynamoDBSaver`) at the module level. This caused `ModuleNotFoundError` during pytest collection in CI environments where AWS dependencies are intentionally omitted for security and speed.

## 2. Decision
1. **Multi-AI Agnostic SSOT:** We established `.ai/context.md` as the absolute Single Source of Truth for all architectural dogmas. Entrypoints like `CLAUDE.md` and `.github/copilot-instructions.md` now simply delegate to this file.
2. **Lazy Loading & Soft Environments:** We refactored `src/core/graph.py` to lazy import `DynamoDBSaver` strictly within the `create_graph()` function. We introduced the `_SOFT_ENVS = {"local", "ci"}` structural flag, forcing the application to use LangGraph's in-memory `MemorySaver` in these environments.
3. **Fail-Fast Cloud Validation:** In `dev`, `hom`, and `prod`, if the module fails to load, the system triggers an immediate and actionable `RuntimeError`.

## 3. Consequences
* **Positive:** Complete elimination of AWS credential/dependency issues during unit test collection. CI pipeline is now strictly gated by Ruff and native Dogma Audits (regex). AI assistants operate under unified constraints, drastically reducing code hallucinations.
* **Negative:** Slightly increased complexity in `graph.py` due to dynamic imports and environment parsing.
