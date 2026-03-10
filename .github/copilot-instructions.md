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

---

## Language Protocol

- **Code, variables, docstrings, comments, commit messages:** English.
- **All user-facing output and chat responses:** Brazilian Portuguese (pt-BR).

## Architecture at a Glance

- Hexagonal (Ports & Adapters) + DDD, orchestrated via LangGraph stateful DAGs.
- State: Pydantic V2 `BaseModel` with `ConfigDict(frozen=True)`. Financial fields: `Optional[float] = None`.
- Agent DI: factory closures (`create_<agent>(dependency)`) injected at `src/core/graph.py`.
- Test suite: `poetry run pytest` — maintain 0 regressions at all times.
