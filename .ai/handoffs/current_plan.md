---
plan_id: plan-sprint-9-phase-2-telemetry-presentation-001
target_files:
  - "src/tools/b3_fetcher.py"
  - "src/core/interfaces/audit_store.py"
  - "src/infra/adapters/opensearch_audit_adapter.py"
  - "src/core/interfaces/presentation.py"
  - "src/core/telemetry.py"
enforced_dogmas: [temporal-invariance, dependency-inversion, controlled-degradation]
validation_scale: FACTS (Mean: 5.0)
---

## 1. Intent & Scope
Design the architectural blueprint for Sprint 9 (Phase 2), focusing on enhancing data resilience and observability. The plan introduces a temporal-invariant intraday fallback for B3 fetching, formalizes the OpenSearch `AuditStorePort` to guarantee IoC, establishes the foundational Pydantic models for the downstream `PresentationAdapter` (Thesis-CoT), and implements strict Controlled Degradation for telemetry to protect the FastAPI gateway.

## 2. File Implementation

### Step 2.1: Implement Intraday Fallback in B3 Fetcher
* **Target:** `src/tools/b3_fetcher.py`
* **Action:** Update `_fetch_price_as_of` to include an intraday fallback. If the requested `as_of_date` is strictly equal to `date.today()` AND historical `Close` is missing/NaN, attempt to read `info.get("currentPrice")` or `info.get("regularMarketPrice")`.
* **Constraints:** Must strictly preserve Temporal Invariance. If `as_of_date < date.today()`, it MUST NOT fallback to the intraday price to avoid look-ahead bias. Must use `_coerce_optional_finite_float`.
* **Signatures:** `def _fetch_price_as_of(self, market_client: Any, as_of_date: date) -> Optional[float]: ...`

### Step 2.2: Design Audit Port and Enforce IoC
* **Target:** `src/core/interfaces/audit_store.py` (and adapter verification)
* **Action:** Formalize the `AuditStorePort` Protocol. Ensure that the `OpenSearchAuditAdapter` explicitly implements this interface and completely isolates all `opensearch-py` / `boto3` SDK logic inside `src/infra/adapters/`.
* **Constraints:** Zero cloud SDK imports in the `src/core/` and `src/agents/` layers. The graph state and routers must only depend on the abstract port.
* **Signatures:** `class AuditStorePort(Protocol): def record_event(self, event: BaseModel) -> None: ...`

### Step 2.3: Design Presentation Adapter Foundation (Thesis-CoT)
* **Target:** `src/core/interfaces/presentation.py`
* **Action:** Define the `ThesisReportPayload` Pydantic model (with `frozen=True`) and the `PresentationAdapter` protocol that will consume it to generate deterministic PDFs.
* **Constraints:** This establishes the boundary to prevent LLM visual hallucinations (e.g., ASCII charts, markdown tables). The LLM output MUST be a strict JSON payload mapped to `ThesisReportPayload`.
* **Signatures:** `class ThesisReportPayload(BaseModel): ...`; `class PresentationAdapter(Protocol): def render_report(self, payload: ThesisReportPayload) -> bytes: ...`

### Step 2.4: Establish Telemetry Controlled Degradation
* **Target:** `src/core/telemetry.py` and `src/infra/adapters/opensearch_audit_adapter.py`
* **Action:** Implement strict exception catching around OpenTelemetry payload shipping and OpenSearch audit indexing. Ensure that timeouts or network errors degrade silently (logging locally via `structlog` as warnings) without raising upstream HTTP 500s.
* **Constraints:** The `/analyze` and `/backtest/run` FastAPI endpoints must remain 100% resilient to telemetry pipeline failures.
* **Signatures:** Standard `try...except Exception` blocks around external network calls with proper fallback logging.

## 3. Definition of Done (DoD)
- [ ] Intraday fallback is implemented with strict `as_of_date == today` check, preserving Temporal Invariance.
- [ ] `AuditStorePort` and `PresentationAdapter` protocols are defined, fully abstracting concrete implementations.
- [ ] Telemetry and Audit Adapters fail gracefully without crashing graph execution or FastAPI routes.
- [ ] Code passes standard static analysis (`ruff check`).
- [ ] Tests verify that look-ahead fallback does NOT occur for past dates.
- [ ] Tests mock OpenSearch adapters and intentionally raise timeouts to verify the API gateway does not crash.