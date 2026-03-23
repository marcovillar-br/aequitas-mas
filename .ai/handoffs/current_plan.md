# 🗺️ Current Plan: Sprint 8 - Step 3 (Graph Integration)

## 1. Objective
Finalize and harden the resilient integration of the deterministic optimizer within `core_consensus_node` (`src/agents/core.py`). The node must safely handle all failure modes (e.g., singular covariance matrices, missing inputs) by explicitly setting `optimization_blocked=True` and injecting a qualitative rationale into the graph state and audit log.

## 2. Scope & Constraints
- **Target:** `core_consensus_node` logic.
- **Resilient Integration:** Ensure all branches where the optimizer is skipped, fails, or degrades to `None` are caught.
- **State Immutability:** The returned patch (`CoreConsensusNodeResult`) must always include an initialized `CoreAnalysis` object, even when weights are empty.
- **Auditability:** Every degradation path must append a clear string to `audit_log` and `messages` explaining why optimization was blocked.
- **Risk Confinement:** The LLM determines the qualitative consensus; the tool strictly performs math. If the tool fails, the LLM is NOT invoked to hallucinate an alternative.

## 3. Implementation Steps (For SDD Implementer)

### Step 1: Logic Verification & Hardening
- [x] Review `core_consensus_node` in `src/agents/core.py` to confirm that `optimize_portfolio(...)` degradation strictly returns `optimization_blocked=True`.
- [x] Ensure that missing inputs (`portfolio_returns`, `risk_appetite`) also safely bypass the optimizer and log the rationale without raising unhandled exceptions.

### Step 2: State Patch & Audit Log Alignment
- [x] Confirm that `_build_blocked_core_analysis` sets `recommended_weights=[]` and preserves `source_urls` for traceability.
- [x] Verify that the `audit_log` correctly receives the degradation justification string.

### Step 3: Unit Testing (RED-GREEN-REFACTOR)
- [x] Write/update unit tests to explicitly mock an `Exception` inside `optimize_portfolio` to test the failure boundary.
- [x] Write/update unit tests mocking `optimize_portfolio` returning `None` to test the controlled degradation path.
- [x] Validate the correct shape of `CoreConsensusNodeResult` in all fallback scenarios.

## 4. Definition of Done
- `core_consensus_node` correctly and safely degrades upon any optimizer failure or input absence.
- The graph state reliably reflects `optimization_blocked=True` and logs an explanatory rationale.
- 100% unit test coverage for the new degradation branches in `src/agents/core.py`.
