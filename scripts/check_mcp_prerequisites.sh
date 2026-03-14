#!/bin/bash
# Aequitas-MAS: Prerequisite Validation Script (v5.1)

echo "--- Environmental Validation: Aequitas-MAS ---"

# 1. Python Validation (Required: ^3.12)
PYTHON_VER=$(python3 --version 2>&1 | awk '{print $2}')
echo -n "Python: "
if [[ $PYTHON_VER == 3.12* ]]; then
    echo "OK ($PYTHON_VER)"
else
    echo "FAIL (Found $PYTHON_VER, required 3.12.x)"
fi

# 2. Poetry Validation (Required: ^2.0)
POETRY_VER=$(poetry --version 2>&1 | awk '{print $3}' | tr -d ')')
echo -n "Poetry: "
if [[ $POETRY_VER == 2.* ]]; then
    echo "OK ($POETRY_VER)"
else
    echo "FAIL (Found $POETRY_VER, required ^2.0.0)"
fi

# 3. Node.js Validation (Required for MCP Server)
NODE_VER=$(node -v 2>&1)
echo -n "Node.js: "
if [[ $NODE_VER == v* ]]; then
    echo "OK ($NODE_VER)"
else
    echo "FAIL (Not found. Required for 'npx @modelcontextprotocol/server-filesystem')"
fi

# 4. Nix Manager (Optional but recommended)
echo -n "Nix Manager: "
if command -v nix &> /dev/null; then
    echo "OK ($(nix --version))"
else
    echo "WARNING (Not found. Nix is recommended for Isomorphism)"
fi