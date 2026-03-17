# ADR 011: Point-in-Time Architecture and Temporal Invariance

## Status
Accepted and Implemented (Sprint 7 Step 1, 2026-03-16).

## Context

Aequitas-MAS is a financial multi-agent system operating across both
quantitative and qualitative evidence flows. This architecture creates a
specific risk: if each path resolves time independently, the system can
silently introduce look-ahead bias.

This risk was no longer theoretical once Sprint 7 connected:

1. deterministic Graham valuation over historical market and fundamental data,
2. real historical ingestion through `B3HistoricalFetcher`,
3. qualitative retrieval through HyDE and `VectorStorePort`,
4. backtesting replay through `HistoricalDataLoader` and `BacktestEngine`.

Without a shared temporal anchor, the system could mix:
- a Graham valuation computed with one effective date,
- a retrieval query resolved against later macro context,
- a replay step executed under a different market snapshot.

That would break temporal honesty, invalidate replay results, and undermine the
project's anti-look-ahead dogma. In a DSS, temporal inconsistency is not a
minor implementation defect; it is a structural integrity failure.

## Decision

The architecture mandates `as_of_date` as the shared temporal anchor across
state, retrieval, valuation, and historical replay.

The following rules are now architectural requirements:

1. **State Anchor**
   - `AgentState` must carry `as_of_date: date` as the canonical point-in-time
     reference for a graph execution.
   - Agents must not synthesize local temporal fallbacks such as `date.today()`
     when `as_of_date` is missing.

2. **Quantitative Synchronization**
   - Graham valuation must consume historical inputs resolved for the active
     `as_of_date`.
   - `HistoricalMarketData` and `HistoricalDataLoader.get_market_data_as_of(...)`
     define the deterministic boundary for point-in-time replay inputs.
   - `B3HistoricalFetcher` must only expose observations valid at or before the
     active `as_of_date`.

3. **Qualitative Synchronization**
   - `VectorStorePort.search_macro_context(...)` must receive `as_of_date`
     explicitly.
   - HyDE retrieval and downstream synthesis must use the same temporal anchor
     as the Graham path and the backtesting path.

4. **Temporal Invariance**
   - For a fixed `ticker`, `thread_id`, and `as_of_date`, the system must
     resolve evidence under the same temporal boundary across all deterministic
     and retrieval-enabled paths.
   - No node may weaken that invariant by consulting evidence that becomes
     visible only after the active `as_of_date`.

## Consequences

**Positive**
- Look-ahead bias is structurally reduced across both quantitative and
  qualitative flows.
- Backtesting and replay results become reproducible because state, retrieval,
  and valuation share the same temporal contract.
- The Graham path and the RAG/HyDE path now operate under one temporal model
  instead of separate implicit clocks.
- Auditing becomes simpler because temporal correctness can be inspected from a
  single explicit state field rather than inferred from node-local behavior.

**Negative**
- Retrieval adapters and historical loaders now require explicit temporal
  metadata propagation, increasing boundary complexity.
- Vector search and historical ingestion adapters may need more restrictive
  filtering logic to preserve temporal validity.
- Missing or invalid temporal context must fail fast or degrade explicitly,
  which can surface stricter runtime behavior than earlier scaffolded flows.
