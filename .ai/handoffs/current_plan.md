# 🗺️ PLAN: Graph Integration of Dynamic Constraints - Sprint 7 Step 4

## 1. Overview
This document outlines the technical blueprint for integrating the `BenchmarkFetcher` and `DynamicConstraints` deterministic tools directly into the LangGraph execution flow. The core consensus node will act as the orchestration layer to route these deterministic inputs into the portfolio optimizer.

## 2. Target Components
- **Target File:** `src/agents/core.py` (specifically `core_consensus_node`)
- **Test File:** `tests/test_core_consensus_node.py`

## 3. Execution Flow & Integration
1. **Data Extraction:** The `core_consensus_node` must extract `as_of_date` and `risk_appetite` from the `AgentState`.
2. **Fetch Benchmarks:** 
   - Instantiate `BenchmarkFetcher` and call `fetch_as_of(BenchmarkType.CDI, state.as_of_date)`.
   - Construct the `BenchmarkMetrics` object mapping the fetched CDI value.
3. **Calculate Constraints:** 
   - Call `calculate_dynamic_constraints(state.risk_appetite, benchmarks)`.
4. **Portfolio Optimization Handoff:**
   - Pass the resulting `max_ticker_weight` and `min_cash_position` from the `DynamicConstraints` object into the `optimize_portfolio` tool/function alongside the existing tickers, returns, and risk appetite.

## 4. Error Handling & Controlled Degradation
- **No Crashes:** The LangGraph node must NOT crash if the fetcher degrades.
- Rely entirely on the graceful degradation already built into `HistoricalBenchmarkData` and `calculate_dynamic_constraints` (which safely handles `None` values).

## 5. Dogmas & Guardrails
- **No LLM Mental Math:** The supervisor node just routes the deterministic outputs. The LLM must NOT be exposed to or reason about the mathematical values of these constraints.
- **Immutability:** Preserve `frozen=True` boundaries for all intermediate data structures.

## 6. Testing Requirements (TDD)
- **SOTA Unit Tests:** Update `tests/test_core_consensus_node.py`.
- Mock `BenchmarkFetcher.fetch_as_of` and `calculate_dynamic_constraints` (or just rely on the pure function if feasible).
- Assert that `optimize_portfolio` is called with the correct constraint arguments (`max_ticker_weight`, `min_cash_position`).
- Ensure the state updates correctly under both optimal and degraded network conditions.

## 7. Definition of Done
- [ ] `src/agents/core.py` updated to orchestrate fetcher and constraints.
- [ ] `optimize_portfolio` signature correctly accepts and utilizes the new dynamic boundaries.
- [ ] LLM isolation maintained (no math in prompts).
- [ ] All tests pass with proper patching.