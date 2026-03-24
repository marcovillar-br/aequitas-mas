---
plan_id: plan-instrumentation-b3-fetcher-diagnostic-001
target_files:
  - "src/tools/b3_fetcher.py"
enforced_dogmas: [observability, type-safety]
validation_scale: FACTS (Mean: 5.0)
---

## 1. Intent & Scope
Implement diagnostic instrumentation in `src/tools/b3_fetcher.py` using `structlog` to gain deep visibility into the intraday fallback logic. The goal is to explicitly log the state, types, and values of date comparisons and cascade dictionary resolutions without altering the existing deterministic logic. All new logs must be emitted at the `INFO` level to ensure terminal visibility during development execution.

## 2. File Implementation

### Step 2.1: Instrument `_fetch_price_as_of` Date Evaluation
* **Target:** `src/tools/b3_fetcher.py`
* **Action:** Before executing the `as_of_date == date.today()` condition, inject a `logger.info` statement capturing the comparison context.
* **Constraints:** Must log the raw value of `as_of_date`, `type(as_of_date).__name__`, the raw value of `date.today()`, and the boolean result of the equality check.
* **Signatures:** N/A (Telemetry injection only).

### Step 2.2: Instrument `_fetch_intraday_price` Cascade Resolution
* **Target:** `src/tools/b3_fetcher.py`
* **Action:** Inject `logger.info` statements at the start and throughout the fallback cascade.
* **Constraints:** 
  - Log `list(info.keys())` to preview available provider data.
  - Log the resolved (or coerced) value for each fallback step (`currentPrice`, then `regularMarketPrice`, then `previousClose`) to visualize the exact point of early return or final degradation.
* **Signatures:** N/A (Telemetry injection only).

## 3. Definition of Done (DoD)
- [ ] `structlog` is imported and initialized at the module level in `b3_fetcher.py` if not already present.
- [ ] Date comparison types and values are explicitly logged at the `INFO` level.
- [ ] The `info` dictionary keys and the cascade candidate resolutions are logged at the `INFO` level.
- [ ] Code passes standard static analysis (`ruff check`).
- [ ] Zero logical modifications were made to the fallback rules themselves.