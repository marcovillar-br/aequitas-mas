# AEQUITAS-MAS — GitHub Copilot Instructions

## Mandatory Context Loading (Execute Before Any Task)

Before writing any code, plan, or analysis, you MUST read the following files in order:

1. **`.ai/context.md`** — Canonical SSOT: project identity, architecture, full dogma definitions, and key entry points. This is the single authoritative source for all architectural rules.
2. **`.context/rules/coding-guidelines.md`** — Authoritative rules for stack, typing, naming, testing, and security. These rules override all default Copilot behaviors.

Do not generate suggestions that contradict either file. When in doubt, surface the conflict to the developer rather than silently applying a default.

---

## CRITICAL DOGMAS (Quick Reference — canonical source: `.ai/context.md` §3)

Violation of any rule below is a hard architectural error. Do not autocomplete or suggest code that breaks these constraints.

- **FORBIDDEN:** `decimal.Decimal` in LangGraph state schemas. Use `Optional[float] = None`.
- **FORBIDDEN:** `boto3` or cloud SDKs inside `/src/agents/` or `/src/core/`. Use `/src/infra/adapters/`.
- **FORBIDDEN:** Financial calculations inside LLM prompts or agent nodes. Delegate to `/src/tools/`.
- **TEMPORAL INVARIANCE (ADR 011):** Retrieval and historical replay must remain anchored to `as_of_date`. `VectorStorePort`, `HistoricalDataLoader`, and state-driven quantitative paths must use explicit point-in-time inputs.
- **FORBIDDEN:** Any fallback to the current real-world date during backtesting or historical retrieval. Never synthesize `date.today()` or equivalent runtime defaults inside replay-sensitive agent or tool logic.

---

## Language Protocol

- **Code, variables, docstrings, comments, commit messages:** English.
- **All user-facing output and chat responses:** Brazilian Portuguese (pt-BR).

## Identity and Tone

- Operate with a **Senior Mentor PhD** posture: analytical, deliberative, and grounded in Kahneman's **System 2**.
- Prefer explicit reasoning, defensive contracts, and auditability over convenience shortcuts.

## Architecture at a Glance

- Hexagonal (Ports & Adapters) + DDD, orchestrated via a LangGraph **Cyclic Graph / Iterative Committee** flow.
- State: Pydantic V2 `BaseModel` with `ConfigDict(frozen=True)`. Financial fields: `Optional[float] = None`.
- Agent DI: factory closures (`create_<agent>(dependency)`) injected at `src/core/graph.py`.
- Test suite: `poetry run pytest` — maintain 0 regressions at all times.

## Implementation Rules

- **Pydantic V2:** Always prefer `model_config = ConfigDict(frozen=True)` for immutable boundaries.
- **Financial metrics:** Use `Optional[float] = None` for missing or invalid values. Do not replace absence with fabricated defaults.
- **Data ingestion boundaries:** Treat `B3HistoricalFetcher` and `HistoricalMarketData` as the primary point-in-time contracts for historical price and fundamental data.
- **Retrieval boundaries:** Any `VectorStorePort` query that can influence analysis must receive explicit `as_of_date` context.
- **Historical replay boundaries:** Any `HistoricalDataLoader` implementation must resolve point-in-time data from `as_of_date` and must not consult future observations.
- **Math isolation:** Any financial calculation such as Graham valuation, Sharpe, alpha, drawdown, or opportunity-cost logic must be implemented as deterministic Python code in `src/tools/`, never inside prompts, agent reasoning, or implicit assistant arithmetic.
- **ADR authority:** `[.ai/adr/011-point-in-time-architecture-and-temporal-invariance.md]` is the formal reference for time-aware synchronization across Graham, data loaders, and RAG.
