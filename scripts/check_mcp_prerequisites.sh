#!/bin/bash
# Aequitas-MAS: Prerequisite Validation Script (v5.2)

failure_count=0

echo "--- Environmental Validation: Aequitas-MAS ---"

# 1. Python Validation (Required: ^3.12)
echo -n "Python: "
if command -v python3 &> /dev/null; then
    PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
    if [[ $PYTHON_VER == 3.12* ]]; then
        echo "OK ($PYTHON_VER)"
    else
        echo "FAIL (Found $PYTHON_VER, required 3.12.x)"
        failure_count=$((failure_count + 1))
    fi
else
    echo "FAIL (python3 not found, required 3.12.x)"
    failure_count=$((failure_count + 1))
fi

# 2. Poetry Validation (Required: ^2.0)
echo -n "Poetry: "
if command -v poetry &> /dev/null; then
    POETRY_VER=$(poetry --version 2>&1 | awk '{print $3}' | tr -d ')')
    if [[ $POETRY_VER == 2.* ]]; then
        echo "OK ($POETRY_VER)"
    else
        echo "FAIL (Found $POETRY_VER, required ^2.0.0)"
        failure_count=$((failure_count + 1))
    fi
else
    echo "FAIL (poetry not found, required ^2.0.0)"
    failure_count=$((failure_count + 1))
fi

# 3. Node.js Validation (Required for MCP Server)
echo -n "Node.js: "
if command -v node &> /dev/null; then
    NODE_VER=$(node -v 2>&1)
    if [[ $NODE_VER == v* ]]; then
        echo "OK ($NODE_VER)"
    else
        echo "FAIL (Found $NODE_VER, required Node.js runtime)"
        failure_count=$((failure_count + 1))
    fi
else
    echo "FAIL (Not found. Required for 'npx @modelcontextprotocol/server-filesystem')"
    failure_count=$((failure_count + 1))
fi

# 4. Nix Manager (Optional but recommended)
echo -n "Nix Manager: "
if command -v nix &> /dev/null; then
    echo "OK ($(nix --version))"
else
    echo "WARNING (Not found. Nix is recommended for Isomorphism)"
fi

if [[ $failure_count -gt 0 ]]; then
    echo "Environment validation failed with $failure_count required prerequisite error(s)."
    exit 1
fi

echo "Environment validation passed."
