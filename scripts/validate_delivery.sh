#!/usr/bin/env bash

set -euo pipefail

MODE="auto"
RUN_LIVE_SMOKE=0

print_usage() {
    cat <<'EOF'
Usage: ./scripts/validate_delivery.sh [--mode auto|full|standard|light] [--live-smoke]

Modes:
  auto      Infer validation depth from changed files (default).
  full      Run the full delivery gate for runtime-sensitive changes.
  standard  Run targeted validation for tests, scripts, CI, or Terraform changes.
  light     Run documentation-only validation.

Optional:
  --live-smoke   Run 'poetry run python main.py' after the full gate.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            shift
            if [[ $# -eq 0 ]]; then
                echo "ERROR: --mode requires an argument." >&2
                exit 1
            fi
            MODE="$1"
            ;;
        --live-smoke)
            RUN_LIVE_SMOKE=1
            ;;
        --help|-h)
            print_usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            print_usage >&2
            exit 1
            ;;
    esac
    shift
done

if [[ ! "$MODE" =~ ^(auto|full|standard|light)$ ]]; then
    echo "ERROR: invalid mode '$MODE'." >&2
    print_usage >&2
    exit 1
fi

echo "==================================================="
echo "  Aequitas-MAS Pre-Delivery Validation"
echo "==================================================="

echo
echo "[0] Loading environment variables..."
if [[ -f "$HOME/.bashrc" ]]; then
    # shellcheck disable=SC1090
    source "$HOME/.bashrc"
fi

if ! declare -F load_env >/dev/null 2>&1; then
    LOAD_ENV_DEFINITION="$(bash -ic 'declare -pf load_env' 2>/dev/null || true)"
    if [[ -n "$LOAD_ENV_DEFINITION" ]]; then
        eval "$LOAD_ENV_DEFINITION"
    fi
fi

if declare -F load_env >/dev/null 2>&1; then
    load_env
else
    echo "WARNING: load_env function is not available in the current shell."
fi

collect_changed_files() {
    local tmp_file
    tmp_file="$(mktemp)"

    git diff --name-only --cached >>"$tmp_file" || true
    git diff --name-only >>"$tmp_file" || true
    git ls-files --others --exclude-standard >>"$tmp_file" || true

    if [[ ! -s "$tmp_file" ]]; then
        if git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}' >/dev/null 2>&1; then
            git diff --name-only '@{upstream}...HEAD' >>"$tmp_file" || true
        elif git rev-parse --verify HEAD~1 >/dev/null 2>&1; then
            git diff --name-only HEAD~1..HEAD >>"$tmp_file" || true
        fi
    fi

    mapfile -t CHANGED_FILES < <(sed '/^$/d' "$tmp_file" | sort -u)
    rm -f "$tmp_file"
}

is_full_path() {
    local path="$1"
    [[ "$path" =~ ^(src/agents/|src/core/|src/tools/|src/api/|main\.py$|pyproject\.toml$|poetry\.lock$) ]]
}

is_standard_path() {
    local path="$1"
    [[ "$path" =~ ^(tests/|scripts/|infra/terraform/|\.github/workflows/) ]]
}

is_light_path() {
    local path="$1"
    [[ "$path" =~ ^(docs/official/|\.ai/adr/|\.ai/handoffs/|\.ai/skills/|\.context/|README\.md$|setup\.md$|CLAUDE\.md$|\.ai/aidd-[^/]+\.md$) ]]
}

is_known_path() {
    local path="$1"
    is_full_path "$path" || is_standard_path "$path" || is_light_path "$path"
}

