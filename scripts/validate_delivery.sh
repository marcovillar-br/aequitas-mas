#!/usr/bin/env bash

set -euo pipefail

RUN_LIVE_SMOKE=0

for arg in "$@"; do
    case "$arg" in
        --live-smoke)
            RUN_LIVE_SMOKE=1
            ;;
        --help|-h)
            echo "Usage: ./scripts/validate_delivery.sh [--live-smoke]"
            echo
            echo "Runs the mandatory pre-delivery validation gate:"
            echo "  1. poetry sync"
            echo "  2. poetry run ruff check src/ tests/"
            echo "  3. poetry run pytest tests/"
            echo "  4. focused boundary smoke tests"
            echo
            echo "Optional:"
            echo "  --live-smoke   Run 'poetry run python main.py' after the mandatory gate."
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Use --help for usage." >&2
            exit 1
            ;;
    esac
done

echo "==================================================="
echo "  Aequitas-MAS Pre-Delivery Validation"
echo "==================================================="

echo
echo "[0/5] Loading environment variables..."
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

echo
echo "[1/5] Synchronizing Poetry environment..."
poetry sync

echo
echo "[2/5] Running Ruff..."
poetry run ruff check src/ tests/

echo
echo "[3/5] Running full pytest suite..."
poetry run pytest tests/

echo
echo "[4/5] Running focused boundary smoke tests..."
poetry run pytest tests/test_graph_routing.py -k "agent_state_input_on_invoke or node_exceptions_record_error_span_and_degrade"

if [[ "$RUN_LIVE_SMOKE" -eq 1 ]]; then
    echo
    echo "[5/5] Running live application smoke test..."
    poetry run python main.py
fi

echo
echo "Pre-delivery validation completed successfully."
