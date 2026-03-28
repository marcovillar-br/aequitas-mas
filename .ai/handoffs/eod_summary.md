---
summary_id: eod-sprint16-sota-factors-final
status: completed
target_files:
  - "src/tools/fundamental_metrics.py"
  - "src/core/state.py"
  - "src/core/interfaces/presentation.py"
  - "src/tools/backtesting/historical_ingestion.py"
  - "src/agents/graham.py"
  - "src/agents/fisher.py"
  - "src/agents/macro.py"
  - "src/agents/marks.py"
  - "src/infra/adapters/pdf_presentation_adapter.py"
  - "main.py"
  - "scripts/setup_env.sh"
  - ".ai/prompts/graham_agent_v2.md"
tests_run: ["265 passed, 0 failed, 0 regressions"]
dogmas_respected: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip, pydantic-v2-frozen]
---

## 1. Implementation Summary

Sprint 16 executed across 3 phases on branch `feature/sprint16-sota-factors`.

### Phase 1 — ROIC + DY Tools & Schema (plan-001)
- `calculate_roic` and `calculate_dividend_yield` in `fundamental_metrics.py`
  with full controlled degradation.
- `GrahamMetrics` + `HistoricalMarketData` schema expansion (v3.0).
- Auto-enrichment: consensus receives ROIC/DY via `model_dump()`.

### Phase 2 — Graham Wiring & CoT (plan-002)
- `_build_metrics_from_historical_data` maps roic/DY from historical data.
- `_build_interpreter_prompt` enriched with ROIC and DY lines.
- `GrahamInterpretation` expanded: `roic_assessment` + `dividend_yield_assessment`.
- `graham_agent_v2.md` CoT prompt: quality (ROIC >15%) + income (DY >0) guidance.

### Phase 3 — Tearsheet & Throttling (plan-003)
- `AEQUITAS_FREE_TIER_THROTTLE` toggle in Fisher/Macro/Marks (4 sleep calls).
- `ThesisReportPayload` + 4 SOTA metrics (piotroski, altman, roic, DY).
- Quantitative Health panel: HTML `<section class="quant-health">` + CLI
  `SAÚDE QUANTITATIVA`.
- `setup_env.sh` updated with throttle parameter.

## 2. Validation Performed

- `pytest`: 265 tests passed with 0 regressions (+15 total across 3 phases).
- `ruff check`: All checks passed.
- sdd-auditor: PASSED across all 3 phases.
- sdd-reviewer: PASSED across all 3 phases.

## 3. Sprint 16 — Consolidated Delivery

| Plan | Phase | Tests Added | Total |
| :--- | :--- | :---: | :---: |
| plan-sprint16-sota-factors-001 | ROIC + DY tools + schema | +7 | 257 |
| plan-sprint16-sota-factors-002 | Graham wiring + CoT | +5 | 262 |
| plan-sprint16-sota-factors-003 | Throttle + Tearsheet | +3 | 265 |

**Milestone v3.0 (SOTA Factor Expansion): DELIVERED**