infer_mode() {
    local path
    local all_light=1

    if [[ "$MODE" != "auto" ]]; then
        EFFECTIVE_MODE="$MODE"
        return
    fi

    if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
        EFFECTIVE_MODE="light"
        return
    fi

    for path in "${CHANGED_FILES[@]}"; do
        if is_full_path "$path"; then
            EFFECTIVE_MODE="full"
            return
        fi
    done

    for path in "${CHANGED_FILES[@]}"; do
        if is_standard_path "$path"; then
            EFFECTIVE_MODE="standard"
            return
        fi
    done

    for path in "${CHANGED_FILES[@]}"; do
        if ! is_light_path "$path"; then
            all_light=0
        fi

        if ! is_known_path "$path"; then
            EFFECTIVE_MODE="standard"
            return
        fi
    done

    if [[ "$all_light" -eq 1 ]]; then
        EFFECTIVE_MODE="light"
        return
    fi

    EFFECTIVE_MODE="standard"
}

print_changed_files() {
    if [[ ${#CHANGED_FILES[@]} -eq 0 ]]; then
        echo "Changed files: none detected (falling back to branch diff heuristics)."
        return
    fi

    echo "Changed files:"
    printf '  - %s\n' "${CHANGED_FILES[@]}"
}

run_full_gate() {
    echo
    echo "[1] Synchronizing Poetry environment..."
    poetry sync

    echo
    echo "[2] Running Ruff..."
    poetry run ruff check src/ tests/

    echo
    echo "[3] Running full pytest suite..."
    poetry run pytest tests/

    echo
    echo "[4] Running focused boundary smoke tests..."
    poetry run pytest tests/test_graph_routing.py -k "agent_state_input_on_invoke or node_exceptions_record_error_span_and_degrade"

    if [[ "$RUN_LIVE_SMOKE" -eq 1 ]]; then
        echo
        echo "[5] Running live application smoke test..."
        poetry run python main.py
    fi
}

run_standard_gate() {
    local path
    local -a shell_files=()
    local run_pytest=0
    local run_terraform_fmt=0
    local run_self_smoke=0

    echo
    echo "[1] Synchronizing Poetry environment..."
    poetry sync

    for path in "${CHANGED_FILES[@]}"; do
        if [[ "$path" =~ ^tests/ ]]; then
            run_pytest=1
        fi
        if [[ "$path" =~ ^infra/terraform/.*\.tf$ ]]; then
            run_terraform_fmt=1
        fi
        if [[ "$path" =~ ^scripts/.*\.sh$ ]]; then
            shell_files+=("$path")
        fi
        if [[ "$path" == "scripts/validate_delivery.sh" ]]; then
            run_self_smoke=1
        fi
    done

    if [[ ${#shell_files[@]} -gt 0 ]]; then
        echo
        echo "[2] Validating shell scripts..."
        for path in "${shell_files[@]}"; do
            bash -n "$path"
        done
    fi

    if [[ "$run_terraform_fmt" -eq 1 ]]; then
        echo
        echo "[3] Checking Terraform formatting..."
        terraform fmt -check -recursive infra/terraform
    fi

    if [[ "$run_self_smoke" -eq 1 ]]; then
        echo
        echo "[4] Running validate_delivery self-smoke..."
        ./scripts/validate_delivery.sh --help
        ./scripts/validate_delivery.sh --mode light
    fi

    if [[ "$run_pytest" -eq 1 ]]; then
        echo
        echo "[5] Running test suite because tests changed..."
        poetry run pytest tests/
    fi

    if [[ ${#shell_files[@]} -eq 0 && "$run_terraform_fmt" -eq 0 && "$run_pytest" -eq 0 && "$run_self_smoke" -eq 0 ]]; then
        echo
        echo "[2] No additional standard checks were required for the detected file set."
    fi
}

run_light_gate() {
    echo
    echo "[1] Running documentation diff hygiene check..."
    git diff --check

    echo
    echo "[2] No runtime-sensitive files detected. Full gate skipped."
}

collect_changed_files
infer_mode

echo
echo "Validation mode: $EFFECTIVE_MODE"
print_changed_files

case "$EFFECTIVE_MODE" in
    full)
        run_full_gate
        ;;
    standard)
        run_standard_gate
        ;;
    light)
        run_light_gate
        ;;
esac

echo
echo "Pre-delivery validation completed successfully."
