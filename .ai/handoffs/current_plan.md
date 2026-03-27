---
plan_id: plan-sprint14-cli-observability-001
target_files:
  - "src/core/telemetry.py"
  - "tests/test_telemetry.py"
  - "src/infra/adapters/pdf_presentation_adapter.py"
  - "tests/infra/test_pdf_presentation_adapter.py"
  - ".context/current-sprint.md"
enforced_dogmas: [zero-math-policy, risk-confinement, controlled-degradation, tdd, dip]
validation_scale: "FACTS (Mean: 5.0)"
---

## 1. Intent & Scope

Quick observability improvements for the local CLI developer experience.
Two axes of work:

1. **structlog ConsoleRenderer for local:** The current `_configure_structlog`
   always uses `JSONRenderer`, which produces single-line JSON blobs in the
   terminal — unreadable for local development. When `ENVIRONMENT` is `local`
   (or unset), switch to `structlog.dev.ConsoleRenderer()` for colored,
   human-readable output. Keep `JSONRenderer` for cloud environments
   (`dev`, `hom`, `prod`, `ci`) where CloudWatch/OpenSearch ingestion
   requires structured JSON.

2. **Presentation Adapter enrichment:** The current `PdfPresentationAdapter`
   renders `thesis`, `evidence`, and `quantitative_data` — but lacks
   `as_of_date`, `current_market_price`, and a clear `APPROVED`/`REJECTED`
   status block. These fields are essential for the Tech Lead's CLI review
   and the PA defense report. Enrich `ThesisReportPayload` with 3 new
   `Optional` fields and update the HTML renderer to display them.

**SCOPE GUARD:**
- No agent files (`src/agents/`) modified.
- No graph file (`src/core/graph.py`) modified.
- No `.tf`, `.sh`, or `.yml` files modified.
- `ThesisReportPayload` enrichment is additive — existing fields untouched,
  new fields are `Optional` with defaults.

---

## 2. File Implementation

### Step 2.1 — structlog ConsoleRenderer for local environment (RED-GREEN-REFACTOR)

* **Target:** `src/core/telemetry.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action:**
  In `_configure_structlog()`, read `os.getenv("ENVIRONMENT", "local")` and
  select the renderer:
  - `local` or empty → `structlog.dev.ConsoleRenderer()`
  - anything else → `structlog.processors.JSONRenderer()`

  Add `import os` at the top (already used in `graph.py` but not in
  `telemetry.py`).

* **Test to add in `tests/test_telemetry.py`:**

**Test A — ConsoleRenderer selected for local environment**
```python
def test_configure_structlog_uses_console_renderer_for_local() -> None:
    """Local environment must use ConsoleRenderer for human-readable output."""
    # Patch ENVIRONMENT=local
    # Force reconfiguration
    # Assert structlog.configure was called with ConsoleRenderer as last processor
```

**Test B — JSONRenderer selected for cloud environment**
```python
def test_configure_structlog_uses_json_renderer_for_cloud() -> None:
    """Cloud environments must use JSONRenderer for structured ingestion."""
    # Patch ENVIRONMENT=dev
    # Force reconfiguration
    # Assert structlog.configure was called with JSONRenderer as last processor
```

* **Constraints:** The processor chain must preserve `merge_contextvars`,
  `add_log_level`, `TimeStamper`, and `_inject_trace_context` — only the
  final renderer changes.

---

### Step 2.2 — Enrich ThesisReportPayload and HTML renderer (RED-GREEN-REFACTOR)

* **Target:** `src/core/interfaces/presentation.py` and
  `src/infra/adapters/pdf_presentation_adapter.py`
* **Execution mode:** code-bearing — write failing tests first.

* **Action in `src/core/interfaces/presentation.py`:**
  Add 3 new Optional fields to `ThesisReportPayload`:
  ```python
  as_of_date: Optional[str] = Field(
      default=None,
      description="Point-in-time reference date (ISO-8601) for the analysis.",
  )
  current_market_price: Optional[float] = Field(
      default=None,
      description="Observed market price at the time of analysis.",
  )
  approval_status: Optional[str] = Field(
      default=None,
      description="Final committee verdict: APPROVED or REJECTED.",
  )
  ```

* **Action in `src/infra/adapters/pdf_presentation_adapter.py`:**
  In `render_html()`, add a header block before the thesis `<h1>` showing:
  - `as_of_date` (or "N/A" if None)
  - `current_market_price` (or "N/A" if None)
  - `approval_status` rendered as a colored badge
    (`APPROVED` = green, `REJECTED` = red, None = grey "PENDING")

* **Tests to add in `tests/infra/test_pdf_presentation_adapter.py`:**

**Test C — Report includes as_of_date and market price**
```python
def test_pdf_adapter_renders_as_of_date_and_price() -> None:
    """The report must display as_of_date and current_market_price."""
    # Build payload with as_of_date="2024-01-15" and price=35.50
    # Assert both values appear in rendered HTML
```

**Test D — Report shows approval status badge**
```python
def test_pdf_adapter_renders_approval_status_badge() -> None:
    """The report must display the committee approval status."""
    # Build payload with approval_status="APPROVED"
    # Assert "APPROVED" appears in rendered HTML
```

**Test E — Report degrades gracefully when new fields are None**
```python
def test_pdf_adapter_degrades_when_enrichment_fields_are_none() -> None:
    """Missing enrichment fields must degrade to N/A, not crash."""
    # Build payload with only thesis (no as_of_date, price, or status)
    # Assert HTML renders without error and shows "N/A"
```

* **Constraints:** Existing tests must not break — the 3 new fields are
  `Optional` with defaults, so existing `ThesisReportPayload()` calls
  remain valid.

---

### Step 2.3 — Update `current-sprint.md` (artifact-only)

* **Target:** `.context/current-sprint.md`
* **Action:** Prepend Sprint 14 section with status `IN PROGRESS` and
  planned steps matching Steps 2.1–2.2.

---

## 3. Definition of Done (DoD)

- [ ] `src/core/telemetry.py`: `ConsoleRenderer` for local, `JSONRenderer`
  for cloud.
- [ ] `tests/test_telemetry.py`: Tests A–B passing.
- [ ] `src/core/interfaces/presentation.py`: 3 new Optional fields on
  `ThesisReportPayload`.
- [ ] `src/infra/adapters/pdf_presentation_adapter.py`: Header block with
  `as_of_date`, `current_market_price`, and `approval_status`.
- [ ] `tests/infra/test_pdf_presentation_adapter.py`: Tests C–E passing.
- [ ] Full test suite: `poetry run pytest` passes with 0 regressions.
- [ ] `poetry run ruff check src/ tests/` passes cleanly.
- [ ] **HARD CONSTRAINT:** No agent, graph, `.tf`, `.sh`, or `.yml` files modified.
