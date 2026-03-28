---
plan_id: plan-sprint16-sota-factors-consolidated
target_files:
  - "src/tools/fundamental_metrics.py"
  - "tests/tools/test_fundamental_metrics.py"
  - "src/core/state.py"
  - "src/core/interfaces/presentation.py"
  - "src/tools/backtesting/historical_ingestion.py"
  - "src/agents/graham.py"
  - "src/agents/core.py"
  - "src/agents/fisher.py"
  - "src/agents/macro.py"
  - "src/agents/marks.py"
  - "src/core/graph.py"
  - "src/infra/adapters/pdf_presentation_adapter.py"
  - "tests/test_graham_agent.py"
  - "tests/test_core_consensus_node.py"
  - "tests/infra/test_pdf_presentation_adapter.py"
  - ".ai/prompts/graham_agent_v2.md"
  - "main.py"
  - "scripts/setup_env.sh"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, pydantic-v2-frozen]
validation_scale: "FACTS (Mean: 5.0)"
---

## Sprint 16 — Consolidated Plan (3 Phases)

### Phase 1: ROIC + DY Tools & Schema (plan-001)
- `calculate_roic` and `calculate_dividend_yield` in `fundamental_metrics.py`.
- `GrahamMetrics` + `HistoricalMarketData` schema expansion (v3.0).
- Consensus auto-enrichment via `model_dump()`.

### Phase 2: Graham Wiring & CoT (plan-002)
- `_build_metrics_from_historical_data` maps roic/DY.
- `_build_interpreter_prompt` enriched with ROIC and DY.
- `GrahamInterpretation` expanded: `roic_assessment` + `dividend_yield_assessment`.
- `graham_agent_v2.md` CoT prompt updated.

### Phase 3: Tearsheet & Throttling (plan-003)
- `AEQUITAS_FREE_TIER_THROTTLE` toggle resolved at `graph.py` (DIP),
  injected into Fisher/Macro/Marks module-level vars.
- `ThesisReportPayload` + 4 SOTA metrics.
- Quantitative Health panel: HTML adapter + CLI.
- `setup_env.sh` updated with throttle parameter.

## Scope Guard (Consolidated)
- `src/tools/` modified: `fundamental_metrics.py` (Phase 1), `historical_ingestion.py` (Phase 1).
- `src/agents/` modified: `graham.py` (Phase 2), `fisher.py`/`macro.py`/`marks.py` (Phase 3).
- `src/core/graph.py` modified: throttle injection (Phase 3 DIP fix).
- `scripts/setup_env.sh` modified: throttle parameter (Phase 3).
- No `.tf` or `.yml` files modified.

## Definition of Done
- [x] 265 tests passing, 0 regressions.
- [x] Milestone v3.0 DELIVERED.
