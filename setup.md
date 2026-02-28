# AEQUITAS-MAS: SETUP & ISOMORPHISM PROTOCOL (V5.0)

## 1. Architectural Philosophy & Isomorphism
The setup ignores traditional "loose scripts" approaches. The system is treated as a **Cyclic State Graph**. The transition to an Agnostic Workspace (v5.0) eliminates development environment variance, ensuring that the Auditing Agent (Marks) operates on the exact same binaries as the Quantitative Agent (Graham).

To mitigate **Semantic Entropy** in the LLM, the system implements an **Isomorphic Validation Layer**:
Let $S_t$ be the system state and $T$ be the deterministic calculation tool. The LLM output ($O$) is forced through a strict typing filter $P$ (Pydantic):
$$S_{t+1} = P(T(O))$$
This ensures that hallucination errors do not propagate into financial calculations, where precision must be absolute ($\epsilon = 0$).

## 2. System Prerequisites
To ensure the local environment is identical to production (Cloud-Native AWS), the following are mandatory:
* **WSL2 (Ubuntu 22.04+)**: Linux kernel isolation (if on Windows).
* **Nix Package Manager**: Declarative manager to ensure the Python interpreter and C libraries are binarily identical across machines.
* **Poetry (v2.0+)**: Deterministic dependency management and package graph conflict resolution.

## 3. Workspace Initialization (`dev.nix`)
The `dev.nix` file acts as the ultimate source of truth for the OS environment.
```nix
{ pkgs }: {
  channel = "stable-23.11";
  packages = [
    pkgs.python311
    pkgs.poetry
    pkgs.gcc
    pkgs.libffi
  ];
  env = {
    PYTHONPATH = "./src";
    LANG = "pt_BR.UTF-8";
  };
}

```

## 4. Dependency Contract (`pyproject.toml`)

Installation via Poetry locks critical versions to prevent graph logic breakage.

```bash
# Initialization and isolation configuration
poetry config virtualenvs.in-project true
poetry init --name aequitas-mas --python "^3.11"

# Core SOTA Dependencies
poetry add langgraph==0.0.15 pydantic>=2.0 langchain-anthropic
poetry add yfinance pandas numpy
poetry add --group dev pytest pytest-mock

```

## 5. Directory Structure (Hexagonal Architecture)

The project rigorously separates intelligence (Agents) from adapters (Tools/Infra).

* `src/core/`: State management and LangGraph definitions (`state.py`, `graph.py`).
* `src/agents/`: LLM Prompts and Personas logic (Graham, Fisher, Marks).
* `src/tools/`: Deterministic functions (Graham Calculations, B3 Scrapers).
* `src/infra/`: Persistence and Cloud adapters (SqliteSaver / DynamoDB).

## 6. State Contract Implementation (`src/core/state.py`)

This is the core of the **Risk Confinement**. The state is not text; it is a validated object.

```python
from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

class FinancialMetrics(BaseModel):
    ticker: str = Field(pattern=r"^[A-Z0-9]{5}$")
    vpa: float 
    lpa: float
    intrinsic_value: Optional[float] = None

class AgentState(TypedDict):
    messages: Annotated[List, add_messages]
    metrics: Optional[FinancialMetrics]
    compliance_approved: bool

```

## 7. Security & FinOps Protocol (Zero Trust)

* **API Keys**: Usage of `.env` files is strictly prohibited. Keys are injected via the IDE's Secret Manager (Google IDX) or runtime environment variables.
* **Recursion Limit**: Every LangGraph compilation MUST include `recursion_limit=15` to prevent infinite cost loops in case of agent divergence.

## 8. Validation Criteria (Definition of Done - DoD)

To validate the setup, execute the integrity test protocol:

```bash
# 1. Verify Python Isomorphism
poetry run python -c "import platform; print(platform.python_version())"

# 2. Test Quantitative Engine (Tools)
poetry run pytest tests/

```

## 9. Implementation Status Table (Sync: PME v5.0)

| Phase | Component | Status | Traceability |
| --- | --- | --- | --- |
| **1.1** | Agnostic Environment (Nix/Poetry) | ✅ Completed | ETD v5, Cap 3 |
| **1.2** | State Isomorphism (`state.py`) | ✅ Completed | DDE v4.2, Sec 1 |
| **1.3** | Quantitative Engine (Tools) | 🔄 In Progress | `src/tools/` |
| **2.1** | Graham-Fisher Orchestration | 📅 Scheduled | `src/agents/` |

