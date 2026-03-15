# SOP: Pre-Delivery Validation Protocol (PDV)
# Reference: Aequitas-MAS Cognitive Architecture

## 1. Objective
Prevent boundary mismatches, environment drift, and late-stage regressions before any code is delivered to the remote repository.

## 2. Mandatory Gate (Run Before Every Push)
The Developer persona MUST complete a validation gate before every push. The gate is now
risk-based and may run in one of three levels:

1. **Full Gate:** Mandatory for runtime-sensitive changes.
2. **Standard Gate:** Mandatory for tests, scripts, CI/CD, or Terraform changes.
3. **Light Gate:** Allowed for documentation-only or protocol-only changes.

The preferred entrypoint is:

`./scripts/validate_delivery.sh --mode auto`

`auto` is the default and MUST infer the minimum safe validation level from the changed
file set.

## 2.1 Environment Loading Rule
If `load_env` is defined in the developer shell profile, it MUST be executed before the validation gate.

Special case:
- when `load_env` lives inside `~/.bashrc`, the protocol implementation must account for the fact that many `.bashrc` files return early in non-interactive shells
- the automation layer may import the function from an interactive Bash session before executing it

This step ensures that optional smoke validation and any local runtime-dependent checks operate with the same environment contract used during normal development.

## 2.2 Gate Selection Rules

### Full Gate
Use the Full Gate when the change touches:
- `src/agents/`
- `src/core/`
- `src/tools/`
- `src/api/`
- `main.py`

The Full Gate includes:
1. `poetry sync`
2. `poetry run ruff check src/ tests/`
3. `poetry run pytest tests/`
4. focused boundary smoke validation
5. optional live smoke validation when explicitly requested

### Standard Gate
Use the Standard Gate when the change touches:
- `tests/`
- `scripts/`
- `infra/terraform/`
- `.github/workflows/`

The Standard Gate MUST run only the validations relevant to the changed area, for example:
- `bash -n` for changed shell scripts
- `terraform fmt -check -recursive infra/terraform` for Terraform changes
- `poetry run pytest tests/` when the test suite itself was modified

### Light Gate
Use the Light Gate when the change is restricted to documentation or protocol files such as:
- `.context/`
- `README.md`
- `setup.md`

The Light Gate is intentionally minimal and SHOULD avoid unnecessary runtime or test execution.

## 3. Boundary Validation Rules
When a wrapper, adapter, or entrypoint contract changes, the Developer MUST force the
Full Gate and validate the real invocation modes used by the application.

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

`./scripts/validate_delivery.sh --mode auto`

This script standardizes the validation flow and reduces the risk of skipping a required step before delivery.
