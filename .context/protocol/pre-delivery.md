# SOP: Pre-Delivery Validation Protocol (PDV)
# Reference: Aequitas-MAS Cognitive Architecture

## 1. Objective
Prevent boundary mismatches, environment drift, and late-stage regressions before any code is delivered to the remote repository.

## 2. Mandatory Gate (Run Before Every Push)
The Developer persona MUST complete the following sequence in the local Poetry-managed environment:

1. **Environment Loading:** Load local environment variables before validation. The preferred mechanism is the shell function `load_env`, when available.
2. **Environment Synchronization:** `poetry sync`
3. **Linting & Quality:** `poetry run ruff check src/ tests/`
4. **Full Logic Validation:** `poetry run pytest tests/`
5. **Boundary Contract Smoke Validation:** Run focused tests that exercise the real application boundary contracts, especially when `src/core/graph.py`, `main.py`, `src/core/state.py`, or adapter wiring changed.

## 2.1 Environment Loading Rule
If `load_env` is defined in the developer shell profile, it MUST be executed before the validation gate.

Special case:
- when `load_env` lives inside `~/.bashrc`, the protocol implementation must account for the fact that many `.bashrc` files return early in non-interactive shells
- the automation layer may import the function from an interactive Bash session before executing it

This step ensures that optional smoke validation and any local runtime-dependent checks operate with the same environment contract used during normal development.

## 3. Boundary Validation Rules
When a wrapper, adapter, or entrypoint contract changes, the Developer MUST validate the real invocation modes used by the application.

Examples of mandatory contract checks:
- `app.invoke()` with dictionary-based input
- `app.invoke()` with `AgentState` input
- `app.stream()` with the production-style config payload
- controlled degradation paths after non-fatal node exceptions

The goal is to verify that the public execution boundary still behaves exactly as the application entrypoint expects.

## 4. Optional Live Smoke Validation
If all required runtime secrets are available and the feature being delivered touches the operational entrypoint, a live smoke test SHOULD be executed:

`poetry run python main.py`

This step is optional because it may depend on external APIs, cloud configuration, or quota-limited infrastructure. It MUST NOT replace the deterministic mandatory gate.

## 5. Delivery Gate
- **FAIL:** If any mandatory step fails, STOP immediately. Do not commit or push until the issue is resolved.
- **PASS:** If all mandatory steps pass, the Developer may proceed to `git add`, `git commit`, and `git push`.

## 6. Recommended Automation
The preferred local command for this protocol is:

`./scripts/validate_delivery.sh`

This script standardizes the validation flow and reduces the risk of skipping a required step before delivery.
