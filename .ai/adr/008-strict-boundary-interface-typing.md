# ADR 008: Strict Boundary Interface Typing

## Status
Accepted and Implemented (Sprint 6, 2026-03-15).

## Context

Several historical boundaries in the repository used raw dictionaries or
dictionary-like payloads, especially in vector retrieval and deterministic
optimizer handoff. Examples included `list[dict]` and untyped node patch
payloads.

This created architectural risk:

1. Raw payloads bypass validation at the exact point where data contracts should
   be strongest.
2. Silent shape drift becomes easier, especially when LLM-facing and tool-facing
   layers evolve at different speeds.
3. Controlled Degradation is weakened because invalid shapes may propagate
   before the system can collapse cleanly to typed `None`.

These conditions were incompatible with the repository dogmas of strict
Pydantic boundaries, immutable state tensors, and defensive typing.

## Decision

We hardened all critical runtime boundaries with explicit typed contracts.

- `VectorStorePort` now returns `list[VectorSearchResult]`
- retrieval results are represented by immutable Pydantic models
- `optimize_portfolio(...)` returns `Optional[PortfolioOptimizationResult]`
- deterministic optimizer weights are represented through `PortfolioWeight`
- LangGraph node patch outputs were tightened using `TypedDict` where a partial
  state update remains the correct abstraction

The new standard is:
- immutable Pydantic models for external and inter-module boundaries
- `TypedDict` for LangGraph patch payloads when returning a partial state update
- no raw `list[dict]` or generic `dict[str, object]` in critical contracts

## Consequences

**Positive**
- Runtime safety is stronger because shape validation occurs at the boundary.
- IDE support and static comprehension improve significantly.
- Controlled Degradation becomes more reliable when malformed values appear.
- Data-shape hallucinations are reduced because contracts are explicit and
  enforced.

**Negative**
- Refactors touching interfaces now require coordinated updates across tests,
  adapters, and documentation.
- Some helper functions became more explicit and slightly more verbose as they
  transitioned away from generic mappings.

**Follow-up**
- Future boundaries should default to immutable models first and justify any
  looser structure explicitly.
